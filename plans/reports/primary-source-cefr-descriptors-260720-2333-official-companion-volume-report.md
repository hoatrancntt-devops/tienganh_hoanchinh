# Descriptor CEFR chính thức — đối chiếu với 62 bài học

Ngày: 2026-07-20
Nguồn: **CEFR Companion Volume (Council of Europe, 2020)** — 278 trang, PDF chính chủ.

## 1. Nguồn — lấy được thật, không qua trung gian

| | |
|---|---|
| URL | `https://rm.coe.int/common-european-framework-of-reference-for-languages-learning-teaching/16809ea0d4` |
| Loại | **A — chuẩn chính thức**, kho tài liệu `rm.coe.int` của Council of Europe |
| Trạng thái | Tải được, `application/pdf`, 1.784.779 byte, 278 trang |
| Xác minh | Trang 1: "Companion volume — COMMON EUROPEAN FRAMEWORK OF REFERENCE FOR LANGUAGES: LEARNING, TEACHING, ASSESSMENT … The Council of Europe is the continent's leading human rights organisation." |

**Lưu ý kỹ thuật:** `coe.int` và `rm.coe.int` trả **403 với curl mặc định**. Phải gửi User-Agent trình duyệt
mới lấy được. Đây là lý do hai lần chạy agent trước đó thất bại và phải dùng nguồn thứ cấp (blog của hãng
bán bài thi, `linglify.com`). Tài liệu luôn công khai — chỉ là chặn bot.

**Lưu ý thuật ngữ:** trong CV2020 thang tương tác nói tên là **"Overall oral interaction"**, không phải
"spoken interaction" như bản 2001. Tìm sai tên là không ra.

---

## 2. Nguyên văn descriptor (pre-A1 → B1)

### 2.1 Overall oral production (tr. 62)

> **B1** — Can reasonably fluently sustain a straightforward description of one of a variety of subjects within their field of interest, presenting it as a linear sequence of points.
>
> **A2** — Can give a simple description or presentation of people, living or working conditions, daily routines, likes/dislikes, etc. as a short series of simple phrases and sentences linked into a list.
>
> **A1** — Can produce simple, mainly isolated phrases about people and places.
>
> **Pre-A1** — Can produce short phrases about themselves, giving basic personal information (e.g. name, address, family, nationality).

### 2.2 Overall oral comprehension (tr. 48)

> **B1** — Can understand straightforward factual information about common everyday or job-related topics, identifying both general messages and specific details, provided people articulate clearly in a generally familiar variety.
>
> **A2** — Can understand enough to be able to meet needs of a concrete type, provided people articulate clearly and slowly.
>
> **A1** — Can follow language which is very slow and carefully articulated, with long pauses for them to assimilate meaning.
>
> **Pre-A1** — Can understand short, very simple questions and statements, provided […]

### 2.3 Overall oral interaction (tr. 72)

> **B1** — Can communicate with some confidence on familiar routine and non-routine matters related to their interests and professional field. Can exchange, check and confirm information, deal with less routine situations and **explain why something is a problem**.
>
> **A2** — Can interact with reasonable ease in structured situations and short conversations, provided the other person helps if necessary. Can manage simple, routine exchanges without undue effort.

### 2.4 Overall phonological control (tr. 135)

> **A2** — Pronunciation is generally intelligible when communicating in simple everyday situations, provided the interlocutor makes an effort to understand specific sounds. **Systematic mispronunciation of phonemes does not hinder intelligibility**, provided the interlocutor makes an effort to recognise and adjust to the influence of the speaker's language background on pronunciation.
>
> **A1** — Pronunciation of a very limited repertoire of learnt words and phrases can be understood with some effort by interlocutors used to dealing with speakers of the language group. Can reproduce correctly a limited range of sounds as well as stress for simple, familiar words and phrases.

**Thang này KHÔNG có bậc Pre-A1.** Đã kiểm: các bậc xuất hiện trên trang 135 chỉ gồm A1 và A2 trở lên.

---

## 3. Đối chiếu với 62 bài — cái gì đứng vững, cái gì không

### ✅ Đứng vững: nhãn `b1` của phase it_english

Descriptor B1 oral interaction ghi đúng chữ **"explain why something is a problem"**. Đó chính xác là
nội dung I05 ("Giải thích vấn đề kỹ thuật cho người không rành") và cụm I05–I15 nói chung. Đây là chỗ
nhãn CEFR của project khớp với chuẩn ở mức gần như nguyên văn — không phải trùng hợp, mà là thiết kế đúng.

### ✅ Đứng vững: `a2` cho phase office

A2 oral interaction: "interact with reasonable ease in structured situations and short conversations,
provided the other person helps if necessary" — khớp với các tình huống công sở có cấu trúc của O01–O08.

### ❌ Không đứng vững: `pre_a1` cho F01–F04

Bốn bài này là bài **ngữ âm thuần** (/θ/ /ð/, âm cuối /s/ /z/, âm cuối /t/ /d/, cụm phụ âm cuối).
Nhưng:

1. **Thang ngữ âm của CEFR không có bậc Pre-A1.** Không tồn tại descriptor chính thức nào để gán.
2. Trên thang giao tiếp, Pre-A1 là "short phrases about themselves… name, address, family, nationality".
   Hội thoại F01 là giới thiệu nơi làm việc và giờ họp ("The team sync is at three thirty") — vượt
   phạm vi Pre-A1, gần A1 hơn.

Nhãn `pre_a1` ở đây **không sai về mặt sư phạm** (đây đúng là bài dễ nhất, dạy trước tiên) nhưng
**không có căn cứ trong chuẩn**. Nó đang mô tả thứ tự dạy, không phải bậc năng lực.

### ⚠️ Cần xem lại: chuẩn của CEFR là *dễ hiểu*, không phải *chuẩn xác*

Đây là phát hiện đáng giá nhất, và nó thách thức tiền đề của app:

> **A2** — "Systematic mispronunciation of phonemes does not hinder intelligibility, provided the
> interlocutor makes an effort…"

CEFR coi **lỗi phát âm có hệ thống là chấp nhận được** tới tận A2, miễn người nghe vẫn hiểu. Tiêu chí là
*intelligibility*, không phải phát âm giống người bản xứ.

Trong khi đó app đặt `mastery_weights: {speak: 0.5, ...}` và yêu cầu ≥78 điểm phát âm để mở bài kế. Tức là
**app khắt khe hơn chuẩn CEFR ở chính bậc mà CEFR nói hãy khoan dung**. Với người "mất gốc", đây có thể là
chỗ họ bỏ cuộc — bị chặn ở một tiêu chuẩn mà khung tham chiếu châu Âu không đòi hỏi.

Không có nghĩa là app sai — luyện phát âm sớm là lựa chọn sư phạm hợp lệ, và bối cảnh IT nói chuyện với
người nước ngoài có thể đòi hỏi cao hơn mức "tạm hiểu". Nhưng đây là **lựa chọn có chủ ý cần biết mình
đang làm**, không phải mặc định do CEFR quy định.

---

## 4. Trả lời dứt điểm câu hỏi ban đầu

Câu hỏi gốc: *62 bài học có tham khảo nguồn dạy tiếng Anh phổ biến không?*

**Không — nội dung được viết từ kiến thức nền, không tra nguồn.** Sau khi đối chiếu ngược với chuẩn chính
thức thì:

| Khía cạnh | Kết luận |
|---|---|
| Nhãn `b1` (it_english) | Khớp chuẩn, gần như nguyên văn descriptor |
| Nhãn `a2` (office) | Khớp chuẩn |
| Nhãn `pre_a1` (F01–F04) | Không có căn cứ — CEFR không có bậc này cho ngữ âm |
| Ngưỡng phát âm ≥78 | Khắt khe hơn CEFR ở bậc A1–A2 |
| Tải lượng 6 từ/bài | CEFR không quy định — ngoài phạm vi khung |

Nói cách khác: **trực giác sư phạm phần lớn đúng, nhưng nhãn CEFR được gán sau chứ không dẫn đường.**
Chỗ nào nội dung mô tả hành vi giao tiếp thật (giải thích sự cố, họp, hỏi lại) thì khớp chuẩn tốt.
Chỗ nào nhãn được dùng để chỉ *thứ tự dạy* thay vì *bậc năng lực* thì lệch.

---

## 5. Việc này KHÔNG kết luận được

- Từ vựng theo bậc CEFR: Companion Volume **không** đưa ra con số từ vựng cho từng bậc. Các con số
  "A1 = 784 từ" lưu hành trên mạng đến từ English Vocabulary Profile (Cambridge, sản phẩm riêng), không
  phải từ Council of Europe. Chưa lấy được EVP chính chủ.
- Ngưỡng mastery để mở khoá bài: CEFR là khung mô tả năng lực, **không nói gì** về thiết kế phần mềm học tập.
  Không có và sẽ không có căn cứ CEFR cho con số 75/78/80.
- Số từ mới mỗi bài: ngoài phạm vi CEFR hoàn toàn.

## 6. Câu hỏi chưa giải quyết

1. Có nên đổi nhãn F01–F04 từ `pre_a1` sang `a1`, hay giữ và chấp nhận nó nghĩa là "thứ tự dạy"?
2. Ngưỡng phát âm khắt khe hơn CEFR là chủ ý (vì bối cảnh IT quốc tế) hay là mặc định chưa cân nhắc?
3. Có cần lấy English Vocabulary Profile chính chủ để kiểm tra tải lượng từ vựng không?
