# Bốn kỹ năng và thang Level

**Trạng thái:** Draft — chờ duyệt
**Ngày:** 2026-07-21
**Căn cứ:** `plans/reports/assessment-and-level-audit-260721-1114-placement-scoring-four-skills-level-ladder-report.md`

## Mục tiêu

Đưa app từ "dạy nghe–nói, đo 3 trục, 4 hệ phân cấp lệch nhau" sang "dạy đủ nghe–nói–đọc–viết, đo 4 trục,
một thang level duy nhất bám KNLNN 6 bậc" — cho đối tượng **mất gốc hoàn toàn**.

## Quyết định đã chốt (2026-07-21)

| Quyết định | Chọn | Hệ quả |
|---|---|---|
| Đối tượng | **Mất gốc hoàn toàn** | Nền hiện quá mỏng (14 bài trước 48 bài A2/B1) → phải viết thêm bài |
| Kỹ năng Viết | **Đủ 4 kỹ năng mọi bài** | Sửa cả 62 file YAML + schema + UI + đề xếp lớp |
| Kiểu xếp lớp | **Một band chung + biểu đồ 4 trục** | `ENTRY_LESSON` giữ một điểm vào; kết quả hiện 4 trục |
| Thang level | **4 bậc: Pre-A1 → A1 → A2 → B1** | Khớp `cefr_target` sẵn có, thêm band B1 vào bài test |

## Nguyên tắc kiến trúc chốt ở plan này

**Level là trục dọc tuần tự. Phase là nhãn chủ đề.** Đây là cách gỡ mâu thuẫn "4 hệ phân cấp":
hiện `phase` vừa đóng vai giai đoạn tuần tự (trên UI) vừa đóng vai track song song (trong DAG), nên
học viên hiểu sai thứ tự. Sau plan này, `level` quyết định thứ tự học, `phase` chỉ nói bài đó về chủ đề gì.

## Các phase

| # | Phase | Khối | Phụ thuộc | File |
|---|---|---|---|---|
| 01 | Thang level và tuyên bố đầu ra | C | — | [phase-01](phase-01-thang-level-va-tuyen-bo-dau-ra.md) |
| 02 | Sửa 8 lỗi chấm điểm xếp lớp | A | — | [phase-02](phase-02-sua-cham-diem-xep-lop.md) |
| 03 | Schema Đọc và Viết | B | 01 | [phase-03](phase-03-schema-doc-va-viet.md) |
| 04 | Chấm điểm Viết bằng luật (không AI) | B | 03 | [phase-04](phase-04-cham-diem-viet-bang-luat.md) |
| 05 | Đề xếp lớp 4 kỹ năng | A+B | 01, 02, 03, 04 | [phase-05](phase-05-de-xep-lop-bon-ky-nang.md) |
| 06 | Chuyển đổi 62 bài sang 4 kỹ năng | B | 03, 04 | [phase-06](phase-06-chuyen-doi-62-bai.md) |
| 07 | Dày nền cho người mất gốc | C | 01, 06 | [phase-07](phase-07-day-nen-mat-goc.md) |
| 08 | Kiểm tra kết thúc level + lộ trình động | C | 01, 06 | [phase-08](phase-08-kiem-tra-ket-thuc-level.md) |

### Thứ tự chạy đề xuất

```
01 ─┬─────────────────► 03 ──► 04 ──┬──► 06 ──┬──► 07
    │                      │        │         └──► 08
02 ─┴──────────────────────┴────────┴──► 05
```

Phase 01 và 02 độc lập nhau, chạy song song được. **Phase 02 nên làm trước tiên** — nó sửa lỗi đang gây
xếp sai 2 bậc cho học viên đang dùng thật, và không phụ thuộc quyết định nào.

## Cân đối khối lượng

Phase 06 và 07 là phần soạn nội dung, chiếm phần lớn công sức:

| Phase | Khối lượng | Loại việc |
|---|---|---|
| 01, 02, 03, 04, 05, 08 | ~6 file code + 3 file docs | Kỹ thuật, ước lượng được |
| 06 | 62 file YAML × (1 bài đọc + 1 bài viết) | **Soạn nội dung, làm theo đợt** |
| 07 | ~12 bài học mới | **Soạn nội dung, làm theo đợt** |

Phase 06 và 07 phải chia đợt theo level, không làm một lần. Chi tiết trong từng phase file.

## Tiêu chí nghiệm thu toàn plan

1. `make validate` xanh với luật mới cho `reading_passage` và `writing_task`.
2. Bài xếp lớp trả về **4 trục điểm** (Nghe/Nói/Đọc/Viết) + một band trong `{pre_a1, a1, a2, b1}`.
3. Không ca đầu vào nào làm tụt quá **1 bậc** so với band tính từ điểm gốc — có test phủ 6 ca ở phase 02.
4. Học viên trả lời đúng 100% và nói tốt **đạt được B1** (hiện trần là 86.8 → luôn ra A2).
5. Mỗi level có: danh sách bài cố định, số tuần ước tính, và tuyên bố đầu ra 4 kỹ năng bằng tiếng Việt.
6. Mọi bài học có hoạt động sinh điểm cho cả 4 kỹ năng; `mastery_weights` cộng đúng 1.0 và có mặt
   `read` + `write`.
7. `docs/khung-level.md` tồn tại, đối chiếu được với KNLNN 6 bậc (Thông tư 01/2014/TT-BGDĐT).

## Rủi ro

| Rủi ro | Ảnh hưởng | Giảm thiểu |
|---|---|---|
| Bài học phình quá 12 phút khi thêm Đọc+Viết | Vi phạm cổng validate; học viên bỏ giữa bài | Quyết định ở phase 03 (mục "Xung đột thời lượng") |
| Đề xếp lớp dài từ 14 lên >20 phút | Bỏ ngang ngay bước đầu | Cắt bớt vocab/grammar để bù, chi tiết ở phase 05 |
| Chấm Viết bằng luật quá khắt khe | Học viên viết đúng vẫn bị chấm sai | Chấm theo tầng, có điểm từng phần; chi tiết ở phase 04 |
| Phase 06 + 07 quá lớn, bỏ dở giữa chừng | Nội dung nửa vời, một số bài có Viết một số không | Làm trọn theo level, không trọn theo kỹ năng |

## Câu hỏi chưa giải quyết

1. Bài học nên dài bao nhiêu phút sau khi thêm Đọc + Viết? (quyết định ở phase 03, có đề xuất sẵn)
2. Ngưỡng mastery hiện **giảm dần** khi bài khó lên (foundation 78–80 → reading 70) — là chủ ý hay
   trôi dạt? Tồn đọng từ audit 2026-07-20, chưa được trả lời.
3. Ngưỡng phát âm ≥78 khắt khe hơn chuẩn CEFR ở bậc A1–A2 (CV2020 tr.135 nói lỗi phát âm có hệ thống
   là chấp nhận được tới A2). Với người mất gốc, đây có thể là chỗ bỏ cuộc. Giữ hay hạ?
