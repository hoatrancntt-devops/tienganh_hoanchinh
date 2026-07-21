# Runbook deploy VPS (chỉ có IP) — English@Work

Mục tiêu: chạy app trên VPS Linux để học thử vài tuần, có HTTPS để micro hoạt động.
Đối tượng chạy: bạn, trực tiếp trên VPS. Mọi lệnh đã được kiểm chứng cấu hình trên máy dev trước khi viết.

## Bối cảnh đã chốt

- VPS **chỉ có IP**, không domain → HTTPS bằng **Caddy + self-signed cert** (Let's Encrypt không cấp cho IP).
- Trình duyệt sẽ cảnh báo cert 1 lần. Bấm "vẫn tiếp tục" → từ đó là secure context → **micro chạy**.
- Code đã ở GitHub nhánh `master`: `https://github.com/hoatrancntt-devops/tienganh_hoanchinh.git`

## Điều kiện VPS

- Linux, Docker + Docker Compose v2, **8GB RAM** (app đỉnh ~2,8GB), ~6GB đĩa trống.
- Mở firewall **port 80 và 443**. KHÔNG cần mở 9999 (xem bước 4 — app ghim vào loopback).

---

## Bước 1 — Lấy code

```bash
git clone https://github.com/hoatrancntt-devops/tienganh_hoanchinh.git
cd tienganh_hoanchinh
```

## Bước 2 — Tạo .env

Repo có sẵn Makefile nhưng nếu VPS không có `make`, chạy trực tiếp:

```bash
cp .env.example .env
# sinh SECRET_KEY và POSTGRES_PASSWORD ngẫu nhiên:
python3 -c "import secrets,pathlib; p=pathlib.Path('.env'); p.write_text(p.read_text().replace('SECRET_KEY=','SECRET_KEY='+secrets.token_urlsafe(48),1).replace('POSTGRES_PASSWORD=','POSTGRES_PASSWORD='+secrets.token_urlsafe(24),1))"
```

Nếu có `make`: chỉ cần `make env`.

## Bước 3 — Điền .env (phần bạn tự làm)

Mở `.env`, sửa 3 dòng:

```
ADMIN_EMAIL=email-cua-ban@...        # tài khoản quản trị của bạn
ADMIN_PASSWORD=<mật khẩu bạn chọn>    # tự đặt, không đi qua ai
DEFAULT_TZ=Asia/Ho_Chi_Minh
```

⚠️ **Đừng đổi `SECRET_KEY` sau khi đã seed.** Mọi API key admin nhập trên web được mã hoá bằng khoá dẫn
xuất từ nó — đổi = mất hết secret trong DB và app **im lặng** coi như chưa cấu hình.

Máy yếu: thêm `WHISPER_MODEL=base` (nhẹ hơn `small`). **Đừng tăng `SPEECH_MAX_CONCURRENT`** — nó là thứ
chặn VPS swap khi nhiều người ghi âm cùng lúc.

## Bước 4 — Chốt an toàn: ghim app vào loopback + bật HTTPS

Base compose mở cổng 9999 ra **0.0.0.0** — trên VPS nghĩa là `http://IP:9999` truy cập được qua HTTP
thuần, vòng qua Caddy, mật khẩu đăng nhập đi trần. Chặn bằng cách thêm vào `.env`:

```
APP_PORT=127.0.0.1:9999
COMPOSE_FILE=docker-compose.yml:docker-compose.https.yml
```

- Dòng 1: Docker ghim 9999 vào loopback (đã kiểm: `host_ip: 127.0.0.1`). Chỉ Caddy cùng máy tới được.
- Dòng 2: mọi lệnh `docker compose` từ đây gồm luôn Caddy.

## Bước 5 — Tạo self-signed cert (SAN = IP VPS)

Caddyfile trỏ tới `/certs/cert.pem` và `/certs/key.pem`. Tạo chúng, thay `<IP_VPS>`:

```bash
mkdir -p certs
openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -keyout certs/key.pem -out certs/cert.pem \
  -subj "/CN=<IP_VPS>" -addext "subjectAltName=IP:<IP_VPS>"
```

`-addext subjectAltName=IP:...` là bắt buộc — trình duyệt hiện đại bỏ qua CN, chỉ đọc SAN.

## Bước 6 — Khởi động

```bash
docker compose up -d --build
```

Lần đầu **8–12 phút**: build image + tải model Whisper (nhận giọng) và Piper (đọc mẫu), ~6GB.
Theo dõi: `docker compose logs -f --tail=80`

## Bước 7 — Migration + seed

```bash
docker compose exec app alembic upgrade head
docker compose exec app python -m scripts.seed_data
```

`seed_data` nạp toàn bộ **62 bài** + sinh **~100+ file audio** bằng Piper (mất ~2 phút) + tạo tài khoản
admin (từ .env) và demo. Nếu container `speech` chưa lên kịp, seed vẫn xong nhưng thiếu tiếng — chạy lại
lệnh seed sau 1 phút, nó chỉ bù phần còn thiếu.

## Bước 8 — Vào học

Mở `https://<IP_VPS>` → cảnh báo cert → "vẫn tiếp tục" → micro hoạt động.

| Vai trò | Đăng nhập |
|---|---|
| Học viên | `demo@englishatwork.vn` / `demo12345` |
| Quản trị | ADMIN_EMAIL / ADMIN_PASSWORD bạn đặt ở bước 3 |

Kiểm nhanh: đăng nhập demo → onboarding (thử micro ở đây) → placement test → `/learn` → mở một bài,
thu âm một câu, xem có chấm điểm phát âm không. Chấm được = HTTPS + speech chạy đúng.

---

## Vận hành trong lúc học thử

- Xem log: `docker compose logs -f --tail=80`
- Dừng (giữ dữ liệu): `docker compose down`
- Chạy lại: `docker compose up -d`
- Sao lưu tiến độ: `./docker/backup.sh` → ra `./backups/`
- Cập nhật code mới: `git pull && docker compose up -d --build` rồi `alembic upgrade head`

## Kiểm lại sức khỏe

```bash
docker compose ps                          # cả 4 service Up
curl -k https://localhost/api/v1/health    # -k vì self-signed; mong đợi 200
docker stats --no-stream                   # RAM có gần trần 2,8GB không
```

## Bẫy đã biết

| Triệu chứng | Nguyên nhân | Xử lý |
|---|---|---|
| Nút thu âm im, không chấm | Vào bằng `http://IP:9999` thay vì `https://IP` | Luôn dùng https. Bước 4 đã chặn cổng trần |
| Bài có tiếng nhưng không chấm được giọng | Chưa bấm chấp nhận cert | Vào `https://IP`, chấp nhận cảnh báo 1 lần |
| Bài không có audio mẫu | Container speech lên chậm lúc seed | Chạy lại lệnh seed bước 7 |
| VPS swap, ì | Nhiều người ghi âm cùng lúc | Giữ `SPEECH_MAX_CONCURRENT=2`, hạ `WHISPER_MODEL=base` |
| Mọi secret admin "biến mất" | Đã đổi `SECRET_KEY` sau seed | Không đổi. Nếu lỡ, nhập lại API key trong admin |

## Chưa giải quyết

1. Chưa test thực trên VPS của bạn — runbook kiểm chứng trên máy dev (Docker 29.3.0, WSL2). Bước có thể
   vênh: openssl trên VPS (phiên bản cũ có thể không nhận `-addext`), và thời gian tải model tùy mạng VPS.
2. Chưa có backup tự động — mới có script thủ công `./docker/backup.sh`. Học vài tuần thì nên cron nó hằng ngày.
3. `init_db()` dùng `create_all` (chỉ hợp dev). Runbook dùng Alembic như README khuyến cáo cho production.
