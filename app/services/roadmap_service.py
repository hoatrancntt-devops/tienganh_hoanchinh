"""Ước lượng thời gian còn lại của lộ trình, tính từ dữ liệu thật thay vì hằng số.

Bản cũ trả về một hằng số theo band (`{Pre-A1: 16, A1: 12, A2: 8, B1: 5}` tuần). Hai học viên
cùng band nhưng một người học 30 phút/ngày và một người học 10 phút/ngày nhận cùng một con số,
và con số đó không đổi dù họ đã học được nửa lộ trình.
"""
import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Lesson
from app.models.enums import ContentStatus, LessonState
from app.models.progress import ItemAttempt, LessonProgress
from app.models.user import UserProfile

# Trước khi có đủ dữ liệu, dùng mục tiêu học viên tự đặt ở onboarding. Sau đó dùng tốc độ thật:
# người đặt mục tiêu 30 phút/ngày mà học 10 phút thì con số dựa trên mục tiêu là lời nói dối
# tử tế, và nó sẽ vỡ đúng lúc học viên bắt đầu tin vào nó.
NGAY_TOI_THIEU_DE_TIN_TOC_DO = 7
BAI_TOI_THIEU_DE_TIN_TOC_DO = 3
NGAY_HOC_MOI_TUAN = 5          # giả định thực tế: nghỉ cuối tuần
BIEN_DO = 0.25                 # hiện khoảng, không hiện một con số giả vờ chính xác


@dataclass
class UocLuong:
    tuan_toi_thieu: int
    tuan_toi_da: int
    bai_con_lai: int
    theo_toc_do_that: bool

    @property
    def mo_ta_vi(self) -> str:
        if self.bai_con_lai == 0:
            return "Bạn đã hoàn thành toàn bộ lộ trình."
        can_cu = ("dựa trên tốc độ học thật của bạn" if self.theo_toc_do_that
                  else "dựa trên mục tiêu bạn đặt — sẽ chính xác hơn sau một tuần học")
        if self.tuan_toi_thieu == self.tuan_toi_da:
            return f"Còn khoảng {self.tuan_toi_thieu} tuần ({can_cu})."
        return f"Còn khoảng {self.tuan_toi_thieu}–{self.tuan_toi_da} tuần ({can_cu})."


def uoc_luong(
    bai_con_lai: int,
    phut_moi_bai: float,
    phut_moi_ngay_muc_tieu: int,
    phut_da_hoc: float = 0.0,
    so_ngay_da_hoc: int = 0,
    bai_da_xong: int = 0,
) -> UocLuong:
    """Ước lượng số tuần còn lại.

    Dùng tốc độ THẬT khi đã đủ dữ liệu; trước đó dùng mục tiêu tự đặt. Trả về một khoảng,
    không phải một con số — ước lượng chính xác tới từng tuần là thứ không ai làm được.
    """
    if bai_con_lai <= 0:
        return UocLuong(0, 0, 0, so_ngay_da_hoc >= NGAY_TOI_THIEU_DE_TIN_TOC_DO)

    du_du_lieu = (
        so_ngay_da_hoc >= NGAY_TOI_THIEU_DE_TIN_TOC_DO
        and bai_da_xong >= BAI_TOI_THIEU_DE_TIN_TOC_DO
        and phut_da_hoc > 0
    )
    if du_du_lieu:
        phut_moi_ngay = phut_da_hoc / so_ngay_da_hoc
    else:
        phut_moi_ngay = float(phut_moi_ngay_muc_tieu)
    phut_moi_ngay = max(1.0, phut_moi_ngay)

    tong_phut = bai_con_lai * max(1.0, phut_moi_bai)
    tuan = tong_phut / (phut_moi_ngay * NGAY_HOC_MOI_TUAN)
    return UocLuong(
        tuan_toi_thieu=max(1, round(tuan * (1 - BIEN_DO))),
        tuan_toi_da=max(1, round(tuan * (1 + BIEN_DO))),
        bai_con_lai=bai_con_lai,
        theo_toc_do_that=du_du_lieu,
    )


async def cho_hoc_vien(db: AsyncSession, user_id: uuid.UUID) -> UocLuong:
    """Ước lượng cho một học viên cụ thể, từ tiến độ và nhịp học thật của họ."""
    xong = {
        row[0]
        for row in await db.execute(
            select(LessonProgress.lesson_id).where(
                LessonProgress.user_id == user_id,
                LessonProgress.state == LessonState.MASTERED,
            )
        )
    }
    bai = (
        await db.execute(
            select(Lesson.id, Lesson.est_minutes).where(Lesson.status == ContentStatus.PUBLISHED)
        )
    ).all()
    con_lai = [m for lid, m in bai if lid not in xong]
    phut_moi_bai = (sum(m for _, m in bai) / len(bai)) if bai else 10.0

    # Nhịp học thật: bao nhiêu NGÀY KHÁC NHAU đã học, và tổng thời lượng các bài đã xong.
    so_ngay = (
        await db.execute(
            select(func.count(func.distinct(func.date(ItemAttempt.created_at)))).where(
                ItemAttempt.user_id == user_id, ItemAttempt.is_preview.is_(False)
            )
        )
    ).scalar() or 0
    phut_da_hoc = sum(m for lid, m in bai if lid in xong)

    profile = (
        await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    ).scalar_one_or_none()
    muc_tieu = profile.daily_goal_minutes if profile else 10

    return uoc_luong(
        bai_con_lai=len(con_lai),
        phut_moi_bai=phut_moi_bai,
        phut_moi_ngay_muc_tieu=muc_tieu,
        phut_da_hoc=phut_da_hoc,
        so_ngay_da_hoc=so_ngay,
        bai_da_xong=len(xong),
    )
