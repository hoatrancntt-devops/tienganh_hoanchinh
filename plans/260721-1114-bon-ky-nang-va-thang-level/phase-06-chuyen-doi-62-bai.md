# Phase 06 — Chuyển đổi 62 bài sang 4 kỹ năng

**Phụ thuộc:** phase 03 (schema), 04 (bộ chấm viết).
**Loại việc:** soạn nội dung — **khối lượng lớn nhất của plan**. Bắt buộc chia đợt.

## Khối lượng thật

| Việc | Số bài | Ghi chú |
|---|---|---|
| Thêm `writing_task` | **62** | Mọi bài, theo quyết định đã chốt |
| Thêm `reading_passage` | **51** | 11 bài reading đã có văn bản, chỉ cần chuyển dạng |
| Chuyển R01–R10 từ `dialogue` sang `reading_passage` thật | 11 | Gỡ audio, đổi câu hỏi sang tiếng Anh |
| Cập nhật `mastery_weights` đủ 5 khoá | 62 | Cơ học, làm được bằng script |
| Cân bằng lại `difficulty` của quiz | ~10 | Xem mục "Việc kèm theo" |

Đây không phải việc làm một lần. **Chia đợt theo level, làm trọn từng level** — nếu bỏ dở, học viên ở
level đã xong vẫn có trải nghiệm 4 kỹ năng đầy đủ, thay vì mọi level đều nửa vời.

## Thứ tự đợt

| Đợt | Level | Bài | Vì sao trước |
|---|---|---|---|
| 1 | L1 + L2 | F01–F08, D01–D04, CP-F, CP-D (14 bài) | Người mất gốc gặp đầu tiên; cũng là nơi bài Đọc/Viết dễ soạn nhất |
| 2 | L3 | F09–F17, O01–O08, I01–I04, R01–R02, CP-O (24 bài) | Khối lớn nhất |
| 3 | L4 | F18–F20, I05–I15, R03–R10, CP-I, CP-R (24 bài) | Khó nhất, để cuối |

Mỗi đợt kết thúc bằng `make validate` + `make seed` + chạy thử một bài end-to-end.

## Nguyên tắc soạn `reading_passage`

- **Không sinh audio.** Đây là điều kiện phân biệt kỹ năng Đọc với kỹ năng Nghe. Nếu bài đọc nghe được,
  học viên sẽ nghe thay vì đọc, và kỹ năng Đọc lại biến mất y như hiện nay.
- Văn bản liền mạch, **không** chia `speaker` turns. R01 hiện nhét email vào cấu trúc hội thoại có
  `speaker: Linh` cho từng dòng — đó chính là thứ phải bỏ.
- Độ dài tăng theo level: L1 ~40 từ, L2 ~60, L3 ~90, L4 ~130.
- **Câu hỏi bằng tiếng Anh.** Quiz hiện hỏi bằng tiếng Việt → đang đo hiểu tiếng Việt chứ không phải đọc
  hiểu tiếng Anh. Bản dịch tiếng Việt vẫn có, nhưng ẩn tới khi nộp.
- Loại văn bản đa dạng theo chủ đề bài: `chat`, `email`, `ticket`, `doc`, `announcement`.
- Tái dùng từ vựng của chính bài đó — bài đọc là chỗ gặp lại 6 từ mới trong ngữ cảnh khác, không phải chỗ
  giới thiệu thêm từ mới.

## Nguyên tắc soạn `writing_task`

Dạng bài theo level, tăng dần độ tự do:

| Level | Dạng chính | Ví dụ |
|---|---|---|
| L1 | `fill_blank` | Điền từ vào tin nhắn 1 câu |
| L2 | `fill_blank`, `reorder` | Sắp 3 câu thành tin nhắn đúng thứ tự |
| L3 | `error_correction`, `guided_email` | Sửa lỗi; viết email 2–3 câu có khung |
| L4 | `guided_email` | Viết email 4–5 câu, khung lỏng hơn |

Với `guided_email`, mỗi bài phải khai đủ: khung mở/thân/kết, **≥3 cụm bắt buộc kèm biến thể chấp nhận
được**, độ dài tối thiểu, và ≥2 `common_mistakes` để sinh phản hồi tiếng Việt. Thiếu biến thể là nguyên
nhân số một khiến chấm luật đánh trượt người viết đúng.

## Việc kèm theo — nợ từ audit 2026-07-20

Đang mở 62 file YAML thì xử lý luôn, đừng mở lại lần nữa:

1. **Quiz của F01–F04 khó hơn quiz B1** (2.81 vs 2.46 trung bình). Người mới gặp phần khó nhất ngay bài
   thứ nhất — đúng chỗ dễ bỏ cuộc nhất. Nguyên nhân: quiz phân biệt âm (`mcq_listen`, cặp tối thiểu
   think/sink) được gán difficulty cao, dùng chung thang 1–5 với quiz ngữ nghĩa dù hai loại không so sánh
   được. Hạ difficulty ở F01–F04, hoặc tách thang riêng.
2. **Ba chỗ nhảy bậc đột ngột:** F10→F11 (hội thoại 22→46 từ), I04→I05 (transcript 26→49 từ, đồng thời
   nhảy A2→B1), R09→R10 (hội thoại 48→**151 từ**, gấp 3.1). R10 vẫn ghi cùng `est_minutes` như bài 40 từ.
3. **Tốc độ audio dừng ở 1.0 từ F08 trở đi**, 50/57 bài. Không bài nào vượt 1.0, trong khi mục tiêu là
   standup và call với khách nước ngoài — nơi người ta nói nhanh hơn 1.0. Cân nhắc đẩy lên 1.1 ở L4.

## Việc làm được bằng script

- Thêm 5 khoá vào `mastery_weights` của 62 file (giá trị theo phase, xem phase 03)
- Kiểm tra chéo: mọi bài có `reading_passage` thì **không** có mục audio tương ứng
- Thống kê độ dài `reading_passage` theo level để phát hiện chỗ nhảy bậc
- Kiểm tra câu hỏi đọc bằng tiếng Anh (tỉ lệ ký tự có dấu tiếng Việt)

Phần soạn nội dung thật (văn bản đọc, đề bài viết, cụm bắt buộc, phản hồi) **không** tự sinh được — đó là
việc viết tay, và là lý do phase này phải chia đợt.

## Nghiệm thu (mỗi đợt)

1. `make validate` xanh với luật đầy đủ của phase 03 (không còn chế độ cảnh báo).
2. `make seed` chạy xong, số file audio sinh ra **không tăng** so với trước khi thêm `reading_passage`.
3. Mọi bài trong đợt có đủ 4 kỹ năng sinh điểm; `mastery_weights` đủ 5 khoá, cộng đúng 1.0.
4. Chạy thử 2 bài bất kỳ trong đợt end-to-end: nghe → nói → đọc → viết → quiz → mastery.
5. Không bài nào vượt trần `est_minutes` đã chốt ở phase 03.
6. Câu hỏi đọc bằng tiếng Anh trên toàn bộ bài của đợt.

## Nghiệm thu toàn phase

Sau đợt 3: cả 62 bài đủ 4 kỹ năng, và ba nợ kỹ thuật ở mục "Việc kèm theo" đã được xử lý hoặc ghi rõ
lý do giữ nguyên.

## Rủi ro

Đây là phase dễ bỏ dở nhất. Nếu dừng giữa chừng, phải dừng **ở ranh giới đợt**, không dừng giữa đợt —
một level nửa có Viết nửa không thì cổng validate sẽ phải giữ chế độ cảnh báo vô thời hạn, và không ai
biết bài nào đã xong.
