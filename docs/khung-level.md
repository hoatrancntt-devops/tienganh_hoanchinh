# Khung level English@Work

Ngày cập nhật: 2026-07-21 · Nguồn sự thật: `cefr_target` trong `seeds/content/**/*.yaml`

## Nguyên tắc: level là trục dọc, phase là nhãn chủ đề

Trước bản này, app có bốn cách phân cấp chạy song song và không khớp nhau (band xếp lớp 3 bậc,
enum CEFR 4 bậc, `cefr_target` 4 bậc, `phase` 5 nhóm). Từ nay:

- **Level = `cefr_target`.** Quyết định thứ tự học và điểm vào sau khi xếp lớp. Bốn bậc.
- **Phase = chủ đề.** `foundation` / `daily` / `office` / `it_english` / `reading` chỉ nói bài đó
  nói về cái gì, **không** quyết định thứ tự.

Vì thế một phase trải qua nhiều level: `foundation` có bài ở cả bốn bậc, `reading` có bài ở hai bậc.
Đó là chủ ý, không phải lỗi.

**Bất biến bắt buộc:** không cạnh tiên quyết nào đi từ bậc cao xuống bậc thấp. Cổng
`make validate` kiểm tra bằng `check_level_order()` — bài dễ bị khoá sau bài khó là lỗi chặn publish.

## Đối chiếu khung ngoài

| Level app | CEFR | KNLNN 6 bậc (TT 01/2014/TT-BGDĐT) |
|---|---|---|
| L1 | Pre-A1 | *không có bậc tương ứng* |
| L2 | A1 | Bậc 1 |
| L3 | A2 | Bậc 2 |
| L4 | B1 | Bậc 3 |

**L1 cố ý không tuyên bố tương đương KNLNN.** Đây là bậc khởi động dạy ngữ âm thuần. Thang ngữ âm của
CEFR Companion Volume 2020 (tr.135) không có bậc Pre-A1, nên không có descriptor chính thức nào để bám.
Nhãn `pre_a1` ở đây mô tả **thứ tự dạy**, không phải **bậc năng lực**.

Tham chiếu thị trường: Ms Hoa 5 level Pre-A1→B1 trong 8 tháng / 68 buổi; VUS iTalk 4 level A1→B1+ với
60 bài mỗi level. App này 4 level / 66 bài — ít bài hơn đáng kể, xem mục "Giới hạn đã biết".

---

## L1 — Bậc khởi động (Pre-A1)

**8 bài:** S01 S02 S03 S04 · F01 F02 F03 F04 · **~3 tuần**

Bốn bài sinh tồn trước: bảng chữ cái và đánh vần tên, số đếm và cặp -teen/-ty, giờ và thứ,
ba câu cứu hộ khi chưa hiểu. Rồi bốn âm mà tiếng Việt không có hoặc hay nuốt: /θ/–/ð/,
âm cuối /s/–/z/, âm cuối /t/–/d/, cụm phụ âm cuối.

| Kỹ năng | Đầu ra |
|---|---|
| Nghe | Phân biệt được cặp tối thiểu chứa các âm đã học (*think*/*sink*, *thirty*/*thirteen*) khi nghe chậm. |
| Nói | Phát âm được /θ/ /ð/ và giữ được âm cuối /s/ /z/ /t/ /d/ ở mức người nghe phân biệt được. |
| Đọc | Đọc được đoạn chat công việc rất ngắn (26–35 từ), tìm được giờ và tên trong đó. |
| Viết | Điền đúng từ đã học vào chỗ trống trong câu cho sẵn. |

**Lên L2 khi:** đạt ≥75 mastery cả tám bài.

---

## L2 — Sơ cấp (A1 · KNLNN Bậc 1)

**10 bài:** F05 F06 F07 F08 CP-F · D01 D02 D03 D04 CP-D · **~4 tuần**

Trọng âm từ, ba động từ lõi (be/have/do), câu hỏi Wh-, câu hỏi lại khi chưa hiểu. Rồi bốn tình huống
đời thường: chào và giới thiệu, small talk ở pantry, gọi món, đi lại.

| Kỹ năng | Đầu ra |
|---|---|
| Nghe | Nghe được câu chào hỏi và chỉ dẫn ngắn khi người nói nói chậm và rõ; nhận ra khi mình chưa hiểu. |
| Nói | Giới thiệu được bản thân và đồng nghiệp; hỏi và đáp câu Wh- đơn giản; **nói được câu hỏi lại** thay vì im lặng. |
| Đọc | Đọc được chat và email công việc ngắn (32–48 từ), rút ra được việc phải làm và mốc thời gian. |
| Viết | Điền từ vào câu, và sắp xếp được 3–4 câu thành một tin nhắn/email đúng thứ tự. |

**Lên L3 khi:** qua checkpoint CP-F (chốt F01–F08) và CP-D (chốt D01–D04).

> CP-F chỉ chốt F01–F08. Trước bản này nó chốt cả F01–F20, khiến bài giao tiếp đầu tiên (D01, bậc A1)
> bị khoá sau 20 bài trong đó có cả bài B1.

---

## L3 — Sơ trung cấp (A2 · KNLNN Bậc 2)

**24 bài:** F09–F17 · O01–O08 CP-O · I01–I04 · R01 R02 · **~8 tuần**

Ngữ âm nâng cao (nối âm, schwa, ngữ điệu câu hỏi, cặp âm dễ nhầm). Toàn bộ tiếng Anh công sở:
standup, xin nghỉ phép, báo tiến độ, đặt lịch họp, xin giúp đỡ. Bắt đầu tiếng Anh IT: báo sự cố,
nhận ticket, hướng dẫn khắc phục.

| Kỹ năng | Đầu ra |
|---|---|
| Nghe | Nghe đủ để xử lý tình huống công việc cụ thể khi người nói nói rõ; bắt được số, ngày, giờ không nhầm. |
| Nói | Tham gia được hội thoại ngắn có cấu trúc ở công sở (standup, xin nghỉ, báo tiến độ) — người đối thoại có thể phải hỗ trợ đôi chỗ. |
| Đọc | Đọc được email, chat, ticket và thông báo lỗi (46–62 từ), xác định được ai phải làm gì trước khi nào. |
| Viết | Sửa được lỗi ngữ pháp thường gặp, và viết được email công việc 3–4 câu: báo sự cố, xin nghỉ, báo tiến độ, hỏi làm rõ. |

**Lên L4 khi:** qua CP-O.

---

## L4 — Trung cấp (B1 · KNLNN Bậc 3)

**24 bài:** F18–F20 · I05–I15 CP-I · R03–R10 CP-R · **~10 tuần**

Nhịp câu, ngữ điệu lịch sự, nói rõ trên điện thoại. Toàn bộ tiếng Anh IT chuyên sâu: giải thích sự cố
cho người không rành, bàn giao ca, standup, review code, mạng, cloud, bảo mật, database, họp với
khách hàng. Đọc tài liệu kỹ thuật thật: release notes, README, ticket, log, API docs, postmortem.

| Kỹ năng | Đầu ra |
|---|---|
| Nghe | Nghe được thông tin công việc trực tiếp trong họp và call, nắm cả ý chính lẫn chi tiết cụ thể. |
| Nói | **Giải thích được vì sao một thứ đang hỏng** — trao đổi, kiểm chứng, xác nhận thông tin trong tình huống không theo kịch bản. |
| Đọc | Đọc được tài liệu kỹ thuật thật — release notes, README, ticket, log, API docs, security advisory, postmortem — và rút ra hành động cần làm. |
| Viết | Viết được email và thông báo kỹ thuật 4–6 câu: cập nhật sự cố, bàn giao ca, thông báo bảo trì, tóm tắt postmortem. |

Descriptor B1 "oral interaction" của CEFR Companion Volume 2020 (tr.72) ghi đúng chữ *"explain why
something is a problem"* — đó chính là nội dung I05 và cụm I05–I15. Đây là chỗ nhãn CEFR của app khớp
chuẩn gần như nguyên văn.

---

## Điểm vào sau khi xếp lớp

| Band | Bài vào | Vì sao |
|---|---|---|
| Pre-A1 | S01 | Bài đầu của L1 |
| A1 | F05 | Bài đầu của L2 |
| A2 | F09 | Bài đầu của L3 |
| B1 | F18 | Bài đầu của L4 |

Định nghĩa trong `app/services/placement_scoring.py` (`ENTRY_LESSON`). Trước bản này bảng chỉ có 3 mục
và band A2 vào thẳng `D01` — bỏ qua toàn bộ F09–F17.

## Bài xếp lớp đo gì

26 câu, ~18 phút. **Bốn trục kỹ năng** (Nghe / Nói / Đọc / Viết) cộng một trục phụ từ vựng–ngữ pháp.
Kết quả ra **một band chung** để chọn điểm vào, kèm biểu đồ bốn trục để học viên thấy mình lệch ở đâu.

Trọng số: nói 0.30 · nghe 0.25 · đọc 0.20 · viết 0.15 · từ vựng–ngữ pháp 0.10.
Định nghĩa ở `app/services/placement_scoring.py`.

## Độ phủ bốn kỹ năng

**66/66 bài** có đủ Nghe · Nói · Đọc · Viết, cả bốn bậc. Tuyên bố đầu ra ở trên là thật và kiểm
chứng được — cổng `make test` chạy trên chính giáo trình này và bắt lỗi nếu đáp án mẫu không qua nổi
bộ chấm của nó, hoặc bài đọc dài quá trần của bậc.

| | Bài đọc | Bài viết |
|---|---|---|
| Dạng | 30 chat · 11 doc · 9 email · 6 ticket · 4 announcement · 2 log | 34 email/note có khung · 14 sửa lỗi · 9 điền chỗ trống · 5 sắp thứ tự |
| Trần độ dài | pre-A1 60 từ · A1 90 · A2 130 · B1 200 | — |

Bài đọc **không sinh audio** — có test khoá điều đó ở cả hai đầu (schema và bộ sinh tiếng). Bài đọc
mà nghe được thì học viên sẽ nghe thay vì đọc, và kỹ năng đọc lặng lẽ biến mất.

## Đường cong đòi hỏi

Ngưỡng để hoàn thành một bài **tăng dần theo bậc**, không phẳng:

| Bậc | Bài thường | Checkpoint | Vì sao |
|---|---|---|---|
| L1 Pre-A1 | 70 | 72 | Người mất gốc cần đà, không cần chuẩn xác |
| L2 A1 | 73 | 75 | |
| L3 A2 | 76 | 78 | |
| L4 B1 | 80 | 82 | Chuẩn bị cho call thật với khách nước ngoài |

Trước bản này đường cong đi **ngược**: F01–F04 (bậc Pre-A1, tuần đầu) có ngưỡng 78 — cao nhất
giáo trình — còn CP-I và CP-R (checkpoint B1, bài chốt cuối) chỉ 70. Giáo trình đòi hỏi nhiều
nhất ở người biết ít nhất.

**Căn cứ hạ ngưỡng ở bậc thấp** — CEFR Companion Volume 2020, tr.135, bậc A2:

> *"Systematic mispronunciation of phonemes does not hinder intelligibility, provided the
> interlocutor makes an effort to understand specific sounds."*

Tới tận A2, chuẩn châu Âu đo bằng **người nghe có hiểu không**, không đo độ giống người bản xứ.
App từng khắt khe hơn chuẩn ở đúng bậc mà chuẩn bảo hãy khoan dung — và đó là bậc người học dễ
bỏ cuộc nhất.

**Cái không hạ:** `min_speaking_attempts` giữ nguyên 4 (checkpoint 6). Đó là cổng đòi **nỗ lực**,
không đòi hoàn hảo — học viên vẫn phải mở miệng đủ số lần và vẫn nhận phản hồi phát âm từng lần.
Hạ ngưỡng *điểm* mà giữ cổng *số lần* là cách giữ được việc luyện tập mà bỏ được việc chặn đường.

Ngưỡng riêng từng kỹ năng ở checkpoint cũng tăng theo (nói: 62 → 66 → 70). Trục phụ được phép
thấp hơn: CP-R là checkpoint đọc, nghe chỉ chiếm 10% điểm nên ngưỡng nghe ở đó thấp là đúng.

`make test` khoá cả ba bất biến này.

## Giới hạn đã biết

1. **Nền L1 vẫn mỏng hơn mục tiêu.** Đã tăng 4 → 8 bài (thêm S01–S04), nhưng kế hoạch nhắm 12 bài;
   L2 chưa dày thêm. VUS 60 bài/level, Ms Hoa ~14 buổi/level. Phase 07 của
   `plans/260721-1114-bon-ky-nang-va-thang-level/` còn dở.
2. **Checkpoint gắn với *phase*, không gắn với *level*.** Chúng đã đo đủ bốn kỹ năng và đã có ngưỡng
   riêng từng kỹ năng, nhưng vẫn chưa phải một bài kiểm tra kết thúc level đúng nghĩa.
3. **Bộ luyện viết độc lập ở `/learn/write`** (14 bài, 3 bộ) không tính vào mastery và không gắn với
   level nào. Nó dùng chung bộ chấm với bài viết trong bài học, nhưng vẫn là một hòn đảo cạnh lộ trình.
4. **Chấm viết bằng luật không đo được mạch lạc và giọng điệu.** Nó đo cấu trúc, ý bắt buộc, và lỗi
   thường gặp — đừng hứa nhiều hơn thế.
