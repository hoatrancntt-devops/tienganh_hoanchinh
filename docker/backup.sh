#!/usr/bin/env sh
# Sao lưu DB + media. Chạy: ./docker/backup.sh  (hoặc make backup)
# Cron gợi ý:  0 3 * * *  cd /srv/english-for-work && ./docker/backup.sh
set -eu

DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"
[ -f .env ] && . ./.env

OUT="${DIR}/backups"
KEEP="${BACKUP_KEEP_DAYS:-7}"
STAMP="$(date +%Y-%m-%d_%H%M)"
mkdir -p "$OUT"

echo "-> dump database..."
docker compose exec -T db pg_dump -U "${POSTGRES_USER:-efw}" -d "${POSTGRES_DB:-efw}" \
  | gzip > "${OUT}/db-${STAMP}.sql.gz"

echo "-> archive media..."
tar -czf "${OUT}/media-${STAMP}.tar.gz" -C "$DIR" media 2>/dev/null || true

SIZE=$(gzip -l "${OUT}/db-${STAMP}.sql.gz" | awk 'NR==2{print $2}')
if [ "${SIZE:-0}" -lt 1000 ]; then
  echo "[X] Dump chi ${SIZE} byte — co gi do sai. Giu file de kiem tra." >&2
  exit 1
fi

find "$OUT" -name 'db-*.sql.gz'    -mtime "+${KEEP}" -delete
find "$OUT" -name 'media-*.tar.gz' -mtime "+${KEEP}" -delete

echo "[OK] ${OUT}/db-${STAMP}.sql.gz  ($(du -h "${OUT}/db-${STAMP}.sql.gz" | cut -f1))"
echo "     Backup chua test bang khong. Dien tap restore mot lan: make restore f=..."
