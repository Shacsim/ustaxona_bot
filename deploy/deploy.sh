#!/usr/bin/env bash
# Serverga deploy: kod → /home/admin/ustaxona_bot, Mini App → /var/www/ustaxona,
# keyin docker compose qayta yig'adi (migratsiya avtomatik).
# Serverdagi .env va backups/ ga tegilmaydi.
set -euo pipefail
HOST=${HOST:-shacsim}
DIR=${DIR:-/home/admin/ustaxona_bot}
cd "$(dirname "$0")/.."

echo "→ Deploydan oldin bazaning zaxira nusxasi"
ssh "$HOST" "cd $DIR && sudo docker compose exec -T db pg_dump -U ustaxona -d ustaxona --clean --if-exists | gzip | sudo tee backups/predeploy_\$(date +%Y%m%d_%H%M%S).sql.gz >/dev/null"

echo "→ Kodni yuklash"
rsync -az --delete --no-owner --no-group --rsync-path="sudo rsync" \
  --exclude venv --exclude .venv --exclude .git --exclude __pycache__ \
  --exclude .env --exclude backups --exclude '*.sql.gz' \
  ./ "$HOST:$DIR/"

echo "→ Mini App (telefon raqami)"
ssh "$HOST" "sudo install -D -m 644 $DIR/webapp/tel.html /var/www/ustaxona/tel.html"

echo "→ Qayta yig'ish va ishga tushirish"
ssh "$HOST" "cd $DIR && sudo docker compose up -d --build && sleep 8 && sudo docker compose logs --tail 25 bot"
