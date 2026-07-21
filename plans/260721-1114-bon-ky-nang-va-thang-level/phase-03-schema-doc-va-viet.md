# Phase 03 — Schema Đọc và Viết

**Phụ thuộc:** phase 01. **Chặn:** phase 04, 06.
**Loại việc:** code — schema, model, mastery, validate, UI.

## Vấn đề đang giải

62/62 bài dùng **chung một schema**: `vocabulary`, `sentence_patterns`, `dialogue`, `listening_snippet`,
`speaking_drills`, `mini_quiz`. Không có trường nào cho bài đọc, không có trường nào cho bài viết.

Hệ quả cụ thể ở phase `reading`: R01 "Đọc email nội bộ" nhét email vào cấu trúc `dialogue` có `speaker`
(`seeds/content/reading/R01.yaml:58-69`), sinh audio bằng Piper, kèm thêm `listening_snippet`. Học viên
**nghe** email đó. `learning_path_service.py:35` khai `Phase.READING: ["read", "listen"]` nhưng không có
hoạt động nào sinh điểm `read` — 11 file reading đặt `mastery_weights: {quiz: 0.7, listen: 0.3}`, tức
điểm "đọc" thực chất là điểm quiz trắc nghiệm tiếng Việt.

Viết thì bằng 0 ở mọi tầng: `ActivityKind` không có `WRITE`, schema không có, UI không có ô nhập text.

## QUYẾT ĐỊNH CẦN CHỐT TRƯỚC KHI CODE — xung đột thời lượng

`app/seeds/schema.py:138` đặt `est_minutes: int = Field(default=10, ge=3, le=12)`. Cổng validate chặn
bài dài quá 12 phút, với lý do ghi trong code: *"bài dài là bài không được học"*.

Một bài hiện đã gồm: từ vựng + hội thoại + nghe + drill nói + quiz ≈ 10 phút. Thêm bài đọc và bài viết
vào **mọi bài** thì không thể giữ 12 phút.

Ba lối ra:

| Cách | Nội dung | Đánh đổi |
|---|---|---|
| **A. Micro-task + nới trần lên 16** | Đọc ~2 phút (80–120 từ), Viết ~3 phút (1 bài tập ngắn) | Bài dài thêm 60%; đơn giản nhất về kỹ thuật |
| B. Tách 2 khối trong player | Cùng một bài nhưng chia "Khối nghe–nói" / "Khối đọc–viết", làm được 2 lần ngồi | Giữ được cảm giác bài ngắn; phải sửa player và cách tính tiến độ |
| C. Xen kẽ | Bài lẻ có Đọc, bài chẵn có Viết | Bài vẫn ngắn nhưng **vi phạm quyết định "đủ 4 kỹ năng mọi bài"** |

**Đề xuất: A + B.** Nới trần `est_minutes` lên 16, đồng thời chia player thành hai khối để học viên
dừng giữa chừng được. C mâu thuẫn với quyết định đã chốt nên loại.

Chốt xong mới code — quyết định này quyết định luôn hình dạng của phase 06.

## Việc phải làm

### 1. `ActivityKind` thêm `WRITE`

`app/models/enums.py:39` hiện có `LISTEN, SHADOW, SPEAK, VOCAB, READ, QUIZ`. Thêm `WRITE = "write"`.
`READ` đã tồn tại nhưng chưa hoạt động nào sinh ra — phase này làm nó có thật.

### 2. Trường `reading_passage` — tách khỏi `dialogue`

Đặc trưng bắt buộc, phân biệt với `dialogue`:

- Văn bản **liền mạch**, không chia `speaker` turns
- **Không sinh audio** — đây là điểm phân biệt cốt lõi với `listening_snippet`. Bài đọc mà nghe được thì
  không còn là bài đọc.
- Câu hỏi đọc hiểu **bằng tiếng Anh** (hiện quiz đọc hiểu viết bằng tiếng Việt → đang đo hiểu tiếng Việt)
- Có bản dịch tiếng Việt **ẩn**, chỉ mở sau khi trả lời — không hiện song song như `dialogue`
- Trường `word_count` và loại văn bản (`email`, `ticket`, `chat`, `doc`, `announcement`)

Loại câu hỏi cần có, tối thiểu 2 loại khác nhau mỗi bài: tìm thông tin cụ thể (scan), ý chính (skim),
đoán nghĩa từ ngữ cảnh, suy luận.

### 3. Trường `writing_task`

Bốn dạng, chấm được bằng luật (chi tiết thuật toán ở phase 04):

| Dạng | Mô tả | Vì sao chấm được bằng luật |
|---|---|---|
| `fill_blank` | Điền từ vào chỗ trống trong email | So khớp tập đáp án chấp nhận được |
| `reorder` | Sắp xếp câu thành đoạn đúng thứ tự | So sánh hoán vị |
| `error_correction` | Sửa lỗi trong câu cho sẵn | So khớp câu đích + biến thể |
| `guided_email` | Viết email theo khung cho sẵn | Từ khoá bắt buộc + cấu trúc + kiểm tra cơ học |

`guided_email` là dạng duy nhất có đầu ra tự do. Nó phải cung cấp: khung (mở/thân/kết), danh sách cụm
bắt buộc, độ dài tối thiểu, và `common_mistakes` riêng để sinh phản hồi tiếng Việt.

### 4. `mastery_weights` — bổ sung `read` và `write`

Mặc định hiện tại `{speak: 0.5, quiz: 0.3, listen: 0.2}` (`app/seeds/schema.py:113`) không có chỗ cho
đọc/viết. Đề xuất mặc định mới:

```yaml
{speak: 0.30, listen: 0.20, read: 0.15, write: 0.15, quiz: 0.20}
```

Vẫn giữ trọng số nói cao nhất — đó là mục tiêu sản phẩm. Từng phase được lệch khỏi mặc định (foundation
nặng `speak`, reading nặng `read`), nhưng **mọi bài phải có đủ 5 khoá** để không kỹ năng nào bị bỏ trống.

`compute_mastery_raw` (`app/services/prerequisite_service.py:46`) đã chia cho tổng trọng số thực tế nên
không cần sửa logic — chỉ cần dữ liệu vào có đủ khoá.

### 5. `skills_for_phase` — bỏ hoặc sửa

`learning_path_service.py:31-36` khai skill theo phase. Sau khi mọi bài có đủ 4 kỹ năng, bảng này hoặc
thành thừa, hoặc chuyển thành "kỹ năng **trọng tâm** của phase" dùng cho hiển thị. Chốt khi code.

### 6. Cổng validate — luật mới

Thêm vào `app/seeds/validate_content.py`:

- Mọi bài phải có `reading_passage` và `writing_task` (sau phase 06; trong lúc chuyển đổi thì cảnh báo)
- `reading_passage` **không được** có trường sinh audio
- Câu hỏi đọc hiểu phải bằng tiếng Anh (kiểm tra cơ học: tỉ lệ ký tự có dấu tiếng Việt)
- `mastery_weights` phải có đủ 5 khoá và cộng đúng 1.0
- `writing_task` dạng `guided_email` phải có ≥3 cụm bắt buộc và ≥2 `common_mistakes`
- Nới trần `est_minutes` theo quyết định ở đầu file

### 7. UI

- Màn đọc: văn bản liền, **không có nút play**, nút "Hiện bản dịch" chỉ bật sau khi trả lời
- Màn viết: `textarea`, hiện khung gợi ý, đếm từ, nút nộp
- Player chia hai khối nếu chọn cách B

## File đụng tới

| File | Việc |
|---|---|
| `app/models/enums.py` | Thêm `ActivityKind.WRITE` |
| `app/seeds/schema.py` | Thêm `ReadingPassage`, `WritingTask`; sửa mặc định `mastery_weights`; nới `est_minutes` |
| `app/seeds/validate_content.py` | 6 luật mới ở trên |
| `app/seeds/loader.py` | Nạp 2 trường mới vào DB |
| `app/seeds/generate_audio.py` | **Đảm bảo không** sinh audio cho `reading_passage` |
| `app/models/content.py` | Cột cho 2 trường mới |
| `app/services/learning_path_service.py` | `skills_for_phase` |
| `app/web/templates/` + `static/js/` | Màn đọc, màn viết |
| `migrations/` | Alembic revision cho cột mới |

## Nghiệm thu

1. `make validate` xanh với luật mới trên một bài mẫu đã có đủ `reading_passage` + `writing_task`.
2. `make seed` chạy xong **không** sinh file audio nào cho `reading_passage`.
3. Một bài mẫu (đề xuất R01) chạy end-to-end: đọc → trả lời → viết → chấm → mastery gồm cả `read` và `write`.
4. `compute_mastery_raw` trả về đúng khi thiếu điểm một kỹ năng (không kẹt trần, không chia 0).
5. Migration chạy được cả chiều lên và chiều xuống.

## Rủi ro

`generate_audio.py` hiện quét theo cấu trúc bài. Nếu `reading_passage` vô tình lọt vào vòng quét, mỗi bài
đọc sẽ bị sinh audio và **phá luôn ý nghĩa của kỹ năng đọc** — đây là lỗi im lặng, không có gì báo.
Phải có test khẳng định số file audio sinh ra không đổi khi thêm `reading_passage`.
