# Phase 02 — Sửa 8 lỗi chấm điểm xếp lớp

**Phụ thuộc:** không. **Loại việc:** code, 1 file chính + test.
**Làm trước tiên** — lỗi đang gây xếp sai 2 bậc cho học viên đang dùng thật.

## File đụng tới

| File | Việc |
|---|---|
| `app/services/placement_service.py` | Toàn bộ 8 sửa lỗi bên dưới |
| `seeds/placement/form_{a,b}.yaml` | Giãn phân bố `difficulty` (mục 1) |
| test mới | Phủ 6 ca xếp band |

**Không** đụng `app/schemas/placement.py` và `app/api/routes/placement.py` ở phase này — mở rộng trục
điểm là phase 05.

## 8 sửa lỗi

### 1. Trần điểm 86.8 → không ai chạm B1 được (nghiêm trọng)

Đo bằng số thật của cả hai form: trả lời **đúng 100%** + nói hoàn hảo = 86.8 điểm → A2. Dải A2 danh nghĩa
65–101 nhưng 14 điểm cuối là vùng chết. Và `BANDS` không có mục B1.

Nguyên nhân: `_score_mcq` cho câu difficulty 1 đúng chỉ **60/100**:
```python
score = 100.0 * (0.5 + 0.5 * weight / 5)     # d=1 → 60, d=5 → 100
```

Sửa hai chỗ, cả hai đều cần:

- **Giãn thang điểm câu:** hệ số nền 0.5 quá thấp. Câu dễ trả lời đúng vẫn là trả lời đúng — nên được
  ~85. Đề xuất `0.8 + 0.2 * weight/5` (d=1 → 84, d=5 → 100). Giá trị cuối chốt khi chạy lại bảng mô phỏng.
- **Thêm band B1 vào `BANDS`.** Sau khi giãn thang, chạy lại mô phỏng để đặt 3 mốc cắt sao cho:
  đúng ~40% → A1, đúng ~70% → A2, đúng ~90% + nói tốt → B1.

Đồng thời giãn `difficulty` trong form: hiện mỗi phần chỉ có **một** câu difficulty 5, kéo trung bình
xuống. Phân bố đều hơn.

### 2. Tụt 2 bậc do 3 nhánh hạ bậc chồng nhau (nghiêm trọng)

`placement_service.py:147-160` có ba nhánh chạy nối tiếp, không loại trừ nhau:

```python
if speech_available and speaking < 30 and band != PRE_A1:  band -= 1   # phủ quyết nói
if not speech_available:                                    band -= 1   # thiếu dữ liệu nói
if near_edge and index(band) > 0:                           band -= 1   # sát biên
```

Ca thật đã kiểm chứng:
- knowledge 90, listening 90, speaking 29 → 65.6 → A2 → phủ quyết → A1 → near_edge (|65.6−65|=0.6) → **Pre-A1**
- knowledge 60, listening 75, micro hỏng → 67.5 → A2 → thiếu nói → A1 → near_edge → **Pre-A1**

Gốc rễ: `near_edge` được thiết kế cho *điểm gốc* nhưng lại chạy *sau* khi band đã bị hạ vì lý do khác.

**Sửa:** gộp thành **một** lần điều chỉnh, tối đa 1 bậc. Tính `band_raw` từ điểm gốc, thu thập mọi lý do
hạ bậc vào một danh sách, rồi hạ đúng một lần nếu danh sách không rỗng. `near_edge` chỉ xét trên
`band_raw`, không xét trên band đã hạ.

### 3. Bỏ câu khó thì điểm tăng

`submit()` chỉ lấy trung bình trên câu **đã trả lời**. Trả lời đúng mỗi `V5` (difficulty 5) rồi bỏ 8 câu
còn lại → `knowledge = 100`; làm đúng cả 9 câu → 77.8.

**Sửa:** mẫu số là **toàn bộ câu của section trong form**, không phải số câu đã trả lời. Câu không trả
lời tính 0 điểm. Lấy danh sách câu từ `form["items"]` chứ không từ `responses`.

### 4. Công thức `confidence` sai thứ nguyên

```python
self_avg = trung bình choice_index         # thang 0–4 (Likert)
measured_level = index(band) + 1           # thang 1–4 (bậc CEFR)
if abs(self_avg - measured_level * 1.5) >= 2: confidence = "low"
```

Hai đại lượng khác đơn vị, phép trừ vô nghĩa. Hệ quả: band B1 → ngưỡng 6, `self_avg` tối đa 4 → **luôn**
low confidence. `confidence == "low"` lại mở quyền thi lại ngay (`can_retake`) và bật `can_challenge`,
nên lỗi rò thẳng ra hành vi sản phẩm.

**Sửa:** bỏ hẳn công thức, thay bằng luật rõ ràng — `low` khi (a) không chấm được phần nói, hoặc
(b) chênh lệch giữa trục cao nhất và thấp nhất > 40 điểm, hoặc (c) điểm tổng nằm trong 3 điểm quanh mốc
cắt. Chuẩn hoá `self_avg` về thang 0–100 nếu vẫn muốn dùng để đối chiếu.

### 5. `replay_count` do client tự khai, phạt 15%/lần

Nghe 3 lần → mất 45% điểm. Không phân biệt "chưa hiểu" với "loa chưa bật / audio chưa tải xong". Server
không kiểm chứng. Luật cũng đang áp cho `vocab`/`grammar` (vô hại vì không có audio, nhưng cho thấy áp bừa
theo section).

**Sửa:** hạ `REPLAY_PENALTY` xuống 0.10, chặn trần tổng phạt ở 20%, và chỉ áp cho `section == "listening"`.
Lần nghe thứ 2 miễn phạt (lần đầu thường là để làm quen giọng).

### 6. Bỏ trống câu tự đánh giá bị tính là "Không bao giờ"

`self_answers.append(resp.get("choice_index") or 0)` (dòng 102) — `None` → `0` = mức thấp nhất.
**Sửa:** bỏ qua câu `None`, không đưa vào `self_answers`.

### 7. `latency_ms` thu thập nhưng không dùng

Lưu vào `PlacementResponse` rồi không xuất hiện ở công thức nào. Với bài xếp lớp, thời gian phản xạ phân
biệt "biết chắc" với "đoán mò".

**Sửa:** dùng làm tín hiệu phụ cho `confidence` — trả lời đúng nhưng chậm bất thường (> 3× trung vị của
chính học viên đó) thì hạ `confidence`, **không** trừ điểm. Không đủ căn cứ để trừ điểm.

### 8. Sàn im lặng cứng 3/5 + trọng số nói 0.40

Một sự cố micro giữa chừng đủ phá toàn bộ kết quả, vì không phân biệt "im lặng vì không nói được" với
"im lặng vì thu âm lỗi".

**Sửa:** phân biệt hai tình huống — nếu client báo lỗi thu âm (đã có mã lỗi từ `speech_service`) thì coi
là *thiếu dữ liệu* (nhánh `not speech_available`), không phải *im lặng*. Chỉ đếm `silent` khi có file âm
thanh hợp lệ nhưng transcript rỗng.

## Test bắt buộc

Test theo ca, mỗi ca một hàng, khẳng định band cuối và `confidence`:

| Ca | Đầu vào | Kỳ vọng |
|---|---|---|
| Hoàn hảo | đúng 100%, nói 95 | **B1** — chứng minh trần đã được gỡ |
| Giỏi giấy, yếu nói | k=90, l=90, speaking=29 | Hạ **đúng 1 bậc**, không phải 2 |
| Micro hỏng | k=60, l=75, không có speech | Hạ **đúng 1 bậc**, `confidence=low` |
| Sát biên | tổng cách mốc cắt 2 điểm | Hạ 1 bậc, không cộng dồn với lý do khác |
| Bỏ câu khó | chỉ trả lời 1 câu d=5 đúng | Điểm **thấp**, không phải 100 |
| Im lặng thật | 4/5 lượt nói có audio nhưng transcript rỗng | Pre-A1, `confidence=low` |

## Nghiệm thu

1. Sáu ca test trên đều xanh.
2. Không tồn tại đầu vào nào làm tụt quá 1 bậc so với band tính từ điểm gốc — khẳng định bằng test
   quét toàn dải điểm, không chỉ 6 ca mẫu.
3. Học viên trả lời đúng 100% + nói tốt ra **B1**.
4. `BANDS`, `CEFR_ORDER`, `ENTRY_LESSON` cùng có đủ 4 bậc (phối hợp với phase 01).
5. Test cũ của placement vẫn xanh, hoặc được cập nhật có chủ đích và ghi rõ lý do.
