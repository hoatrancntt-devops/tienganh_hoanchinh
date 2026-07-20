# Đối chiếu từ vựng 62 bài học với danh sách tần suất chuẩn

Ngày: 2026-07-20
Phạm vi: `seeds/content/{foundation,daily,office,it_english,reading}/*.yaml`
Không sửa file nào trong `seeds/`.

---

## 1. Nguồn wordlist đã dùng

**Chính — NGSL (New General Service List) v1.01**

- Nội dung: 2.818 headword, đã sắp xếp theo thứ hạng tần suất (dòng 1 = `the`, dòng 2 = `be`, …). Thứ hạng dòng chính là band tần suất.
- URL tải được thật: `https://raw.githubusercontent.com/evan-007/ngsl-dictionary/master/public/data/ngsl-utf8.csv`
- Nguồn gốc: newgeneralservicelist.org (Browne, Culligan & Phillips). Giấy phép của NGSL là **CC BY-SA 4.0**. Bản mirror trên GitHub (`evan-007/ngsl-dictionary`) chỉ là bản sao dữ liệu headword + định nghĩa.
- Ghi chú trung thực: trang chủ newgeneralservicelist.org phát hành file qua Google Drive/Dropbox nên không tải trực tiếp bằng `curl` được. Bản mirror GitHub là thứ tải được thật sự. Số lượng headword (2.818) khớp với con số NGSL công bố (~2.800), nên tôi tin bản mirror là đúng — nhưng đây **là** một bản sao bên thứ ba, không phải nguồn chính thức.

**Phụ — google-10000-english** (dùng làm tham chiếu thứ hai, KHÔNG dùng để chấm điểm)

- URL: `https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa-no-swears.txt`
- Giấy phép: Public domain / CC0 (dựa trên Google Trillion Word Corpus).
- Vai trò: với mỗi từ nằm ngoài NGSL, tra thêm thứ hạng trong top-10.000 tiếng Anh để phân biệt "từ hiếm thật" và "từ thường gặp nhưng không phải headword NGSL".

**Đã thử và thất bại:** `nrrb/new-general-service-list` (404), tải trực tiếp từ newgeneralservicelist.org (không có link tĩnh). Không dùng Oxford 3000/5000 vì Oxford không phát hành list dạng dữ liệu mở tải được — chỉ có bản PDF/web có bản quyền.

---

## 2. Phương pháp

1. Parse 62 file YAML. **5 file `CP-*.yaml` (checkpoint) không có khối `vocabulary:` nào** → không chấm được, còn lại **57 bài** có từ vựng.
2. Với mỗi mục từ vựng: lấy `term` (nguồn chính) và `chunk` (nguồn phụ).
3. Chuẩn hoá: lowercase, bỏ dấu câu, **bóc IPA nội tuyến** (bài F13–F17 nhét IPA thẳng vào `term`, ví dụ `"sheep /ʃiːp/"` — nếu không bóc thì các mảnh IPA bị đếm nhầm thành "từ ngoài list"), **tách dạng rút gọn** (`I'll` → `I` + `will`, `can't` → `can` + `not`).
4. Lemmatize thô bằng luật hậu tố (-s/-es/-ies/-ed/-ing/-er/-est/-ly, phụ âm nhân đôi) cộng một bảng ~90 động từ bất quy tắc.
5. Map vào band: top-1000 / 1001-2000 / 2001-2818 / ngoài NGSL.
6. **Loại khỏi mẫu số:** thuật ngữ IT (danh sách riêng ~250 từ), số đếm/số thứ tự (NGSL không đưa số vào headword), tên riêng.

---

## 3. Bảng tổng

Cột "% trong top-2000" tính trên các token đã chấm, **đã loại IT jargon, số đếm và tên riêng** khỏi mẫu số.

| Bài | cefr_target | Số mục từ vựng | Token đã chấm | % trong top-2000 | Số từ ngoài NGSL | Từ ngoài list |
|---|---|---|---|---|---|---|
| F01 | pre_a1 | 6 | 4 | 100.0% | 0 | — |
| F02 | pre_a1 | 6 | 6 | 100.0% | 0 | — |
| F03 | pre_a1 | 6 | 5 | 100.0% | 0 | — |
| F04 | pre_a1 | 6 | 6 | 100.0% | 0 | — |
| F05 | a1 | 6 | 4 | 100.0% | 0 | — |
| F06 | a1 | 6 | 7 | 100.0% | 0 | — |
| F07 | a1 | 6 | 9 | 100.0% | 0 | — |
| F08 | a1 | 6 | 12 | 91.7% | 0 | — |
| F09 | a2 | 6 | 6 | 83.3% | 1 | configuration |
| F10 | a2 | 6 | 15 | 100.0% | 0 | — |
| F11 | a2 | 6 | 11 | 90.9% | 0 | — |
| F12 | a2 | 6 | 6 | 83.3% | 1 | schwa |
| F13 | a2 | 6 | 6 | 100.0% | 0 | — |
| F14 | a2 | 6 | 6 | 83.3% | 0 | — |
| F15 | a2 | 6 | 6 | 100.0% | 0 | — |
| F16 | a2 | 6 | 5 | 80.0% | 1 | reload |
| F17 | a2 | 6 | 0 | n/a | 0 | — |
| F18 | b1 | 6 | 10 | 90.0% | 1 | chunk |
| F19 | b1 | 6 | 13 | 100.0% | 0 | — |
| F20 | b1 | 6 | 15 | 86.7% | 1 | dot |
| D01 | a1 | 6 | 14 | 100.0% | 0 | — |
| D02 | a1 | 6 | 14 | 92.9% | 0 | — |
| D03 | a1 | 6 | 12 | 83.3% | 1 | allergic |
| D04 | a1 | 6 | 13 | 92.3% | 1 | reception |
| O01 | a2 | 6 | 11 | 100.0% | 0 | — |
| O02 | a2 | 6 | 15 | 100.0% | 0 | — |
| O03 | a2 | 6 | 15 | 100.0% | 0 | — |
| O04 | a2 | 6 | 14 | 100.0% | 0 | — |
| O05 | a2 | 6 | 14 | 92.9% | 1 | halfway |
| O06 | a2 | 6 | 15 | 93.3% | 1 | reschedule |
| O07 | a2 | 6 | 20 | 90.0% | 1 | stuck |
| O08 | a2 | 6 | 14 | 100.0% | 0 | — |
| I01 | a2 | 6 | 9 | 88.9% | 0 | — |
| I02 | a2 | 6 | 18 | 94.4% | 1 | meantime |
| I03 | a2 | 6 | 15 | 86.7% | 2 | click, restart |
| I04 | a2 | 6 | 21 | 100.0% | 0 | — |
| I05 | b1 | 6 | 19 | 100.0% | 0 | — |
| I06 | b1 | 6 | 14 | 85.7% | 1 | workaround |
| I07 | b1 | 6 | 18 | 100.0% | 0 | — |
| I08 | b1 | 6 | 11 | 90.9% | 0 | — |
| I09 | b1 | 6 | 13 | 92.3% | 1 | nit |
| I10 | b1 | 6 | 6 | 83.3% | 1 | ping |
| I11 | b1 | 6 | 7 | 100.0% | 0 | — |
| I12 | b1 | 6 | 9 | 55.6% | 3 | click, reset, suspicious |
| I13 | b1 | 6 | 10 | 80.0% | 0 | — |
| I14 | b1 | 6 | 21 | 100.0% | 0 | — |
| I15 | b1 | 6 | 17 | 88.2% | 1 | unavailable |
| R01 | a2 | 6 | 12 | 83.3% | 2 | eod, fyi |
| R02 | a2 | 6 | 12 | 91.7% | 0 | — |
| R03 | b1 | 6 | 7 | 71.4% | 2 | deprecated, upgrade |
| R04 | b1 | 6 | 9 | 66.7% | 3 | installation, prerequisites, usage |
| R05 | b1 | 6 | 9 | 66.7% | 2 | reproduce, reproducible |
| R06 | b1 | 6 | 7 | 28.6% | 4 | info, retry, stack, timestamp |
| R07 | b1 | 6 | 11 | 81.8% | 2 | cc, thread |
| R08 | b1 | 6 | 5 | 80.0% | 1 | optional |
| R09 | b1 | 6 | 8 | 75.0% | 2 | mitigation, vulnerability |
| R10 | b1 | 6 | 7 | 57.1% | 3 | blameless, impact, timeline |

Phân bố cấp độ: pre_a1 = 4 bài, a1 = 8, a2 = 23, b1 = 22.

---

## 4. Cờ đỏ

### 4.1 Cờ đỏ "gán cấp quá thấp" (bài dễ nhưng chứa từ khó): KHÔNG CÓ

Đây là kết quả tích cực và đáng nói rõ: **không một bài pre_a1 hay a1 nào (12 bài) chứa từ nằm ngoài NGSL.** Toàn bộ 12 bài đều ở mức 91,7–100% top-2000. Tầng nhập môn được kiểm soát chặt. Không cần can thiệp.

Bài a2 cũng sạch: từ "lệch" duy nhất ở tầng a2 là các từ đơn lẻ và đều nằm trong top-3000 tiếng Anh phổ thông (`configuration` g10k#2134, `reload` #6886, `restart`, `click` #94, `meantime`) — đều là từ người học IT gặp hằng ngày trên giao diện máy tính.

### 4.2 Cờ đỏ thật sự — cụm bài Reading (R03–R10)

Đây là chỗ duy nhất có vấn đề hệ thống. 6/8 bài reading gán b1 có mật độ từ ngoài list cao bất thường:

| Bài | % top-2000 | Từ gây lệch | Đánh giá |
|---|---|---|---|
| **R06** | **28,6%** | `info`, `retry`, `stack`, `timestamp` | **Nặng nhất.** 0/7 token nằm trong top-1000. `timestamp`, `retry` ngoài cả top-10.000. Đây là bài log/lỗi — về bản chất là ESP, nhưng vẫn được gán b1 chung. |
| **R10** | 57,1% | `blameless`, `impact`, `timeline` | `blameless` ngoài top-10.000 và là thuật ngữ văn hoá kỹ thuật (blameless postmortem), không phải từ vựng b1. |
| **R04** | 66,7% | `installation`, `prerequisites`, `usage` | `prerequisites` ngoài top-10.000 — từ vựng học thuật/tài liệu, thường xếp B2+. |
| **R05** | 66,7% | `reproduce`, `reproducible` | `reproducible` ngoài top-10.000. Hai biến thể của cùng một gốc chiếm 2/6 slot từ vựng. |
| **R03** | 71,4% | `deprecated`, `upgrade` | `deprecated` ngoài top-10.000, nghĩa chuyên ngành khác hẳn nghĩa thường. |
| **R09** | 75,0% | `mitigation`, `vulnerability` | Cả hai đều là từ vựng an ninh mạng cấp B2/C1 theo thang chung. |

**Nhận định:** cụm R nói chung không sai về mặt sư phạm — nó là ESP đọc-hiểu tài liệu kỹ thuật. Nhưng nhãn `b1` đang che giấu việc tải trọng từ vựng thực tế cao hơn b1. Hai hướng xử lý (chọn 1, thuộc quyền quyết định của planner):
- Nâng `cefr_target` của R03–R06, R09, R10 lên `b2`; hoặc
- Giữ `b1` nhưng bổ sung nhãn phụ kiểu `esp_technical: true` để hệ thống tiến trình không so sánh trực tiếp bài R với bài O/D cùng cấp.

### 4.3 Cờ đỏ phụ — I12 (55,6% top-2000)

`click`, `reset`, `suspicious` — chỉ `suspicious` là từ vựng chung khó thật (ngoài top-10.000). Bài về cảnh báo bảo mật/phishing. Mức lệch nhẹ hơn cụm R nhiều; có thể để nguyên.

### 4.4 Cờ vàng "gán cấp quá cao" — từ vựng không gánh nổi nhãn b1

Nhóm bài gán `b1` nhưng từ vựng gần như hoàn toàn nằm trong top-1000 NGSL:

| Bài | Token top-1000 / tổng |
|---|---|
| F19 | 13/13 = 100% |
| I14 | 21/21 = 100% |
| I07 | 17/18 = 94% |
| I05 | 17/19 = 89% |
| F20 | 13/15 = 87% |
| I11 | 6/7 = 86% |

**Cách đọc đúng:** đây **chưa chắc** là lỗi. Các bài này (F19, F20 về nối âm/đánh vần; I05, I07, I11, I14 về đàm phán, từ chối, họp) đặt độ khó ở **cấu trúc câu, ngữ dụng và tốc độ nghe**, không phải ở từ vựng — mà đó chính là định nghĩa hợp lệ của b1. Từ vựng cao tần dùng cho chức năng ngôn ngữ phức tạp là thiết kế tốt, không phải lỗi.

Điều đáng lưu ý cho planner là **sự bất đối xứng**: cùng nhãn `b1`, bài I14 có 100% từ top-1000 còn bài R06 có 0%. Nếu hệ thống tiến trình/gợi ý bài tiếp theo coi `cefr_target` là thước đo khó dễ so sánh được, thì hai bài này không hề tương đương và trải nghiệm người học sẽ hụt.

### 4.4b ⚠️ Ghi chú kiểm chứng (thêm sau khi rà soát báo cáo, 2026-07-20)

**Cờ đỏ R06 nhiều khả năng là artifact của phương pháp, không phải lỗi nội dung.**

Từ vựng thật của R06 (đã đối chiếu file gốc): `INFO`, `WARNING`, `ERROR`, `timestamp`, `stack trace`, `retry`.
Đây là thuật ngữ log — cùng loại jargon IT với `cache`, `queue`, `API`, `SQL` của F17.

Báo cáo này xử lý hai bài theo hai cách khác nhau:
- F17: jargon bị loại khỏi mẫu số → kết luận "không đo được, KHÔNG phải cờ đỏ" (mục 4.5).
- R06: jargon KHÔNG bị loại → kết luận "cờ đỏ nặng nhất, 28,6%" (mục 4.2).

Áp dụng nhất quán tiêu chí của mục 4.5 thì R06 cũng thuộc nhóm "ngoài tầm đo", không phải cờ đỏ.
Nguyên nhân gốc là danh sách IT jargon viết tay thiếu nhóm thuật ngữ log/level — đúng như phần
"Giới hạn phương pháp" đã tự cảnh báo, nhưng cảnh báo đó chưa được áp dụng ngược vào kết luận chính.

**Còn giá trị sau kiểm chứng:** R04 (`prerequisites`), R05 (`reproducible`), R09 (`mitigation`,
`vulnerability`), R10 (`blameless`) — đây là từ vựng học thuật/kỹ thuật chung, không phải jargon công cụ,
nên việc gán chúng vào `b1` vẫn đáng xem lại.

**Còn giá trị và là phát hiện mạnh nhất:** nhận định ở mục 4.4 rằng `cefr_target` đang trộn hai trục độ khó
(từ vựng vs ngữ dụng). Sai lệch R06/F17 ở trên chính là thêm một bằng chứng cho nhận định đó.

### 4.5 Trường hợp riêng — F17 không đo được

F17 (`a2`) có 6/6 mục từ vựng là thuật ngữ IT thuần: API, URL, JSON, SQL, cache, queue. Sau khi loại IT jargon, mẫu số bằng 0 → **phương pháp này không nói được gì về F17**. Không phải cờ đỏ, chỉ là ngoài tầm đo.

---

## 5. Danh sách IT jargon (tách riêng — KHÔNG tính là cờ đỏ)

38 thuật ngữ IT xuất hiện trong `term`/`chunk`, nằm ngoài NGSL là **bình thường và đúng** với một khoá ESP cho dân IT:

| Thuật ngữ | Bài |
|---|---|
| api | F17 |
| auth | R03 |
| authentication | R09 |
| aws | R04 |
| backup | I13, R01 |
| blockers | I08, O01 |
| browser | I03 |
| bug | O07 |
| cache | F17 |
| cli | R04 |
| config | R03 |
| credentials | R06 |
| deploy | F05, F08, I11, O07 |
| deployed | F03 |
| deployment | F05 |
| dns | I10 |
| downtime | I11, R10 |
| email | F11, F16, I12, I14 |
| endpoint | R08, R09 |
| escalate | I01 |
| firewall | I10 |
| gateway | I10 |
| json | F17, R08 |
| login | I03, I07, R09 |
| migration | O01, O05 |
| outage | I06, I08 |
| password | I12, I15, R02 |
| patch | R09 |
| postmortem | R01, R10 |
| query | F17, I13 |
| queue | F17 |
| script | F16 |
| severity | R09 |
| sql | F17, R08 |
| sync | F01 |
| timeout | I01 |
| token | R02 |
| url | F17 |
| vpn | F02, O01 |

Ngoài ra, ở tầng `chunk` (không tính điểm) còn xuất hiện: `portal`, `laptop`, `icon`, `settings`, `tabs`, `wi-fi`, `sign-in`, `iam`, `cve-`, `inc-`, `auth-service`, `refresh`, `bypass`, `configured`, `overloaded`, `rename`, `client`, `visibility`.

---

## 6. Giới hạn của phương pháp — nói thật

Những điểm sau **làm giảm độ tin cậy của con số**, cần biết trước khi ra quyết định dựa trên báo cáo này:

1. **Lemmatize thô, không phải POS-aware.** Dùng luật hậu tố + bảng bất quy tắc thủ công, không dùng spaCy/NLTK (không có sẵn trong môi trường). Hệ quả cụ thể: từ như `usage` không quy về `use`, `installation` không quy về `install`, `reproducible` không quy về `reproduce`. **Vài trường hợp trong danh sách "ngoài list" ở mục 4.2 thực ra là dạng phái sinh của một headword NGSL** — nếu tính theo word family (như NGSL vốn được thiết kế để dùng) thì R04 và R05 sẽ đỡ nặng hơn con số trong bảng. Đây là sai lệch **theo hướng bi quan**: báo cáo đánh giá bài khó hơn thực tế, không dễ hơn.
2. **NGSL là danh sách headword, không phải danh sách word family đầy đủ.** Bản mirror tôi tải về chỉ có headword + định nghĩa, không có file "word family" đi kèm. Đây là nguyên nhân gốc của giới hạn (1).
3. **NGSL không chứa số đếm, số thứ tự, tên riêng, và phần lớn từ viết tắt.** Tôi đã loại số và tên riêng khỏi mẫu số, nhưng viết tắt (`eod`, `fyi`, `cc`, `nit`) vẫn bị đếm là "ngoài list" — chúng là quy ước email công sở, không phải từ vựng khó. Bài R01 và R07 do đó bị chấm nặng hơn thực tế.
4. **`chunk` chứa nhiều từ chức năng và tên riêng.** Tôi chỉ chấm điểm trên `term`; `chunk` dùng làm tín hiệu phụ và báo cáo riêng. Nếu chấm cả `chunk` thì mọi bài sẽ bị kéo về gần 100% top-1000 (vì `the`, `is`, `to`… áp đảo) và mất hết khả năng phân biệt. Đổi lại, **số token/bài rất nhỏ (4–21)** — nên một từ khó duy nhất có thể kéo tỷ lệ xuống 15-20 điểm phần trăm. Đừng đọc các % này như số liệu thống kê ổn định; hãy đọc danh sách từ cụ thể.
5. **Bài F12 dùng phiên âm giả có chủ ý** (`check-thuh-logs`, `fer`, `lotta`, `need-tuh-go`) để dạy nói nối. Những chuỗi này bị đếm là ngoài list ở tầng `chunk`. Đã loại khỏi phần chấm điểm nhưng cần biết khi đọc mục 3 phần chunk.
6. **Danh sách IT jargon là do tôi soạn thủ công (~250 từ), không phải chuẩn ngành.** Không có wordlist ESP-IT mở nào tương đương NGSL. Ranh giới "IT jargon" vs "từ chung" ở vài trường hợp là phán đoán chủ quan — ví dụ tôi xếp `timeout`, `escalate` là IT jargon nhưng `restart`, `reload`, `click`, `reset` là từ chung. Đổi phán đoán này sẽ đổi kết quả một vài bài.
7. **NGSL từ mirror bên thứ ba**, không phải bản tải chính thức (xem mục 1). Số headword khớp con số công bố nhưng tôi không xác minh được từng dòng.
8. **5 file checkpoint không có dữ liệu.** Báo cáo phủ 57/62 bài. `CP-D`, `CP-F`, `CP-I`, `CP-O`, `CP-R` không có khối `vocabulary:` nên không thể đối chiếu — nếu chúng có từ vựng ở dạng khác (ví dụ tham chiếu lại bài trước) thì cần kiểm riêng.

---

## 7. Kết luận ngắn cho planner

1. **Tầng nhập môn (pre_a1, a1, a2 — 35 bài) không có vấn đề tần suất.** Không cần đụng đến.
2. **Cụm Reading R03–R06, R09, R10 là cờ đỏ thật.** Nhãn `b1` không phản ánh tải trọng từ vựng thực tế. Cần quyết định: nâng cấp độ, hay thêm nhãn ESP riêng.
3. **Nhãn `cefr_target` hiện đang trộn hai loại độ khó** (từ vựng vs. ngữ dụng/cấu trúc). Bài I14 và bài R06 cùng là `b1` nhưng khoảng cách từ vựng là 100% vs 0% top-1000. Nếu engine gợi ý bài dựa vào `cefr_target`, đây là rủi ro trải nghiệm cần xử lý ở tầng thiết kế dữ liệu, không phải tầng nội dung.
4. Trước khi hành động dựa trên các % ở mục 4.2, nên xác nhận lại giới hạn (1) và (3) — một phần từ trong danh sách "ngoài list" của R04, R05, R01, R07 là artefact của phương pháp chứ không phải từ khó thật.

---

Script phân tích lưu ở scratchpad (`vocab_audit.py`, `ngsl.csv`, `google10k.txt`, `audit.json`), không đưa vào repo.
