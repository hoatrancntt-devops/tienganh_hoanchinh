# Phase 04 — Chấm điểm Viết bằng luật (không AI)

**Phụ thuộc:** phase 03. **Chặn:** phase 05, 06.
**Loại việc:** code — một module mới + test.

## Ràng buộc nền

Quyết định kiến trúc số 4 của project (README): *"AI là phần thêm, không phải nền. Không có API key thì
app vẫn dạy đủ."* Chấm phát âm đã chạy local không cần LLM. **Chấm viết phải theo đúng nguyên tắc đó** —
chạy được khi không có API key nào.

Đây là ràng buộc, không phải sở thích: nếu chấm viết cần AI thì kỹ năng Viết sẽ biến mất với mọi cài đặt
không có key, và tuyên bố "đủ 4 kỹ năng" thành sai.

## Module mới

`app/services/writing_service.py` — song song với `speech_service.py` đang chấm phát âm.

Vào: `writing_task` (từ bài học) + văn bản học viên nộp.
Ra: `{score: 0-100, detail: {...}, feedback_vi: str, errors: [...]}` — cùng hình dạng với kết quả chấm nói
để `learning_path_service` dùng lại được đường ống hiện có.

## Thuật toán theo dạng bài

### `fill_blank` và `error_correction`

Cả hai là so khớp một ô nhập với tập đáp án chấp nhận được. Chuẩn hoá trước khi so: bỏ khoảng trắng thừa,
thường hoá chữ hoa (trừ khi bài đang **dạy** viết hoa), bỏ dấu câu cuối.

Điểm từng phần theo khoảng cách Levenshtein: khớp chính xác 100; sai ≤2 ký tự 80 kèm phản hồi "gần đúng,
sai chính tả"; còn lại 0. Ngưỡng 2 ký tự bắt được lỗi gõ mà không tha lỗi từ vựng thật.

### `reorder`

So sánh hoán vị người học nộp với thứ tự đúng. Không chấm nhị phân — dùng số cặp đúng thứ tự trên tổng số
cặp (Kendall tau chuẩn hoá về 0–100). Sắp gần đúng phải được điểm gần đúng, nếu không học viên chỉ cần
sai một chỗ là mất trắng.

### `guided_email` — dạng khó, chấm theo tầng

Đây là dạng duy nhất có đầu ra tự do. Chấm 4 tầng, cộng điểm:

| Tầng | Điểm | Kiểm tra |
|---|---|---|
| Cấu trúc | 25 | Có lời chào? có thân? có kết + ký tên? |
| Nội dung bắt buộc | 40 | Đủ các cụm bắt buộc khai trong `writing_task` (chấp nhận biến thể) |
| Cơ học | 20 | Viết hoa đầu câu, dấu chấm cuối, độ dài ≥ tối thiểu |
| Lỗi thường gặp | 15 | Trừ điểm cho mỗi lỗi khớp `common_mistakes` của bài |

**Nguyên tắc chấm:** thưởng cái làm được, không phạt cái không phát hiện được. Luật không đọc hiểu được
ngữ nghĩa, nên mọi thứ nó không kiểm tra được đều mặc định là **đạt**. Chấm chặt bằng luật sẽ đánh trượt
người viết đúng theo cách khác — hỏng hơn nhiều so với cho điểm rộng tay.

Cụ thể: cụm bắt buộc phải khai kèm **biến thể chấp nhận được**. Ví dụ bài yêu cầu xin nghỉ phép thì
`["I'd like to take", "I would like to take", "I want to take", "Can I take"]` cùng tính là đạt. Tái dùng
đúng ý tưởng `accept_patterns` mà `seeds/placement/form_a.yaml` đang dùng cho câu nói tự do.

## Phản hồi tiếng Việt

Bắt buộc — đây là sản phẩm giải thích hoàn toàn bằng tiếng Việt. Phản hồi phải chỉ đúng chỗ sai và nói
cách sửa, không được chung chung.

Sinh từ `errors` mà bộ chấm phát hiện, theo mẫu gắn với từng loại lỗi. Không có lỗi nào phát hiện được thì
phản hồi là lời xác nhận cụ thể ("Email của bạn đủ ba phần và có đủ thông tin Linh cần"), không phải
"Tốt lắm!".

## Nối vào hệ có sẵn

- Ghi `ItemAttempt` với `kind = "write"` để `_recent_scores_by_kind`
  (`app/services/learning_path_service.py:44`) gom được vào `mastery_weights.write`.
- Có cần `min_writing_attempts` giống `min_speaking_attempts` không? `apply_speaking_gate`
  (`prerequisite_service.py:55`) chặn kiểu "quiz giỏi + bỏ phần nói". Với Viết, đề xuất **không** thêm
  cổng chặn ở phase này — thêm một cổng nữa cho người mất gốc là thêm chỗ bỏ cuộc. Xem lại sau khi có
  dữ liệu học viên thật.

## API

`POST /api/v1/learning/writing/submit` — nhận `{lesson_id, task_id, text}`, trả kết quả chấm.
Giới hạn độ dài đầu vào (chống nộp văn bản khổng lồ). Không lưu văn bản thô quá mức cần thiết.

## File đụng tới

| File | Việc |
|---|---|
| `app/services/writing_service.py` | **Tạo mới** — toàn bộ logic chấm |
| `app/api/routes/learning.py` | Endpoint nộp bài viết |
| `app/schemas/learning.py` | I/O cho bài viết |
| `app/services/learning_path_service.py` | Gom điểm `write` vào mastery |
| test mới | Xem bên dưới |

## Test bắt buộc

1. **Mỗi dạng bài** có ca đúng hoàn toàn → 100, và ca sai hoàn toàn → gần 0.
2. `reorder` sai một cặp → điểm cao, không phải 0 (khẳng định điểm từng phần).
3. `guided_email`: cùng một ý diễn đạt bằng **3 cách khác nhau** đều đạt — đây là test quan trọng nhất,
   nó bắt lỗi chấm quá khắt khe.
4. `fill_blank` sai chính tả 1 ký tự → 80 kèm phản hồi chính tả, không phải 0.
5. Chấm chạy đúng khi **không có API key nào** cấu hình.
6. Phản hồi tiếng Việt không rỗng ở mọi ca, kể cả ca điểm 100.

## Nghiệm thu

1. Sáu nhóm test trên xanh.
2. Không có lời gọi LLM nào trong `writing_service.py` — kiểm bằng grep, không chỉ bằng test.
3. Điểm `write` xuất hiện trong mastery của bài mẫu và ảnh hưởng đúng theo trọng số.
4. Nộp văn bản rỗng trả về 0 kèm phản hồi hướng dẫn, không phải lỗi 500.

## Rủi ro

Chấm bằng luật **không** đo được: mạch lạc, giọng điệu phù hợp, ngữ pháp phức tạp. Đừng giả vờ là có.
`docs/khung-level.md` (phase 01) phải nói thẳng phần Viết được đo tới đâu, để tuyên bố đầu ra không hứa
quá thứ hệ thống kiểm chứng được.
