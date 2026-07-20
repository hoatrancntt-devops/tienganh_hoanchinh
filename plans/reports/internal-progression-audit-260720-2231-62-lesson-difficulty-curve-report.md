# Audit tiến độ độ khó — 62 bài học

Ngày: 2026-07-20
Phạm vi: `seeds/content/**/*.yaml` (57 bài học + 5 checkpoint)
Phương pháp: trích metric cơ học từ YAML, không dùng LLM chấm điểm chất lượng nội dung.

## Tóm tắt

Đường cong độ khó **phẳng hơn nhiều so với những gì nhãn CEFR tuyên bố**. Nội dung từng bài viết tốt, nhưng
các tham số điều khiển độ khó (số từ vựng, độ dài, độ khó quiz, thời lượng) gần như là hằng số. Có 4 vấn đề
thật, 3 vấn đề cần bạn quyết định vì phụ thuộc ý đồ sản phẩm.

## Metric đã đo

| Chỉ số | Kết quả | Nhận xét |
|---|---|---|
| Số từ vựng/bài | **6 cho cả 57/57 bài** | Hằng số tuyệt đối |
| Thời lượng ước tính | 10 phút (41 bài), 11 (14), 12 (2) | Gần như hằng số |
| Tốc độ audio | 0.85 (6 bài), 0.9 (1), 1.0 (50 bài) | Chỉ 7 bài đầu được nói chậm |
| Ngưỡng mastery | 80 → 78 → 75 → 70 (giảm dần theo phase) | **Giảm khi bài khó lên** |
| Phân bố CEFR | pre_A1: 4, A1: 8, A2: 23, B1: 22 | Nền móng mỏng |
| Độ khó quiz TB | pre_A1: 2.81 · A1: 2.32 · A2: 2.45 · B1: 2.46 | **Đảo ngược ở bậc thấp nhất** |
| Độ dài transcript nghe | pre_A1: 23 từ · A1: 27.8 · A2: 24.0 · B1: 35.5 | A2 dễ hơn A1 |

## Vấn đề thật (nên sửa)

### 1. Độ khó quiz không tăng theo cấp độ — còn đảo ngược ở bậc đầu

4 bài `pre_a1` có quiz khó trung bình **2.81/5**, cao hơn cả 22 bài `b1` (2.46). Bài F03 đạt 3.25 — khó nhất
toàn bộ giáo trình, trong khi nó là bài thứ ba của người mới bắt đầu.

Nguyên nhân có thể đoán: quiz phân biệt âm (`mcq_listen` với cặp tối thiểu như think/sink, thirty/thirteen)
tự nhiên được gán difficulty cao. Nhưng kết quả là **người mới gặp phần khó nhất ngay đầu**, đúng chỗ dễ bỏ cuộc nhất.

Đề xuất: hoặc hạ difficulty ở F01–F04, hoặc tách thang difficulty riêng cho quiz ngữ âm và quiz ngữ nghĩa —
hiện hai loại đang dùng chung một thang 1–5 nhưng không so sánh được với nhau.

### 2. Ngưỡng mastery giảm dần khi bài khó lên

`foundation` 78–80 → `daily`/`office`/`it_english` 75 → `reading` 70.

Nghĩa là bài càng khó, yêu cầu càng dễ. Nếu chủ ý là "giảm ma sát để người học không bỏ giữa chừng" thì hợp lý,
nhưng nó mâu thuẫn với ý nghĩa của từ "mastery" — và người học đọc con số đó sẽ hiểu ngược. Cần quyết định rõ
đây là thiết kế hay là trôi dạt.

### 3. Tốc độ audio dừng ở 1.0 từ bài F08 và không bao giờ đổi nữa

50/57 bài dùng speed 1.0. Không có bài nào vượt 1.0. Với người học hướng tới môi trường làm việc thật
(standup, call với khách nước ngoài), tốc độ hội thoại thật thường nhanh hơn 1.0 — giáo trình hiện không
chuẩn bị cho điều đó ở bất kỳ đâu.

### 4. Ba chỗ nhảy bậc đột ngột về khối lượng

| Chuyển tiếp | Thay đổi |
|---|---|
| F10 → F11 | Hội thoại 22 → 46 từ (gấp đôi) |
| I04 → I05 | Transcript nghe 26 → 49 từ, đồng thời nhảy A2 → B1 |
| R09 → R10 | Hội thoại 48 → **151 từ** (gấp 3.1) |

R10 là bài dài nhất giáo trình với biên độ lớn. Nếu đây là bài kết chủ ý (climax của mạch truyện) thì chấp nhận
được, nhưng nên báo trước cho người học hoặc tăng `est_minutes` — hiện R10 vẫn ghi cùng thời lượng như bài 40 từ.

## Cần bạn quyết định

### 5. Số từ vựng cố định 6/bài trên toàn bộ 57 bài

Không có bài nào 4 từ, không có bài nào 8 từ. Đây là dấu hiệu con số được chọn theo khuôn mẫu chứ không theo
nhu cầu từng bài. Không nhất thiết sai — 6 từ/bài là tải lượng hợp lý — nhưng nó có nghĩa là **độ khó thực sự
của bài không được điều khiển bởi tham số nào cả**, chỉ bởi nội dung. (Agent đang nghiên cứu xem có bằng chứng
nào về con số hợp lý cho vocabulary load; sẽ đối chiếu sau.)

### 6. Nền móng mỏng so với phần còn lại

Chỉ 4 bài `pre_a1` + 8 bài `a1` (21% giáo trình) trước khi nhảy vào 45 bài A2/B1. Nếu đối tượng là người
"mất gốc" thì tỷ lệ này quá dốc. Nếu đối tượng là người đã có nền A2 muốn chuyển sang tiếng Anh IT thì hợp lý —
nhưng khi đó 4 bài pre_A1 kia lại thừa.

Đây là câu hỏi định vị sản phẩm, mình không tự quyết được.

### 7. Phase `reading` không có speaking drill nào (10/10 bài)

Nhất quán và chủ ý — đây là kỹ năng đọc. Đã kiểm tra code và xác nhận **xử lý đúng**: cả 11 file reading đặt
`mastery_weights: {quiz: 0.7, listen: 0.3}` (bỏ hẳn `speak`, cộng đúng 1.0) và `min_speaking_attempts: 0`.
`compute_mastery_raw()` tại `app/services/prerequisite_service.py:46` chia cho tổng trọng số thực tế nên không
có chuyện điểm bị kẹt trần. Không cần sửa gì.

## Không phải vấn đề (đã kiểm tra, sạch)

- **Chuỗi `recommended_next` và `prerequisites`**: 10 tham chiếu tới `CP-*` — cả 5 file checkpoint đều tồn tại.
  Không có link gãy.
- **Tụt lùi CEFR giữa các phase** (F20 b1 → D01 a1, I15 b1 → R01 a2): mỗi phase là một track riêng có điểm vào
  riêng, không phải lỗi tuần tự.
- **Cấu trúc bài**: 57/57 bài đều đủ dialogue, listening, quiz, common_mistakes.

## Giới hạn của audit này

Đây là đo **cơ học**, không phải đánh giá sư phạm. Nó đo được số từ, độ dài câu, nhãn difficulty do chính
người viết gán — không đo được liệu nội dung có thật sự dễ hiểu, ngữ pháp có tăng dần đúng thứ tự tự nhiên,
hay hội thoại có tự nhiên không. Nhãn `difficulty` trong quiz là tự gán, nên mọi kết luận dựa trên nó kế thừa
sai lệch của người gán.

Chưa kiểm tra: độ khó ngữ pháp (thì, câu điều kiện, mệnh đề quan hệ) theo thứ tự bài — cần phân tích cú pháp
sâu hơn hoặc chấm bằng LLM.

## Câu hỏi chưa giải quyết

1. Ngưỡng mastery giảm dần là chủ ý hay trôi dạt?
2. Đối tượng thật là "mất gốc" hay "đã có A2, cần tiếng Anh IT"? Quyết định này ảnh hưởng tới mục 6.

(Câu hỏi về `mastery_weights.speak` ở phase reading đã được giải quyết — xem mục 7.)
