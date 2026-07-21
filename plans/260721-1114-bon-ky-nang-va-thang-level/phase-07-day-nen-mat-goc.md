# Phase 07 — Dày nền cho người mất gốc

**Phụ thuộc:** phase 01 (thang level), 06 (bài mới phải có sẵn 4 kỹ năng ngay từ đầu).
**Loại việc:** soạn nội dung — ~12 bài học mới.

## Vấn đề đang giải

Quyết định đối tượng đã chốt: **mất gốc hoàn toàn**. Phân bố nội dung hiện tại không phục vụ nhóm đó.

| Level | Bài hiện có | Số bài |
|---|---|---|
| L1 (Pre-A1) | F01–F04 | **4** |
| L2 (A1) | F05–F08, D01–D04, CP-F, CP-D | **10** |
| L3 (A2) | F09–F17, O01–O08, I01–I04, R01–R02, CP-O | 24 |
| L4 (B1) | F18–F20, I05–I15, R03–R10, CP-I, CP-R | 24 |

14 bài nền rồi nhảy vào 48 bài A2/B1. Với người chưa biết gì, đó là vách đứng đúng chỗ họ dễ bỏ nhất.

Đối chiếu bên ngoài: VUS iTalk **60 bài mỗi level**; Ms Hoa 5 level / 68 buổi ≈ 14 buổi mỗi level.
Mục tiêu đề xuất khiêm tốn hơn cả hai: **L1 ≈ 12 bài, L2 ≈ 14 bài** → cần thêm ~8 bài L1 và ~4 bài L2.

Con số cuối chốt ở phase 01 khi viết `docs/khung-level.md`.

## Bốn bài L1 hiện có dạy gì

F01–F04 là **bài ngữ âm thuần**: /θ/ và /ð/, âm cuối /s/ /z/, âm cuối /t/ /d/, cụm phụ âm cuối. Đúng và
cần thiết cho người Việt, nhưng chưa đủ để gọi là một level.

Lưu ý từ audit CEFR ngày 20/07: **thang ngữ âm của CEFR Companion Volume 2020 (tr.135) không có bậc
Pre-A1**. Nhãn `pre_a1` ở đây mô tả *thứ tự dạy*, không phải *bậc năng lực* — nên L1 phải được đặt tên là
"bậc khởi động" và không tuyên bố tương đương KNLNN (đã ghi ở phase 01).

## Bài cần thêm cho L1 (~8 bài)

Nguyên tắc: người mất gốc cần **sống sót** trước khi cần đúng. Ưu tiên thứ tự chữ cái, số, và cụm cứu hộ.

Chủ đề đề xuất, chốt lại khi soạn:

1. Bảng chữ cái và đánh vần tên mình (người Việt bị hỏi "spell your name" liên tục)
2. Số 0–100 và nghe số điện thoại / số phòng
3. Giờ và ngày trong tuần (nối thẳng vào D01 sau này)
4. Cụm cứu hộ: *Sorry?* / *Say that again, please* / *I don't understand* — dạy sớm nhất có thể, vì đây là
   thứ giữ họ ở lại trong cuộc hội thoại thay vì im lặng
5. Trọng âm từ — người Việt nói đều đều, đây là lỗi làm người nghe không hiểu nhiều hơn cả lỗi âm cuối
6. Ngữ điệu câu hỏi lên / câu kể xuống
7. Nguyên âm dài–ngắn (`ship`/`sheep`)
8. Nhịp câu: nối âm và nuốt âm khi nói tự nhiên

Bài 4 nên đứng **rất sớm**, có thể là bài thứ hai của cả giáo trình. Nó có giá trị thực dụng cao nhất
trong toàn bộ L1.

## Bài cần thêm cho L2 (~4 bài)

Lấp khoảng trống giữa "phát âm được" và "nói được câu có việc":

1. Giới thiệu bản thân trong công việc (tên, phòng ban, làm gì)
2. Hỏi và trả lời thông tin cơ bản ở văn phòng
3. Nói về việc đang làm hôm nay (nối vào standup ở D/O sau này)
4. Xin lỗi, cảm ơn, và nhờ giúp đỡ

## Ràng buộc soạn bài

- Bài mới phải có **đủ 4 kỹ năng ngay từ đầu** — schema của phase 03, chấm viết của phase 04. Không tạo
  thêm bài thiếu Đọc/Viết rồi phải quay lại sửa.
- Giữ 6 từ vựng mỗi bài để nhất quán với 57 bài hiện có, **trừ khi** bài đó có lý do rõ (bài số đếm
  có thể nhiều hơn). Audit ngày 20/07 ghi nhận 6 từ/bài là hằng số tuyệt đối trên cả 57 bài — nhất quán,
  nhưng cũng có nghĩa độ khó bài không được điều khiển bởi tham số nào.
- Đường cong độ khó phải **tăng**, ngược với hiện trạng: quiz L1 hiện khó hơn quiz B1.
- `speed` audio ở L1 nên ≤ 0.85. Hiện chỉ 7 bài đầu được nói chậm, phần còn lại nhảy thẳng lên 1.0.
- Cập nhật DAG `prerequisites` và `recommended_next` cho bài mới, giữ nguyên bất biến: level của bài
  tiên quyết ≤ level của bài phụ thuộc (kiểm tra chéo đã định nghĩa ở phase 01).

## File đụng tới

| File | Việc |
|---|---|
| `seeds/content/foundation/*.yaml` | ~12 file mới |
| `seeds/content/foundation/CP-F.yaml` | Cập nhật điều kiện chốt cho bài mới |
| `docs/khung-level.md` | Cập nhật danh sách bài và số tuần của L1, L2 |
| `app/services/placement_service.py` | `ENTRY_LESSON` nếu bài đầu của level đổi |

## Nghiệm thu

1. L1 ≥ 12 bài, L2 ≥ 14 bài (hoặc con số đã chốt ở phase 01).
2. `make validate` xanh; DAG không có chu trình; không có bài mồ côi.
3. Bất biến level được giữ: không cạnh tiên quyết nào đi từ level cao xuống level thấp.
4. Đường cong difficulty quiz **tăng dần** L1 → L4 — đo bằng script, không đánh giá bằng cảm nhận.
5. Mọi bài mới có đủ 4 kỹ năng và `mastery_weights` 5 khoá.
6. Chạy thử toàn bộ L1 end-to-end như một học viên mới.

## Rủi ro

Thêm 12 bài vào đầu lộ trình làm **học viên hiện có** bị đẩy lùi vị trí — người đang ở F05 bỗng thấy
mình ở giữa một level dài hơn. Cần kiểm tra: bài đã `mastered` phải giữ nguyên trạng thái, và tiến độ
hiển thị không được tụt về mức thấp hơn thực tế. Nếu app đã có học viên thật trên VPS, đây là việc bắt
buộc kiểm trước khi seed.
