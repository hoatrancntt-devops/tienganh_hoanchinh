# Phase 01 — Thang level và tuyên bố đầu ra

**Phụ thuộc:** không. **Loại việc:** quyết định + tài liệu, gần như không đụng code.
**Chặn:** phase 05, 07, 08.

## Vấn đề đang giải

Bốn hệ phân cấp chạy song song và không khớp nhau:

| Hệ | Giá trị | Nơi định nghĩa |
|---|---|---|
| Band xếp lớp | 3: pre_a1 / a1 / a2 | `BANDS`, `app/services/placement_service.py:23` |
| Enum CEFR | 4: + b1 | `app/models/enums.py:9`, `CEFR_ORDER` |
| `cefr_target` của bài | 4: pre_a1(4) a1(10) a2(24) b1(24) | 62 file YAML |
| Phase | 5: foundation/daily/office/it_english/reading | `Phase` enum |

Hệ quả: 24 bài nhắm B1 nhưng bài test không xếp ai vào B1 được; `ENTRY_LESSON` còn 3 mục viết từ hồi
giáo trình 13 bài; UI trình bày phase như 5 giai đoạn tuần tự trong khi DAG coi chúng là track song song.

## Quyết định kiến trúc

**Level = trục dọc tuần tự (quyết định thứ tự học). Phase = nhãn chủ đề (không quyết định thứ tự).**

Với đối tượng mất gốc, tuần tự rõ ràng quan trọng hơn tự do chọn track. `phase` vẫn giữ nguyên trong
schema và DB — chỉ đổi vai trò trên UI và trong tính toán lộ trình.

## Bảng ánh xạ 62 bài → 4 level (bản nháp, phase này chốt lại)

| Level | CEFR / KNLNN | Bài hiện có | Số bài |
|---|---|---|---|
| L1 | Pre-A1 / dưới Bậc 1 | F01–F04 | 4 |
| L2 | A1 / Bậc 1 | F05–F08, D01–D04, CP-F, CP-D | 10 |
| L3 | A2 / Bậc 2 | F09–F17, O01–O08, I01–I04, R01–R02, CP-O | 24 |
| L4 | B1 / Bậc 3 | F18–F20, I05–I15, R03–R10, CP-I, CP-R | 24 |

**Vấn đề lộ ra ngay:** L1 có 4 bài, L2 có 10 bài, rồi nhảy sang L3 24 bài. Với người mất gốc đây là vách
đứng. Đối chiếu bên ngoài: VUS iTalk 60 bài/level; Ms Hoa 5 level / 68 buổi ≈ 14 buổi/level.
→ Mục tiêu đề xuất: **L1 ≈ 12 bài, L2 ≈ 14 bài**, tức cần thêm ~12 bài. Đó là phase 07.

**Bất nhất cần sửa luôn:** `CP-F` gắn `cefr_target: a1` nhưng nó chốt cả F18–F20 (b1). Checkpoint phải
mang cefr của bài cao nhất mà nó chốt.

## Việc phải làm

### 1. Chốt bảng ánh xạ level

Sửa `cefr_target` của các checkpoint cho khớp bài chúng chốt. Không đổi `cefr_target` của bài thường ở
phase này (đổi nội dung là phase 06/07).

Riêng nhãn `pre_a1` của F01–F04: audit CEFR ngày 20/07 xác nhận **thang ngữ âm của CEFR Companion Volume
2020 (tr.135) không có bậc Pre-A1** — nhãn này đang mô tả *thứ tự dạy*, không phải *bậc năng lực*.
Giữ nhãn (nó đúng về sư phạm) nhưng ghi rõ trong `docs/khung-level.md` rằng L1 là "bậc khởi động", không
tuyên bố tương đương KNLNN.

### 2. Viết `docs/khung-level.md`

Nội dung bắt buộc, mỗi level một mục:

- Tên level tiếng Việt + tương ứng CEFR + tương ứng bậc KNLNN (trừ L1)
- Danh sách bài, số bài, số tuần ước tính
- **Tuyên bố đầu ra cho từng kỹ năng** — 4 câu, viết theo mẫu descriptor KNLNN, phải quan sát được.
  Ví dụ mẫu cho L2 (A1):
  - *Nghe:* nghe được câu chỉ dẫn công việc rất chậm, rõ, có nghỉ giữa các cụm.
  - *Nói:* nói được cụm câu rời về bản thân và công việc; người nghe quen giọng Việt hiểu được.
  - *Đọc:* đọc được tin nhắn và email rất ngắn, tìm được tên người và mốc thời gian.
  - *Viết:* viết được câu đơn và tin nhắn ngắn theo khung cho sẵn.
- Điều kiện lên level (nối sang phase 08)

### 3. Cập nhật `ENTRY_LESSON`

`app/services/placement_service.py:24` hiện là `{PRE_A1: F01, A1: F05, A2: D01}`. Thiếu B1, và A2→D01
làm học viên bỏ qua F09–F17. Điểm vào mới phải bám bảng ánh xạ ở trên (bài đầu của mỗi level).

### 4. Đổi cách UI trình bày

`app/services/learning_path_service.py:22-23` liệt kê phase theo thứ tự cố định. Đổi sang gom bài theo
`level`, hiển thị `phase` như nhãn chủ đề trên thẻ bài.

## File đụng tới

| File | Việc |
|---|---|
| `docs/khung-level.md` | **Tạo mới** — tài liệu chính của phase này |
| `app/services/placement_service.py` | `ENTRY_LESSON` 3 → 4 mục, bám bảng ánh xạ |
| `app/services/learning_path_service.py` | Gom theo level thay vì phase |
| `seeds/content/*/CP-*.yaml` | Sửa `cefr_target` của 5 checkpoint |
| `README.md` | Mục "Nội dung" nêu 4 level thay vì 5 phase |

## Nghiệm thu

1. `docs/khung-level.md` có đủ 4 level × 4 tuyên bố đầu ra, mỗi tuyên bố quan sát được (có động từ hành
   vi, không dùng "hiểu được cơ bản" kiểu chung chung).
2. Mọi bài trong 62 bài thuộc đúng một level, không bài nào rơi ra ngoài.
3. `ENTRY_LESSON` có đủ 4 band và mỗi giá trị là mã bài có thật.
4. `make validate` xanh.
5. Đối chiếu được: mỗi level (trừ L1) chỉ rõ tương ứng bậc mấy trong KNLNN 6 bậc.

## Rủi ro

Đổi vai trò phase → level có thể làm hỏng DAG tiên quyết nếu bài ở level cao lại là tiên quyết của bài ở
level thấp. **Phải chạy kiểm tra chéo:** với mọi cạnh `prerequisites`, level của bài tiên quyết phải ≤
level của bài phụ thuộc. Nếu có vi phạm, đó là dấu hiệu bảng ánh xạ sai chứ không phải DAG sai.
