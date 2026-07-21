# Phase 05 — Đề xếp lớp 4 kỹ năng

**Phụ thuộc:** phase 01 (thang level), 02 (chấm điểm sạch), 03 (schema), 04 (bộ chấm viết).
**Loại việc:** nội dung đề + code + UI.

## Vấn đề đang giải

Đề hiện tại 23 câu, không có kỹ năng Đọc, không có kỹ năng Viết:

| Section | Câu | Kỹ năng thật |
|---|---|---|
| `self` | 3 | Tự đánh giá, không tính điểm |
| `vocab` | 5 | Từ vựng thụ động — đề bài bằng **tiếng Việt** |
| `grammar` | 4 | Nhận diện câu đúng |
| `listening` | 6 | Nghe |
| `speaking` | 5 | Nói |

Màn kết quả (`placement_result.html:13`) hiện đúng 3 nhãn: **Nghe / Nói / Từ vựng & ngữ pháp**.

Lưu ý: `vocab` hỏi *nghĩa tiếng Việt của từ tiếng Anh* → đo từ vựng thụ động, **không phải** đọc hiểu.
Đọc hiểu là rút thông tin từ văn bản có ngữ cảnh. Đừng đổi nhãn `vocab` thành "Đọc" để lấp chỗ trống.

## Quyết định đã chốt

**Một band chung + biểu đồ 4 trục.** `ENTRY_LESSON` vẫn nhận một band duy nhất (giữ đơn giản), nhưng
kết quả hiện 4 trục Nghe/Nói/Đọc/Viết để học viên thấy mình lệch ở đâu.

## Ngân sách thời gian — ràng buộc cứng

Đề hiện `est_minutes: 14`. Thêm Đọc + Viết mà không cắt gì thì lên ~22 phút. **Bỏ ngang ở bước đầu tiên
là rủi ro lớn nhất của cả plan này** — học viên chưa học gì đã phải ngồi 22 phút.

Cân đối đề xuất, giữ **tổng ≤ 18 phút**:

| Section | Hiện | Mới | Ghi chú |
|---|---|---|---|
| `self` | 3 | 3 | Giữ |
| `vocab` | 5 | **3** | Cắt 2 — trùng vai trò với `reading` |
| `grammar` | 4 | **3** | Cắt 1 |
| `listening` | 6 | 5 | Cắt 1 |
| `speaking` | 5 | 5 | Giữ — trọng số cao nhất |
| `reading` | 0 | **4** | Mới |
| `writing` | 0 | **3** | Mới |
| **Tổng** | 23 | **26** | +3 câu, ~+4 phút |

## Thiết kế section `reading` (4 câu)

Hai đoạn văn ngắn, tăng dần, mỗi đoạn 2 câu hỏi:

1. **Tin nhắn chat công việc, ~40 từ** — 1 câu tìm thông tin cụ thể, 1 câu ý chính
2. **Email có yêu cầu và hạn chót, ~90 từ** — 1 câu suy luận (ai phải làm gì), 1 câu đoán nghĩa từ ngữ cảnh

Bắt buộc: **không có audio**. Câu hỏi bằng tiếng Anh (khác quiz trong bài học hiện đang hỏi bằng tiếng
Việt). Có nút hiện bản dịch **sau khi** nộp.

Cách này cũng phân biệt được người "đọc được nhưng không nghe được" — nhóm rất phổ biến ở học viên Việt
học ngữ pháp ở trường — mà đề hiện tại hoàn toàn không thấy.

## Thiết kế section `writing` (3 câu)

Dùng đúng bộ chấm ở phase 04, ba dạng tăng dần:

1. `fill_blank` — điền 2 chỗ trống trong tin nhắn ngắn (đo từ vựng chủ động)
2. `error_correction` — sửa 1 câu sai kiểu người Việt hay mắc (thiếu `s` số nhiều / sai thì)
3. `guided_email` — viết 2–3 câu trả lời một email, có khung cho sẵn (đo viết thật)

Câu 3 là câu duy nhất mở. Chấm rộng tay theo nguyên tắc ở phase 04 — người mất gốc viết được 2 câu có
nghĩa đã là tín hiệu mạnh.

## Chấm điểm và trục hiển thị

Trục điểm mới:

```
listening  ← section listening
speaking   ← section speaking
reading    ← section reading
writing    ← section writing
knowledge  ← vocab + grammar   (trục phụ, không hiện trên biểu đồ 4 trục)
```

Trọng số cho band chung — đề xuất, chốt khi chạy mô phỏng:

```python
WEIGHTS = {speaking: 0.30, listening: 0.25, reading: 0.20, writing: 0.15, knowledge: 0.10}
```

Nói vẫn nặng nhất (mục tiêu sản phẩm), nhưng không còn 0.40 như hiện tại — vì bây giờ có 4 kỹ năng chia
nhau, và trọng số 0.40 cộng với sự cố micro là nguyên nhân của lỗi xếp sai ở phase 02.

**Nhánh dự phòng bắt buộc:** khi không chấm được phần nói (micro hỏng / speech service chết), chuẩn hoá
lại trọng số trên 4 trục còn lại thay vì rơi vào nhánh `0.5*knowledge + 0.5*listening` như hiện nay.
Giờ đã có Đọc và Viết nên dữ liệu còn lại đủ dày để xếp lớp tử tế.

## File đụng tới

| File | Việc |
|---|---|
| `seeds/placement/form_{a,b}.yaml` | Cắt/thêm câu theo bảng trên; **hai form phải tương đương độ khó** |
| `app/services/placement_service.py` | Trục điểm 3 → 5, trọng số mới, nhánh dự phòng |
| `app/schemas/placement.py` | Section mới, kiểu response cho câu viết |
| `app/api/routes/placement.py` | Nối bộ chấm viết vào luồng nộp bài |
| `app/web/templates/placement.html` | Màn đọc (không audio) + màn viết (textarea) |
| `app/web/templates/placement_result.html` | Biểu đồ 4 trục thay 3 nhãn |
| `app/web/static/js/placement.js` | Điều hướng section mới, đếm thời gian |

## Nghiệm thu

1. Đề chạy end-to-end trong **≤ 18 phút** đo thật, không phải ước lượng.
2. Kết quả trả về đủ 4 trục + 1 band trong `{pre_a1, a1, a2, b1}`.
3. Ca "đọc tốt, nghe kém" (reading 85, listening 30) ra kết quả **khác** ca "nghe tốt, đọc kém" — khẳng
   định hai trục thật sự độc lập, không phải trang trí.
4. Micro hỏng: vẫn xếp được band từ 3 trục còn lại, `confidence = low`, **không** tụt 2 bậc.
5. Form A và form B cho kết quả lệch nhau ≤ 5 điểm trên cùng một bộ đáp án tương đương.
6. Câu hỏi đọc bằng tiếng Anh; phần đọc **không** có file audio nào được sinh.

## Rủi ro

Hai form đề hiện **giống hệt nhau về phân bố difficulty** (đã kiểm: cùng `[1,2,3,4,5]` vocab,
`[1,2,3,4]` grammar, `[1,2,2,3,4,5]` listening). Khi thêm section mới phải giữ được tính tương đương này,
nếu không việc thi lại bằng form khác sẽ cho kết quả lệch mà không ai biết.
