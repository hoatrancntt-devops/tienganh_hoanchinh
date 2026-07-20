# Cốt truyện xuyên suốt cho 62 bài

Trạng thái: XONG toàn bộ nội dung (62 bài + màn mở chương). Chờ deploy lên VPS.

## Vấn đề

Người học vào F01 gặp ngay câu hỏi nghe không có gì để nghe và không có bối cảnh. Sâu hơn:
62 bài không có nhân vật chung, không có mạch truyện, không có lý do nào để câu tiếng Anh
trong bài xuất hiện. Học xong không nhớ vì không có chỗ để móc trí nhớ vào.

## Phase 1 — Sửa mạch nghe (XONG)

- `app/seeds/schema.py` — `Listening.context_vi`: bối cảnh tiếng Việt trước khi phát.
- `app/seeds/loader.py` — đưa `context_vi` vào `activity.config`.
- `app/web/routes.py` — truyền `config` + đường dẫn audio của activity nghe ra template.
- `app/seeds/generate_audio.py` — sinh wav cho mọi activity `listen` từ `transcript_en`.
- `app/web/static/js/player.js` — chèn bước "🎧 Nghe đoạn hội thoại" (bối cảnh + nút phát +
  lời thoại giấu trong accordion) trước các câu hỏi nghe; câu hỏi có nút "Nghe lại đoạn".

Acceptance: mở F01 → bước 2 là màn nghe có tiếng; câu hỏi 3:13/3:30 trả lời được bằng tai.

## Phase 2 — Story bible (CHỜ DUYỆT)

### Bối cảnh

Bạn là **fresher IT support vừa vào Vertex Solutions** — công ty phần mềm Việt Nam làm
outsourcing cho khách hàng nước ngoài. Toàn bộ 62 bài là **6 tháng đầu đi làm** của bạn.

### Dàn nhân vật (cố định, tái xuất hiện)

| Tên | Vai | Chức năng trong việc học |
|---|---|---|
| **Bạn** | Fresher IT support, mới vào | Người học nhập vai — mọi drill nói là lời của bạn |
| **Minh** | Đồng nghiệp cùng team, vào trước 1 năm | Người an toàn để tập nói sai; giọng Việt-Anh dễ nghe |
| **Linh** | Team lead người Việt | Giao việc, review, hỏi tiến độ — nguồn câu hỏi công việc |
| **David Carter** | Engineering manager phía khách hàng, người Mỹ | Nói nhanh, nuốt âm — nguồn "nghe khó" thật |
| **Priya Nair** | DevOps ở Singapore, giọng Ấn | Đa dạng giọng; phối hợp deploy và trực ca |
| **Emma Brooks** | Kế toán, người dùng cuối không rành kỹ thuật | Nguồn ticket helpdesk; buộc bạn giải thích đơn giản |

### Tuyến truyện theo phase

**Chương 1 — Foundation (F01-F20, CP-F): "Tuần đầu tiên"**
Ngày đầu đến công ty, Minh dẫn đi, Linh giao việc nhẹ. Xung đột: bạn nói mà người ta không
hiểu. Mỗi bài là **một khoảnh khắc hiểu lầm cụ thể** — F01 nhầm 3:30 với 3:13 nên lỡ họp;
F14 nói "ship" khách nghe "sheep"; F20 gọi điện bị hỏi lại ba lần. Khép chương: CP-F là buổi
bạn tự giới thiệu trước cả team, có David dự qua call.

**Chương 2 — Daily (D01-D04, CP-D): "Hoà nhập"**
Priya sang Việt Nam công tác một tuần. Bạn được giao đưa đón, ăn trưa, small talk ở pantry.
Áp lực thấp, quan hệ ấm lên. Khép chương: bữa tiễn Priya ra sân bay.

**Chương 3 — Office (O01-O08, CP-O): "Thành viên thật của team"**
Bạn được đưa vào dự án của David. Standup thật, báo tiến độ thật, xin nghỉ, dời họp, nhắn
Slack. Khép chương: bạn chủ trì một standup khi Linh nghỉ.

**Chương 4 — IT English (I01-I15, CP-I): "Sự cố"**
Mạch chính, kịch tính nhất: **hệ thống của khách hàng sập lúc 2 giờ sáng thứ Sáu.**
- I01-I05: Emma báo không đăng nhập được → bạn nhận ticket, hỏi chẩn đoán, hướng dẫn, giải thích.
- I06-I09: sự cố lan rộng → cập nhật incident cho David, bàn giao ca cho Priya, standup khủng hoảng, review bản vá.
- I10-I13: truy nguyên nhân qua mạng / cloud / quyền truy cập / database và backup.
- I14-I15: họp với nhà cung cấp, viết email thông báo cho khách hàng.
Khép chương: CP-I là cuộc gọi tổng kết với David.

**Chương 5 — Reading (R01-R10, CP-R): "Tự xoay sở bằng chữ"**
Tất cả tài liệu bạn đọc đều là **hiện vật của chính sự cố ở chương 4**: email của David, log
đêm hôm đó, ticket của Emma, security advisory về lỗ hổng gây ra sự cố, và cuối cùng là bản
postmortem. Khép vòng: R10 bạn đọc lại chính câu chuyện mình vừa sống.

### Nguyên tắc viết

1. **Mỗi bài phải trả lời được "vì sao hôm nay bạn cần câu này"** — nếu không, bài đó chưa đúng.
2. **`dialogue` và `listening_snippet` cùng một cảnh**, không phải hai văn bản rời như hiện nay.
3. Nhân vật nói đúng tính cách: David ngắn và nhanh, Emma vòng vo không thuật ngữ, Priya lịch sự và chính xác.
4. Mục tiêu ngôn ngữ không đổi. Cốt truyện phục vụ mục tiêu, không lấn át. Từ vựng, IPA,
   `focus_phonemes`, `unlock_condition` giữ nguyên.
5. Bối cảnh viết bằng tiếng Việt, hội thoại bằng tiếng Anh đúng trình độ CEFR của bài.

## Phase 2b — Màn mở chương (XONG)

- `seeds/story/chapters.yaml` — dàn nhân vật + 5 chương. Nội dung tĩnh, không state người học.
- `app/services/story_service.py` — đọc YAML, cache bằng lru_cache. Không cần bảng DB / migration.
- `app/web/routes.py` — chỉ trả `chapter` ở bài đầu tiên của phase.
- `player.js` — bước `__chapter` đứng trước mọi bước khác.

## Lỗi phát hiện khi soát (đã sửa)

- `.spk` là vòng tròn 20px cho nhãn "A"/"B"; tên thật tràn ra ngoài → đổi thành pill co giãn.
- Bài Reading dùng `dialogue.turns` làm thân tài liệu (log, màn hình lỗi), không phải hội thoại.
  Speaker `A` để nguyên sẽ dán huy hiệu vô nghĩa lên từng dòng log → xoá nhãn, player bỏ qua khi rỗng.
- R07: đáp án "Mai bàn lại" cho "circle back on Monday"; nhân vật "Huy" không có trong truyện.
- CP-F: "Tám bài Foundation" trong khi phase đã có 20 bài.

## Phase 3-7 — Viết lại nội dung (XONG)

Mỗi phase một chương, viết lại `dialogue` + `listening_snippet` (thêm `context_vi`) và
chỉnh `speaking_drills.prompt_vi` cho khớp cảnh.

- Phase 3: Foundation, 21 bài
- Phase 4: Daily, 5 bài
- Phase 5: Office, 9 bài
- Phase 6: IT English, 16 bài
- Phase 7: Reading, 11 bài

Sau mỗi phase: `python -m app.seeds.validate_content` phải xanh.

## Câu hỏi còn treo

- Tên nhân vật "Bạn" có nên đặt tên cụ thể không, hay giữ ngôi thứ hai để người học nhập vai?
- Có cần màn "mở chương" riêng khi người học bước vào phase mới không (hiện chưa có chỗ hiển thị)?
