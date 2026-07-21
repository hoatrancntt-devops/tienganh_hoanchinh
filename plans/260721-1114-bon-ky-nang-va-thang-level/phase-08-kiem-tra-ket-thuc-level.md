# Phase 08 — Kiểm tra kết thúc level và lộ trình động

**Phụ thuộc:** phase 01 (thang level), 06 (bài đủ 4 kỹ năng).
**Loại việc:** code + nội dung đề (4 bài kiểm tra).

## Vấn đề đang giải

Ba thứ mà cả Ms Hoa lẫn VUS đều có, app không có:

1. **Bài kiểm tra kết thúc level.** App có 5 checkpoint (`CP-F`, `CP-D`, `CP-O`, `CP-I`, `CP-R`) nhưng
   chúng gắn với *phase*, không gắn với *level*. VUS iTalk: mini-test sau mỗi 10 chủ đề + bài tổng hợp
   cuối mỗi level.
2. **Số bài cố định mỗi level.** VUS: 60 bài/level. App: level chưa từng gắn với số bài nào.
   (Giải quyết ở phase 01 + 07.)
3. **Tuyên bố đầu ra 4 kỹ năng theo level.** (Giải quyết ở phase 01.)

Ngoài ra `estimated_weeks_to_goal` (`app/services/placement_service.py:222`) là **hằng số cứng**
`{Pre-A1: 14, A1: 10, A2: 7}` tuần. Không tính số phút/ngày học viên chọn ở onboarding, không tính số bài
còn lại, không cập nhật theo tiến độ thật. Học viên học 30 phút/ngày và học viên học 10 phút/ngày thấy
cùng một con số.

## 1. Bài kiểm tra kết thúc level

**Khác checkpoint hiện có ở ba điểm:**

| | Checkpoint (`CP-*`) | Kiểm tra kết thúc level |
|---|---|---|
| Gắn với | Phase (chủ đề) | Level (bậc năng lực) |
| Phạm vi | Bài trong phase đó | **Toàn bộ bài của level**, trộn chủ đề |
| Đo | Chủ yếu nói + quiz | **Đủ 4 kỹ năng**, mỗi kỹ năng có ngưỡng riêng |

Bốn bài, mỗi level một bài. Yêu cầu:

- Trộn nội dung từ mọi phase thuộc level đó, không theo thứ tự bài — đo năng lực còn lại chứ không đo trí
  nhớ ngắn hạn của bài vừa học.
- Có phần Nghe, Nói, Đọc, Viết riêng biệt, mỗi phần chấm riêng.
- **Ngưỡng theo từng kỹ năng**, không chỉ điểm tổng. Đạt 90 Đọc và 40 Nói mà vẫn qua level thì tuyên bố
  đầu ra ở `docs/khung-level.md` thành lời hứa suông.
- Không đạt một kỹ năng → gợi ý cụ thể bài nào cần ôn, dùng lại engine `next_up` sẵn có.

**Câu hỏi cần quyết khi làm:** không đạt thì **chặn** hay chỉ **cảnh báo**? Với người mất gốc, chặn cứng
là chỗ bỏ cuộc. Đề xuất: cảnh báo + gợi ý ôn, cho học tiếp; chỉ chặn nếu lệch quá lớn (một kỹ năng dưới
50 trong khi các kỹ năng khác trên 75). Cần bạn chốt.

## 2. Lộ trình động

Thay hằng số bằng tính thật:

```
tuần_còn_lại = (số_bài_chưa_mastered × est_minutes_trung_bình) / (phút_mỗi_ngày × ngày_học_mỗi_tuần) / 7
```

Đầu vào có sẵn: `daily_goal_minutes` từ onboarding (`app/web/templates/onboarding*.html:66`),
`est_minutes` của từng bài, trạng thái `mastered` từ `learning_path_service`.

Cần thêm: **tốc độ thật** — số bài học viên thực sự hoàn thành mỗi tuần trong 2–3 tuần gần nhất. Sau khi
có đủ dữ liệu, dùng tốc độ thật thay cho mục tiêu tự khai. Người đặt mục tiêu 30 phút/ngày mà học 10 phút
thì con số dựa trên mục tiêu là lời nói dối tử tế, và nó sẽ vỡ.

Hiển thị: khoảng, không phải con số đơn ("khoảng 8–11 tuần"), và ghi rõ dựa trên tốc độ nào.

## 3. Đầu ra khi hoàn thành lộ trình

Hiện **không tồn tại** khái niệm "hoàn thành lộ trình" — không có bài kiểm tra đầu ra, không có tuyên bố
"sau khi xong bạn làm được X".

Cần: màn tổng kết khi qua L4, đối chiếu kết quả 4 kỹ năng với tuyên bố đầu ra ở `docs/khung-level.md`,
và so sánh với kết quả bài xếp lớp lúc đầu (dữ liệu đã có trong `PlacementTest.result_scores`). Đây là
lúc duy nhất app chứng minh được nó có tác dụng.

## File đụng tới

| File | Việc |
|---|---|
| `seeds/level_tests/` | **Tạo mới** — 4 bài kiểm tra kết thúc level |
| `app/services/placement_service.py` | `estimated_weeks_to_goal` động |
| `app/services/learning_path_service.py` | Tốc độ học thật; điều kiện lên level |
| `app/models/assessment.py` | Model cho bài kiểm tra level (tái dùng `PlacementTest` nếu hợp) |
| `app/api/routes/learning.py` | Endpoint làm bài kiểm tra level |
| `app/web/templates/` | Màn kiểm tra level + màn tổng kết lộ trình |
| `docs/khung-level.md` | Nối điều kiện lên level vào tuyên bố đầu ra |

## Nghiệm thu

1. Bốn bài kiểm tra tồn tại, mỗi bài đo đủ 4 kỹ năng với ngưỡng riêng từng kỹ năng.
2. Học viên lệch kỹ năng (Đọc 90 / Nói 40) **không** qua level âm thầm — có cảnh báo và gợi ý ôn cụ thể.
3. `estimated_weeks_to_goal` đổi khi học viên đổi `daily_goal_minutes`, và đổi theo tiến độ thật.
4. Hai học viên cùng band nhưng khác tốc độ nhận hai con số khác nhau.
5. Màn tổng kết L4 hiện so sánh 4 trục lúc vào và lúc ra.
6. Test: học viên chưa đủ dữ liệu tốc độ (tuần đầu) vẫn nhận được ước lượng hợp lý, không chia 0.

## Rủi ro

Tái dùng `PlacementTest` cho bài kiểm tra level có thể làm hỏng `can_retake` (`placement_service.py:233`)
— hàm này tìm bài test gần nhất của user và áp luật 14 ngày. Nếu bài kiểm tra level ghi vào cùng bảng,
học viên làm bài cuối L1 sẽ bị khoá quyền thi lại xếp lớp. Hoặc tách bảng, hoặc thêm cột phân loại và
sửa mọi truy vấn hiện có.
