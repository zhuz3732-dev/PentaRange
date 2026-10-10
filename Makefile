# PentaRange convenience targets. Everything here is a thin wrapper around docker compose so the
# README stays honest about what actually happens.
.DEFAULT_GOAL := help
COMPOSE := docker compose

.PHONY: help up down restart logs ps reset seed shell-web shell-db verify lint

help: ## 显示所有可用目标
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

up: ## 构建并启动全部服务
	$(COMPOSE) up -d --build
	@echo "web      -> http://127.0.0.1:8000"
	@echo "webshell -> http://127.0.0.1:8081"
	@echo "adminer  -> http://127.0.0.1:8082"

down: ## 停止全部服务
	$(COMPOSE) down

restart: ## 重启全部服务
	$(COMPOSE) restart

logs: ## 跟踪日志
	$(COMPOSE) logs -f --tail=100

ps: ## 查看状态
	$(COMPOSE) ps

reset: ## 删掉容器和卷，回到全新状态（会清空数据库与已上传文件）
	$(COMPOSE) down -v

seed: ## 重新灌入种子数据
	$(COMPOSE) exec -T db mysql -uroot -pPentaRange_admin_2026 pentarange < app/seed.sql

shell-web: ## 进 web 容器
	$(COMPOSE) exec web bash

shell-db: ## 进 mysql 客户端
	$(COMPOSE) exec db mysql -uroot -pPentaRange_admin_2026 pentarange

verify: ## 冒烟测试：确认三个入口都活着
	@curl -fsS http://127.0.0.1:8000/ >/dev/null && echo "web      OK"
	@curl -fsS http://127.0.0.1:8081/ >/dev/null && echo "webshell OK"
	@curl -fsS http://127.0.0.1:8082/ >/dev/null && echo "adminer  OK"

lint: ## 语法检查所有 Python 文件
	@find app -name '*.py' -print0 | xargs -0 python -m py_compile && echo "python OK"
