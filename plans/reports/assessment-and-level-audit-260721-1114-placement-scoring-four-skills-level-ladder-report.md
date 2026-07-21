# Rà soát: chấm điểm xếp lớp, phân tách 4 kỹ năng, và phân cấp Level

Ngày: 2026-07-21 · **Đã đính chính 2026-07-21** (xem mục 2.3)

> **ĐÍNH CHÍNH.** Bản đầu của báo cáo này viết *"Viết bằng 0 ở mọi tầng"*. **Sai.**
> Tính năng **Luyện viết đã tồn tại và đang chạy**: 14 bài trong 3 bộ tại `seeds/writing/WR-*.yaml`,
> chấm bằng luật trong `app/services/writing_service.py`, có route `/learn/write` và **có trong menu
> chính** (`base.html`). Lỗi do grep từ khoá `writing` trong khi route và menu dùng `write`.
>
> Phát biểu đúng: Viết tồn tại như một **bộ luyện tập độc lập**, nhưng **không** nối vào bài học,
> **không** có trong `mastery_weights`, **không** có trong bài xếp lớp, và **không** có tuyên bố
> đầu ra theo level. Mục 2.3 và bảng 2.4 bên dưới đã sửa lại.
Phạm vi: `app/services/placement_service.py`, `seeds/placement/form_{a,b}.yaml`, `seeds/content/**/*.yaml`,
`app/models/enums.py`, `app/services/learning_path_service.py`, `app/web/templates/placement_result.html`
Phương pháp: đọc code + chạy lại công thức chấm bằng số thật của hai form đề. Không suy đoán.

---

## Tóm tắt cho người bận

Ba nghi ngờ của bạn đều đúng, và đều nặng hơn dự đoán:

| Nghi ngờ | Kết luận | Mức độ |
|---|---|---|
| Chấm điểm chưa đúng | **8 lỗi**, trong đó 2 lỗi làm xếp sai tới **2 bậc** | Nghiêm trọng |
| Chưa phân rõ Nghe / Nói / Đọc / Viết | Đọc chỉ là nghe trá hình; Viết có nhưng tách rời lộ trình | Nghiêm trọng |
| Phân cấp Level chưa rõ | **4 hệ phân cấp khác nhau** cùng tồn tại, không khớp nhau | Nghiêm trọng |

Hệ quả gộp lại: bài test **không thể** xếp ai vào B1, dù 24/62 bài học đang nhắm B1. Và lộ trình
**không thể** hứa "nghe nói đọc viết thuần thục" vì hai trong bốn kỹ năng không được đo lúc xếp lớp
và không tính vào tiến độ.

---

## 1. Chấm điểm xếp lớp — 8 lỗi

Công thức hiện tại (`placement_service.py:22-25`):

```
WEIGHTS = {knowledge: 0.30, listening: 0.30, speaking: 0.40}
BANDS   = [(35, Pre-A1), (65, A1), (101, A2)]
điểm câu đúng = 100 * (0.5 + 0.5 * difficulty/5) * (1 - 0.15*replay)
```

### 1.1 Trần điểm 86.8 — không ai chạm tới B1 được (nghiêm trọng)

Chạy lại bằng số thật của form A và form B (giống hệt nhau):

| Trả lời | knowledge | listening | speaking | Tổng | Band |
|---|---|---|---|---|---|
| **Đúng 100% + nói hoàn hảo** | 77.8 | 78.3 | 100 | **86.8** | A2 |
| Đúng 100% + nói 60 | 77.8 | 78.3 | 60 | 70.8 | A2 |
| Đúng 100% + không nói | 77.8 | 78.3 | 0 | 46.8 | A1 |

Nguyên nhân: câu difficulty 1 trả lời đúng chỉ được **60/100**. Form chỉ có một câu difficulty 5 mỗi phần,
nên dù đúng hết, trung bình vẫn kẹt ở ~78.

Hai hệ quả:
- Dải A2 danh nghĩa là 65–101 nhưng thực tế chỉ dùng tới 86.8 — **14 điểm cuối là vùng chết**.
- `BANDS` **không có mục B1**, dù `CEFR_ORDER` (`app/models/assessment.py:76`) có B1 và
  `ENTRY_LESSON` chỉ khai báo 3 bậc. Người đã B1 thật sẽ bị xếp A2 và bắt đầu từ `D01`.

### 1.2 Tụt 2 bậc do hai lần trừ chồng lên nhau (nghiêm trọng)

`placement_service.py:147-160` có ba nhánh hạ bậc chạy nối tiếp mà không loại trừ nhau:

**Ca 1 — micro hỏng / speech service chết:**
knowledge 60, listening 75 → tổng 67.5 → A2
→ hạ vì không chấm được phần nói → A1
→ tổng 67.5 cách mốc 65 chỉ 2.5 điểm nên `near_edge` hạ tiếp → **Pre-A1**

**Ca 2 — giỏi giấy, yếu nói:**
knowledge 90, listening 90, speaking 29 → tổng 65.6 → A2
→ `speaking < 30` phủ quyết → A1
→ `near_edge` (|65.6−65| = 0.6) hạ tiếp → **Pre-A1**

Người nghe hiểu và đọc hiểu ở mức 90/100 bị đẩy về bài `F01` — bài dạy âm /θ/ trong *think*. Đây là kiểu
sai làm học viên bỏ app ngay buổi đầu.

Gốc rễ: `near_edge` được viết cho *điểm gốc* nhưng lại chạy *sau* khi band đã bị hạ vì lý do khác.

### 1.3 Bỏ câu khó thì điểm tăng (lỗ hổng)

`submit()` chỉ lấy trung bình trên **các câu đã trả lời** (`buckets[...].append` chỉ chạy khi có response).
Không trả lời câu nào thì câu đó biến mất khỏi mẫu số.

Trả lời đúng duy nhất câu `V5` (difficulty 5) rồi bỏ 8 câu còn lại → `knowledge = 100`.
Trả lời đúng cả 9 câu → `knowledge = 77.8`.

Người bỏ 8 câu được điểm cao hơn người làm đúng hết.

### 1.4 Công thức `confidence` sai thứ nguyên

```python
self_avg = trung bình choice_index của 3 câu Likert   # thang 0–4
measured_level = CEFR_ORDER.index(band) + 1            # thang 1–4
if abs(self_avg - measured_level * 1.5) >= 2: confidence = "low"
```

`self_avg` là chỉ số lựa chọn Likert, `measured_level * 1.5` là số bậc CEFR nhân 1.5. Hai đại lượng
không cùng đơn vị, phép trừ không có nghĩa. Hệ quả cụ thể:
- Band B1 → `measured_level*1.5 = 6`, `self_avg` tối đa là 4 → **luôn luôn** `low confidence`.
- Band Pre-A1 → ngưỡng 1.5; ai tự đánh giá "Thường xuyên/Luôn luôn" cũng thành `low`.

`confidence = "low"` lại mở quyền thi lại ngay (`can_retake`) và bật nút `can_challenge`. Nên lỗi này
rò rỉ trực tiếp ra hành vi sản phẩm.

### 1.5 `replay_count` do client tự khai, phạt 15%/lần

`REPLAY_PENALTY = 0.15`, nghe 3 lần → mất 45% điểm câu đó. Không phân biệt "nghe lại vì chưa hiểu" với
"nghe lại vì loa chưa bật / audio chưa tải xong". Giá trị gửi từ trình duyệt, server không kiểm chứng.
Phạt cũng áp cho `vocab`/`grammar` — vô hại vì không có audio, nhưng cho thấy luật đang áp bừa theo section.

### 1.6 Bỏ trống câu tự đánh giá bị tính là "Không bao giờ"

`self_answers.append(resp.get("choice_index") or 0)` (dòng 102). `None` → `0` = mức thấp nhất.
Không trả lời khác với "không bao giờ", nhưng code coi là một.

### 1.7 `latency_ms` thu thập nhưng không dùng

Được lưu vào `PlacementResponse` rồi không xuất hiện ở bất kỳ công thức nào. Với bài xếp lớp, thời gian
phản xạ là tín hiệu tốt (đoán mò vs. biết chắc) — hiện đang bỏ phí.

### 1.8 Trọng số nói 0.40 nhưng chỉ có 5 câu nói, và có sàn im lặng cứng

`silent_count >= 3` (trên 5 câu) → ép Pre-A1. Ngưỡng 3/5 cộng với việc phần nói chiếm 40% điểm nghĩa là
một sự cố micro giữa chừng đủ để phá toàn bộ kết quả. Không có cơ chế phân biệt "im lặng vì không nói được"
với "im lặng vì thu âm lỗi".

---

## 2. Bốn kỹ năng chưa được phân tách

### 2.1 Bài test đo 3 trục, không phải 4 kỹ năng

Cả hai form đề có 23 câu, chia đúng như sau:

| Section | Số câu | Kỹ năng thật |
|---|---|---|
| `self` | 3 | Tự đánh giá (không tính điểm) |
| `vocab` | 5 | Từ vựng — đề bài bằng **tiếng Việt** |
| `grammar` | 4 | Ngữ pháp — nhận diện câu đúng |
| `listening` | 6 | **Nghe** |
| `speaking` | 5 | **Nói** |

Không có section `reading`. Không có section `writing`. Màn kết quả
(`placement_result.html:13`) hiển thị đúng ba nhãn: **Nghe / Nói / Từ vựng & ngữ pháp**.

Lưu ý thêm: `vocab` hỏi *nghĩa tiếng Việt của từ tiếng Anh* — đó là kiểm tra từ vựng thụ động, không phải
đọc hiểu. Đọc hiểu là rút thông tin từ một văn bản có ngữ cảnh.

### 2.2 Phase `reading` không dạy đọc — nó dạy nghe hội thoại

62/62 bài dùng **chung một schema**: `vocabulary`, `sentence_patterns`, `dialogue`, `listening_snippet`,
`speaking_drills`, `mini_quiz`. Không có trường nào cho bài đọc.

R01 "Đọc email nội bộ" được soạn thế này (`seeds/content/reading/R01.yaml:58-69`):

```yaml
dialogue:
  turns:
    - {speaker: Linh, en: "Subject: Action required — INC-2291 postmortem", ...}
    - {speaker: Linh, en: "Hi team, as discussed on Friday, ...", ...}
```

Một email bị nhét vào cấu trúc hội thoại có `speaker`, rồi được sinh audio bằng Piper, kèm thêm một
`listening_snippet`. Học viên **nghe** email đó. Câu hỏi đọc hiểu thì viết bằng tiếng Việt và hỏi về
một email *khác* được trích trong đề bài.

Thiếu mọi thứ đặc trưng của kỹ năng đọc: văn bản liền mạch không chia lượt, đọc lướt/đọc quét, suy luận
từ ngữ cảnh, tốc độ đọc, câu hỏi bằng tiếng Anh.

Ở tầng code: `learning_path_service.py:35` khai báo `Phase.READING: ["read", "listen"]`, nhưng không có
loại hoạt động nào sinh ra điểm `read`. Cả 11 file reading đặt `mastery_weights: {quiz: 0.7, listen: 0.3}` —
tức là **điểm "đọc" thực chất là điểm quiz trắc nghiệm tiếng Việt**.

### 2.3 Viết tồn tại nhưng tách rời khỏi lộ trình *(đã đính chính)*

| Tầng | Trạng thái |
|---|---|
| Bộ luyện viết độc lập | ✅ **Có** — 14 bài / 3 bộ, `/learn/write`, có trong menu chính |
| Bộ chấm | ✅ **Có** — `writing_service.py`, chấm bằng luật, không cần AI |
| `ActivityKind` (`enums.py:39`) | ❌ `LISTEN, SHADOW, SPEAK, VOCAB, READ, QUIZ` — không có `WRITE` |
| Schema bài học | ❌ Không có trường bài viết |
| `mastery_weights` | ❌ Chỉ dùng `speak`, `quiz`, `listen` |
| Bài xếp lớp | ❌ Không có section viết |
| Tuyên bố đầu ra theo level | ❌ Không có |

Nói cách khác: học viên **luyện viết được**, nhưng việc đó không tính vào tiến độ, không ảnh hưởng
mở khoá bài, và không được đo lúc xếp lớp. Nó là một hòn đảo cạnh lộ trình, không nằm trong lộ trình.

### 2.4 Bảng tổng kết độ phủ 4 kỹ năng *(đã đính chính)*

| Kỹ năng | Trong bài test | Trong nội dung | Tính vào mastery |
|---|---|---|---|
| **Nghe** | ✅ 6 câu | ✅ `listening_snippet` mọi bài | ✅ |
| **Nói** | ✅ 5 câu (3 dạng) | ✅ `speaking_drills` + chấm phát âm local | ✅ |
| **Đọc** | ❌ không có | ⚠️ 11 bài nhưng là hội thoại có audio | ⚠️ thực chất là điểm quiz |
| **Viết** | ❌ không có | ⚠️ 14 bài, nhưng tách rời khỏi bài học | ❌ không |

---

## 3. Lộ trình đầu ra chưa tuyên bố được

- `README.md` hứa "1–3 tháng giao tiếp cơ bản, 3–6 tháng đọc hiểu tài liệu công việc" — không có mốc
  cho nói/nghe/viết riêng, không có tiêu chí đo được.
- `estimated_weeks_to_goal` là hằng số cứng theo band: `{Pre-A1: 14, A1: 10, A2: 7}` tuần
  (`placement_service.py:222`). Không tính tốc độ học thật, không tính số phút/ngày học viên đã chọn ở
  onboarding, không cập nhật theo tiến độ.
- Không tồn tại khái niệm "hoàn thành lộ trình". Không có bài kiểm tra đầu ra, không có tuyên bố
  "sau khi xong bạn sẽ làm được X".

Kết luận thẳng: **chưa thể hứa "nghe nói đọc viết thuần thục"**. Hứa được nghe và nói. Đọc thì đang là
nghe. Viết thì chưa tồn tại.

---

## 4. Phân cấp Level — bốn hệ đang chạy song song

| Hệ | Giá trị | Nơi định nghĩa |
|---|---|---|
| Band kết quả xếp lớp | 3: Pre-A1 / A1 / A2 | `BANDS`, `placement_service.py:23` |
| Enum CEFR | 4: pre_a1 / a1 / a2 / **b1** | `enums.py:9`, `CEFR_ORDER` |
| `cefr_target` của bài | 4: pre_a1 (4) / a1 (10) / a2 (24) / **b1 (24)** | 62 file YAML |
| Phase nội dung | 5: foundation / daily / office / it_english / reading | `Phase` enum |

Bốn hệ này không ánh xạ lẫn nhau. Cụ thể:

- **24 bài nhắm B1 nhưng bài test không bao giờ xếp ai vào B1.** Ai đã B1 vẫn phải vào `D01`.
- `ENTRY_LESSON` chỉ có 3 mục `{Pre-A1: F01, A1: F05, A2: D01}` — viết từ hồi giáo trình còn 13 bài,
  nay đã 62 bài. Học viên A2 vào `D01` là bỏ qua toàn bộ Foundation F05–F20.
- Phase là **track song song** (audit ngày 20/07 đã xác nhận), nhưng giao diện trình bày như 5 giai đoạn
  nối tiếp. Học viên hiểu sai thứ tự.
- Nhãn `pre_a1` cho F01–F04 **không có căn cứ trong chuẩn**: thang ngữ âm của CEFR Companion Volume 2020
  (tr.135) không có bậc Pre-A1 (đã kiểm bản gốc, xem
  `plans/reports/primary-source-cefr-descriptors-260720-2333-official-companion-volume-report.md`).
  Nhãn đó đang mô tả *thứ tự dạy*, không phải *bậc năng lực*.

### 4.1 Đối chiếu tài liệu bên ngoài

**Ms Hoa Giao Tiếp** — 5 level, Pre-A1 → B1, tổng 8 tháng / 68 buổi. Tuyên bố phát triển **đủ bốn kỹ năng
nghe–nói–đọc–viết**, trọng tâm phản xạ giao tiếp. Hai nhánh: E-survive (mất gốc) và E-challenge (nâng cao).

**VUS / Hội Việt Mỹ (iTalk)** — 4 level, A1 → B1+. **60 bài mỗi level**. Mini-test sau mỗi 10 chủ đề,
bài kiểm tra tổng hợp cuối level để học viên thấy tiến bộ. 365+ chủ đề, lộ trình cá nhân hoá.

**Anh ngữ Dương Minh** — trang chủ nêu tiếng Anh giao tiếp + TOEIC/IELTS "cải thiện nghe, nói, đọc, viết"
nhưng **không công bố khung level chi tiết trên web công khai**. Không dùng làm tham chiếu được.

**Khung có thẩm quyền hơn cả ba trung tâm:** Khung năng lực ngoại ngữ 6 bậc dùng cho Việt Nam
(Thông tư 01/2014/TT-BGDĐT) — 3 cấp độ, 6 bậc, tương thích A1–C2 của CEFR, và **có mô tả riêng cho từng
kỹ năng nghe/nói/đọc/viết ở mỗi bậc**. Đây là văn bản pháp quy, dùng làm căn cứ xây chương trình và
kiểm tra đánh giá. Nếu cần một khung để bảo vệ trước học viên hoặc doanh nghiệp, đây là khung nên bám.

### 4.2 Ba điều app đang thiếu mà cả Ms Hoa lẫn VUS đều có

1. **Mỗi level có số bài rõ ràng và cố định.** VUS: 60 bài/level. App: level không gắn với số bài nào.
2. **Kiểm tra giữa chặng và kiểm tra kết thúc level.** VUS: mini-test mỗi 10 chủ đề + bài tổng hợp.
   App có 5 checkpoint nhưng chúng gắn với *phase*, không gắn với *level*, và không có bài kiểm tra đầu ra.
3. **Tuyên bố đầu ra theo bốn kỹ năng cho từng level.** Cả hai trung tâm đều nêu. App không có.

---

## 5. Đề xuất — ba khối việc, độc lập nhau

### Khối A — Sửa chấm điểm (nhỏ, không đụng nội dung)

1. Gộp ba nhánh hạ bậc thành **một** lần điều chỉnh duy nhất, tối đa 1 bậc.
2. Tính điểm trên **toàn bộ câu của section**, câu không trả lời = 0 điểm.
3. Thêm band **B1** vào `BANDS`, và giãn thang điểm (câu dễ đúng nên được ~85, không phải 60) để trần
   điểm chạm được B1.
4. Cập nhật `ENTRY_LESSON` cho giáo trình 62 bài.
5. Bỏ công thức `confidence` hiện tại, thay bằng luật rõ ràng (thiếu dữ liệu nói / lệch lớn giữa các trục).
6. Hạ `REPLAY_PENALTY`, chỉ áp cho `listening`, và chặn trần số lần phạt.
7. Sửa `choice_index or 0` → phân biệt `None` với `0`.

Ước lượng: 1 file, ~120 dòng thay đổi, cần bổ sung test cho từng ca xếp band.

### Khối B — Phân tách 4 kỹ năng (vừa, đụng schema + nội dung)

1. Thêm `ActivityKind.WRITE` và trường `writing_task` vào schema bài học.
   Chấm được **không cần AI**: điền chỗ trống, sắp xếp câu, sửa lỗi, viết email theo khung cho sẵn
   (so khớp mẫu + từ khoá bắt buộc), giống cách `accept_patterns` đang làm ở phần nói.
2. Thêm trường `reading_passage` (văn bản liền, **không sinh audio**, câu hỏi bằng tiếng Anh) và tách
   khỏi `dialogue`. Chuyển R01–R10 sang dạng này.
3. Thêm section `reading` và `writing` vào form đề xếp lớp → **5 trục điểm**:
   Nghe / Nói / Đọc / Viết / Từ vựng & ngữ pháp.
4. Đổi màn kết quả sang 5 trục, mỗi trục có band riêng (học viên thật hiếm khi đều bốn kỹ năng).

### Khối C — Dựng lại thang Level (vừa, chủ yếu là quyết định + tài liệu)

1. Chốt **một** thang duy nhất, bám KNLNN 6 bậc / CEFR: Pre-A1 → A1 → A2 → B1 (4 level).
2. Ánh xạ 62 bài vào 4 level đó, mỗi level nêu rõ: gồm bài nào, bao nhiêu bài, bao nhiêu tuần.
3. Viết **tuyên bố đầu ra 4 kỹ năng cho mỗi level** bằng tiếng Việt, theo mẫu descriptor của KNLNN.
4. Thêm **bài kiểm tra kết thúc level** (khác với checkpoint theo phase hiện có).
5. Đổi `estimated_weeks_to_goal` từ hằng số sang tính theo số bài còn lại × phút/bài ÷ phút/ngày đã chọn.

---

## Câu hỏi cần bạn quyết

1. **Đối tượng thật là ai?** "Mất gốc hoàn toàn" hay "đã có A2, cần tiếng Anh IT"? Hiện giáo trình có
   4 bài pre-A1 rồi nhảy sang 48 bài A2/B1 — dốc cho nhóm đầu, thừa cho nhóm sau. Câu hỏi này quyết định
   toàn bộ Khối C và đã tồn đọng từ audit ngày 20/07.
2. **Có thật sự cần dạy Viết không?** Thêm Viết là khối việc lớn nhất (schema + 62 bài + chấm điểm + UI).
   Nếu mục tiêu là "nói được với đồng nghiệp" thì Viết có thể chỉ cần ở mức viết email ngắn trong phase
   Office/IT, không cần trải đều mọi bài.
3. **Level nên có bao nhiêu bậc?** 4 (Pre-A1→B1, khớp nội dung hiện có) hay 5 (như Ms Hoa, tách A2 thành
   A2/A2+)?
4. **Xếp lớp nên ra một band hay bốn band theo kỹ năng?** Bốn band chính xác hơn nhưng phải thiết kế lại
   cách chọn bài vào (hiện `ENTRY_LESSON` chỉ nhận một band).

## Nguồn

- [Thông tư 01/2014/TT-BGDĐT — Khung năng lực ngoại ngữ 6 bậc dùng cho Việt Nam](https://thuvienphapluat.vn/van-ban/Giao-duc/Thong-tu-01-2014-TT-BGDDT-Khung-nang-luc-ngoai-ngu-6-bac-Viet-Nam-220349.aspx)
- [Ms Hoa Giao Tiếp — lộ trình từ mất gốc đến thành thạo](https://mshoagiaotiep.com/tai-lieu-tieng-anh-giao-tiep/lo-trinh-hoc-giao-tiep-tieng-anh-2025-ndash-tu-mat-goc-den-thanh-thao-nd501331.html)
- [Ms Hoa Giao Tiếp — khoá học cho người mới bắt đầu](https://mshoagiaotiep.com/khoa-hoc-tai-ms-hoa-giao-tiep/khoa-hoc-beginner-xay-goc-tieng-anh-danh-cho-nguoi-moi-bat-dau-nd497848.html)
- [VUS — khoá tiếng Anh giao tiếp cho người đi làm (iTalk)](https://vus.edu.vn/blog-vus/khoa-hoc-tieng-anh-giao-tiep-cho-nguoi-di-lam)
- [Ngoại ngữ Dương Minh](https://duongminh.edu.vn/)
- CEFR Companion Volume 2020 — đã tải bản gốc, trích dẫn trong
  `plans/reports/primary-source-cefr-descriptors-260720-2333-official-companion-volume-report.md`
