.DEFAULT_GOAL := help
COMPOSE := docker compose
DEV := $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml

.PHONY: help
help: ## Danh sách lệnh
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

.PHONY: env
env: ## Tạo .env với SECRET_KEY sinh ngẫu nhiên
	@test -f .env && echo ".env da ton tai, khong ghi de." && exit 0 || true
	@cp .env.example .env
	@python3 -c "import secrets,pathlib; p=pathlib.Path('.env'); p.write_text(p.read_text().replace('SECRET_KEY=', 'SECRET_KEY='+secrets.token_urlsafe(48), 1).replace('POSTGRES_PASSWORD=', 'POSTGRES_PASSWORD='+secrets.token_urlsafe(24), 1))"
	@echo "[OK] Da tao .env. Gio dien ADMIN_EMAIL va ADMIN_PASSWORD."

.PHONY: up
up: ## Khởi động (prod)
	$(COMPOSE) up -d --build
	@echo "-> http://localhost:9999"

.PHONY: dev
dev: ## Khởi động (dev, hot reload)
	$(DEV) up --build

.PHONY: down
down: ## Dừng (GIỮ dữ liệu)
	$(COMPOSE) down

.PHONY: logs
logs: ## Xem log
	$(COMPOSE) logs -f --tail=80

.PHONY: migrate
migrate: ## Chạy migration Alembic
	$(COMPOSE) exec app alembic upgrade head

.PHONY: seed
seed: ## Nạp nội dung + sinh audio + tạo admin
	$(COMPOSE) exec app python -m scripts.seed_data

.PHONY: seed-fast
seed-fast: ## Nạp nội dung, bỏ qua sinh audio
	$(COMPOSE) exec app python -m scripts.seed_data --no-audio

.PHONY: validate
validate: ## Cổng chất lượng nội dung (chạy được ngoài Docker)
	python -m app.seeds.validate_content

.PHONY: test
test: ## Chạy test (SQLite in-memory, không cần Docker)
	SECRET_KEY=test-secret-key-at-least-32-characters-long pytest -q

.PHONY: backup
backup: ## Sao lưu DB + media ra ./backups
	./docker/backup.sh

.PHONY: restore
restore: ## Phục hồi:  make restore f=backups/db-2026-07-17.sql.gz
	@test -n "$(f)" || (echo "Thieu f=<file>"; exit 1)
	gunzip -c $(f) | $(COMPOSE) exec -T db psql -U $${POSTGRES_USER:-efw} -d $${POSTGRES_DB:-efw}
	@echo "[OK] Da phuc hoi tu $(f)"

.PHONY: shell
shell: ## Shell trong container app
	$(COMPOSE) exec app /bin/bash

.PHONY: psql
psql: ## Mở psql
	$(COMPOSE) exec db psql -U $${POSTGRES_USER:-efw} -d $${POSTGRES_DB:-efw}

.PHONY: clean
clean: ## Xoá file rác build/test (KHÔNG đụng dữ liệu)
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	rm -rf data/dev.db data/dev.db-wal data/dev.db-shm
	@echo "[OK] Da don. Du lieu prod (volume pgdata, ./media) khong bi dung."
