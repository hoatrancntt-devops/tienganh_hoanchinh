# English@Work

Web app dạy tiếng Anh cho **người Việt đi làm bị mất gốc**. Trọng tâm nghe và nói, giải thích hoàn toàn bằng tiếng Việt, tình huống lấy từ standup, ticket, pantry và quán cơm.

- **1–3 tháng** — giao tiếp cơ bản với đồng nghiệp
- **3–6 tháng** — đọc hiểu tài liệu công việc
- Chủ đề: xã giao, ăn uống, đi lại, công sở, và tiếng Anh CNTT (system, network, cloud, helpdesk, AI)

---

## Chạy trong 3 lệnh

Cần: Linux, Docker + Docker Compose, 8GB RAM, ~6GB đĩa trống.

```bash
make env          # tạo .env, tự sinh SECRET_KEY và mật khẩu Postgres
                  # -> mở .env, điền ADMIN_EMAIL và ADMIN_PASSWORD
make up           # build và khởi động (lần đầu ~8-12 phút, tải model whisper + piper)
make seed         # nạp 13 bài học + sinh audio + tạo tài khoản
```

Mở **http://localhost:9999**

| | |
|---|---|
| Học viên demo | `demo@englishatwork.vn` / `demo12345` |
| Quản trị | giá trị bạn đặt trong `ADMIN_EMAIL` / `ADMIN_PASSWORD` |

> `make seed` lần đầu mất ~2 phút vì sinh ~100 file audio bằng Piper. Nếu container `speech` chưa lên kịp, seed vẫn xong nhưng không có tiếng — chạy lại `make seed` sau một phút, nó chỉ sinh phần còn thiếu.

---

## Demo end-to-end

1. **Đăng nhập** với tài khoản demo tại `/login`
2. **Onboarding** — chọn mục tiêu, thời lượng, kiểm tra micro
3. **Placement test** — 26 câu, ~18 phút. Đo **bốn kỹ năng** (nghe / nói / đọc / viết) cộng trục phụ từ vựng–ngữ pháp. Kết quả xếp Pre-A1 / A1 / A2 / B1 kèm biểu đồ bốn trục và giải thích tiếng Việt
4. **Roadmap** tại `/learn` — 5 phase, bài khoá/mở theo DAG tiên quyết, có ô "Học tiếp" giải thích *vì sao* là bài này
5. **Lesson player** — nghe → nhắc lại → nói (chấm phát âm ngay) → quiz
6. **Gợi ý bài kế** hiện ngay sau khi xong bài
7. **Thông báo** — chuông ở header, hoặc `/notifications`

Muốn xem engine chống nhảy cóc: bấm vào một bài bị khoá (ví dụ `D01` khi chưa qua `CP-F`). Bạn sẽ thấy con số cụ thể còn thiếu và nút thi vượt.

---

## Kiến trúc

```
Browser --:9999--> app (FastAPI + Jinja2 + HTMX)
                    |-- /api/v1/*   JSON API
                    |-- /admin      CMS + cấu hình mail/AI
                    |-- APScheduler outbox, nhắc học, streak, dọn dẹp
                    |
                    |--httpx--> speech (faster-whisper + piper)
                    |              lazy load, unload sau 10' idle, tối đa 2 job ASR
                    +--asyncpg-> postgres:16  (volume pgdata)
```

Bốn quyết định định hình mọi thứ:

1. **Audio sinh sẵn lúc seed.** Chi phí runtime của phần nghe bằng 0.
2. **Chấm phát âm chạy local.** faster-whisper + so khớp âm vị. Không LLM, không gửi giọng học viên đi đâu.
3. **Không Node.** Jinja2 + HTMX + CSS viết tay. Một ngôn ngữ, một process.
4. **AI là phần thêm, không phải nền.** Không có API key thì app vẫn dạy đủ.

### Ngân sách RAM

| | Idle | Peak |
|---|---|---|
| postgres | ~250MB | ~700MB |
| app | ~250MB | ~500MB |
| speech | ~200MB | ~1.6GB |
| **tổng** | **~700MB** | **~2.8GB** |

Máy yếu hơn: đổi `WHISPER_MODEL=base` trong `.env`. **Đừng tăng `SPEECH_MAX_CONCURRENT`** — nó là thứ duy nhất chặn máy swap khi nhiều người ghi âm cùng lúc.

---

## Cấu hình

### Email (Microsoft 365 OAuth 2.0 hoặc SMTP)

Cấu hình trên web tại **`/admin/settings/mail`** — không có biến env cho phần này. Client secret được mã hoá trước khi lưu DB.

Với M365, làm bên Azure trước:

1. **App registration** → tạo app mới
2. **API permissions** → Microsoft Graph → **Application permissions** (không phải Delegated) → `Mail.Send`
3. **Grant admin consent**
4. **Certificates & secrets** → New client secret
5. Điền Tenant ID, Client ID, Client secret, và địa chỉ gửi (phải là mailbox có thật trong tenant)

Bấm **Gửi thư thử** để kiểm chứng ngay.

### AI (tuỳ chọn)

Nhập API key trên web tại **`/admin/settings/ai`**. Hỗ trợ Anthropic, OpenAI, Gemini, OpenRouter, Ollama, Azure OpenAI.

Routing dạng chuỗi ưu tiên, provider đầu lỗi thì tự chuyển tiếp:

```
T1 (tác vụ thường xuyên):  anthropic:claude-haiku-4-5,gemini:gemini-2.0-flash
T2 (roleplay, soạn nội dung):  anthropic:claude-sonnet-5
```

Kiểm soát chi phí: cache theo hash, hạn mức mỗi user mỗi ngày, và trần chi phí toàn hệ thống mỗi tháng. Trên 70% trần tự hạ T2 xuống T1; trên 90% chỉ dùng cache và rule-based. Giá model nằm trong `config/llm_prices.json`.

**Không có API key thì app vẫn dạy đủ:** giải thích lấy từ `vietnamese_explanation` và `common_mistakes` của từng bài (là trường bắt buộc), chấm phát âm chạy local. Nút AI ẩn hẳn thay vì hiện ra rồi disable.

---

## Nội dung

Nguồn sự thật là `seeds/content/*.yaml`, không phải DB. Sửa YAML rồi `make seed`.

```bash
make validate     # cổng chất lượng, chạy được ngoài Docker
```

Cổng này chặn publish nếu: thiếu `vietnamese_explanation`, có dưới 2 `common_mistakes`, `mastery_weights` không cộng đúng 1.0, DAG có chu trình, bài phase nói có dưới 4 drill, hoặc `est_minutes > 12`.

**Hiện có 62 bài** trải bốn level Pre-A1 → B1. Thang level, tuyên bố đầu ra từng kỹ năng và bảng ánh xạ bài ↔ level nằm ở [`docs/khung-level.md`](docs/khung-level.md).

**Cả 62 bài đều có đủ bốn kỹ năng** — nghe, nói, đọc, viết. Bài đọc là văn bản liền không sinh audio, câu hỏi bằng tiếng Anh; bài viết chấm bằng luật ngay tại máy chủ, không cần API key.

Toàn bộ nội dung **tự biên soạn 100%**. CEFR / British Council / BBC / Cambridge / VOA chỉ dùng để định hướng — không sao chép câu, hội thoại hay bài tập nào.

---

## Vận hành

```bash
make logs                        # xem log
make backup                      # dump DB + media vào ./backups, giữ 7 ngày
make restore f=backups/db-....gz # phục hồi
make psql                        # mở psql
make test                        # 103 test (SQLite in-memory, không cần Docker)
make dev                         # hot reload
make clean                       # dọn file rác build/test (không đụng dữ liệu)
```

**Backup tự động** — thêm vào crontab:

```
0 3 * * * cd /srv/english-for-work && ./docker/backup.sh >> /var/log/efw-backup.log 2>&1
```

### Dữ liệu qua reboot

`pgdata` là named volume, `./media` là bind mount, mọi container `restart: unless-stopped`. Reboot máy thì Docker tự dựng lại và dữ liệu còn nguyên.

- `make down` — dừng, **giữ** dữ liệu
- `docker compose down -v` — **XOÁ SẠCH** dữ liệu học viên. Đừng chạy trên production.

**Diễn tập restore một lần trước khi mở cho học viên.** Backup chưa test bằng không.

---

## Deploy production

```bash
git clone <repo> /srv/english-for-work && cd /srv/english-for-work
make env                          # rồi điền ADMIN_EMAIL / ADMIN_PASSWORD
make up && make seed
```

Hai việc bắt buộc:

**HTTPS.** Micro không chạy trên HTTP thuần (trừ localhost) — không có HTTPS thì toàn bộ phần nói chết. Đặt Caddy phía trước:

```
englishatwork.example.com {
    reverse_proxy localhost:9999
}
```

**Đừng đổi `SECRET_KEY`.** Mọi API key admin nhập trên web được mã hoá bằng khoá dẫn xuất từ nó. Đổi = mất toàn bộ secret trong DB, và app sẽ **im lặng** coi như chưa cấu hình.

### Migration

`init_db()` dùng `create_all` — chỉ hợp cho dev/test. Trên production dùng Alembic:

```bash
make migrate                        # alembic upgrade head
make revision m="thêm bảng x"       # sau khi sửa models
```

---

## Cấu trúc

```
app/
├── core/            config, security, crypto, logging
├── db/              base, session
├── models/          25 bảng
├── schemas/         Pydantic I/O
├── services/        auth, placement, learning_path, prerequisite,
│                    notification, mail, settings, ai/
├── api/routes/      health, auth, onboarding, placement, learning,
│                    speech, notifications, ai
├── web/             SSR templates + static
├── admin/           CMS + cấu hình mail/AI
├── tasks/           APScheduler
└── seeds/           schema, validate_content, loader, generate_audio
speech_service/      whisper + piper + scoring + feedback_vi
seeds/               content/*.yaml, placement/form_{a,b}.yaml
migrations/          Alembic
tests/
```

Luật phụ thuộc: `routes` → `services` → `models`. Không import model chéo giữa các miền.

---

## Bảo mật

- Mật khẩu: Argon2id (tham số hạ để chừa RAM cho whisper)
- Session: cookie HttpOnly + SameSite=Lax, token lưu dạng hash trong DB
- API key và client secret: Fernet, khoá dẫn xuất từ `SECRET_KEY`, không bao giờ trả nguyên văn ra API
- Audit log ghi *tên* provider đổi key, không bao giờ ghi giá trị key
- Đáp án placement không rời server; điểm nói giữ phía server tới lúc nộp bài
- Container chạy non-root, có mem limit
- Đăng nhập sai: cùng một thông báo cho email không tồn tại và mật khẩu sai, có timing guard

---

## Giới hạn đã biết

| | |
|---|---|
| Nội dung | 13 bài đợt 1. Đợt 2 chờ dữ liệu hiệu chỉnh ngưỡng. |
| CMS | Xem DAG và nội dung tại `/admin/content`; CRUD trên web chưa có — sửa YAML rồi `make seed`. |
| Roleplay | Kịch bản `RP-*.yaml` chưa viết. AI panel hiện chỉ có task `explain`. |
| Scheduler | Một worker. Nhiều worker cần advisory lock (đã có code, chưa test tải). |
| Ngưỡng điểm | Giá trị khởi điểm, chưa hiệu chỉnh trên học viên thật. |
| g2p | Lexicon viết tay phủ nội dung seed + luật cho từ lạ. Từ ngoài lexicon chấm kém chính xác hơn. |
