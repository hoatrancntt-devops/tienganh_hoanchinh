"""TaskSpec: mỗi task khai báo tier, hạn mức token, cache, fallback. Router chỉ biết tier."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TaskSpec:
    name: str
    tier: str                 # T1 | T2
    max_output_tokens: int
    temperature: float
    cacheable: bool
    cache_scope: str          # global | lesson | user
    prompt_version: str       # đổi version = vô hiệu cache cũ
    degradable: bool          # T2 có hạ xuống T1 được không
    system_vi: str


EXPLAIN = TaskSpec(
    name="explain", tier="T1", max_output_tokens=350, temperature=0.3,
    cacheable=True, cache_scope="lesson", prompt_version="explain@1", degradable=True,
    system_vi=(
        "Bạn là giáo viên tiếng Anh cho người Việt đi làm bị mất gốc. "
        "Trả lời HOÀN TOÀN bằng tiếng Việt đời thường, tối đa 150 từ. "
        "Không dùng thuật ngữ ngữ pháp hàn lâm: nói 'chuyện đã xảy ra nhưng còn dính tới bây giờ' "
        "thay vì 'thì hiện tại hoàn thành'. Luôn cho một ví dụ dùng được ở công sở. "
        "Nếu câu hỏi không liên quan tiếng Anh, từ chối ngắn gọn và mời hỏi lại."
    ),
)

SENTENCE_REPAIR = TaskSpec(
    name="sentence_repair", tier="T1", max_output_tokens=250, temperature=0.2,
    cacheable=True, cache_scope="lesson", prompt_version="repair@1", degradable=True,
    system_vi=(
        "Học viên người Việt vừa nói một câu tiếng Anh. Chỉ ra ĐÚNG MỘT lỗi quan trọng nhất, "
        "giải thích bằng tiếng Việt trong 2 câu, rồi đưa câu đúng. Không liệt kê mọi lỗi — "
        "sửa hết một lượt làm người học nản. Tối đa 80 từ."
    ),
)

OPEN_FEEDBACK = TaskSpec(
    name="open_feedback", tier="T1", max_output_tokens=250, temperature=0.3,
    cacheable=False, cache_scope="user", prompt_version="feedback@1", degradable=True,
    system_vi=(
        "Chấm câu trả lời tự do của học viên ở trục GIAO TIẾP: họ có đáp ứng đúng câu hỏi không, "
        "người nghe có hiểu không. KHÔNG chấm phát âm (hệ thống khác đã làm). "
        "Trả lời bằng tiếng Việt, khen trước, sửa sau, tối đa 60 từ."
    ),
)

ROLEPLAY = TaskSpec(
    name="roleplay", tier="T2", max_output_tokens=200, temperature=0.7,
    cacheable=False, cache_scope="user", prompt_version="roleplay@1", degradable=True,
    system_vi=(
        "Bạn đóng vai đồng nghiệp người bản xứ trong tình huống công sở. "
        "Nói tiếng Anh ĐƠN GIẢN, câu ngắn, tốc độ chậm, đúng trình độ A1-A2. "
        "Mỗi lượt tối đa 2 câu. Nếu học viên bí, gợi ý bằng tiếng Việt trong ngoặc. "
        "Bám kịch bản được cung cấp, không lạc đề."
    ),
)

ADMIN_AUTHORING = TaskSpec(
    name="admin_authoring", tier="T2", max_output_tokens=800, temperature=0.6,
    cacheable=False, cache_scope="global", prompt_version="authoring@1", degradable=False,
    system_vi=(
        "Bạn hỗ trợ biên soạn nội dung dạy tiếng Anh cho người Việt đi làm. "
        "Sinh nội dung MỚI HOÀN TOÀN, không trích tài liệu có bản quyền. "
        "Câu tiếng Anh phải dùng được ở công sở hoặc đời thường Việt Nam. "
        "Trả về JSON đúng schema được yêu cầu."
    ),
)

REGISTRY: dict[str, TaskSpec] = {
    t.name: t for t in (EXPLAIN, SENTENCE_REPAIR, OPEN_FEEDBACK, ROLEPLAY, ADMIN_AUTHORING)
}
