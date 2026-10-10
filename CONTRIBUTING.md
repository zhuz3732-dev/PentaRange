# 贡献指南

## 新增一关

只需动两个地方，第三处会自动生效：

1. **写模块** `app/challenges/<level>.py`

   必须提供 `low` / `medium` / `high` 三个函数，签名统一：

   ```python
   def low(q: str, request) -> str:
       """返回给页面渲染的字符串。抛异常也行，异常会在页面上完整回显（这是有意设计）。"""
       ...
   ```

   `q` 是 `?q=` 的原始值（**故意不做任何清洗**），`request` 是活的 Flask request，需要 POST body / header / cookie 时直接取。

2. **登记元信息** 在 `app/main.py` 的 `LEVEL_INFO` 里加一项，写清标题、简介和每档目标。没有这一项，关卡页面能跑但索引页不会列出它。

3. **自动注册** —— `app/challenges/__init__.py` 会遍历模块并注册 `(level, tier)`，不用手改。

### 难度设计约定

| 档位 | 要求 |
|---|---|
| `low` | 教科书式漏洞，页面上给足提示和可复制的 payload 方向 |
| `medium` | 加一层能被绕过的防护（黑名单、MIME 检查、scheme 限制），提示降级为方向性描述 |
| `high` | 防护看起来合理但存在逻辑缺陷（TOCTOU、字符串比对、前后端转义错配），只给思路不给答案 |

### 别忘了 flag

在 `app/seed.sql` 的 `flags` 表里插入对应 `(level, tier)` 行，并在模块里用 `db.fetch_flag(level, tier)` 取出来回显。没有 flag 的关卡收不了尾。

## 代码风格

- Python：PEP 8，类型标注，模块 docstring 说明这一关**教什么**而不是复述代码。
- **注释解释「为什么」，不解释「是什么」。** 特别是故意留的漏洞，要写清它对应哪个真实场景——学习者需要的是迁移能力。
- 前端：原生 HTML/CSS/JS，不引入构建步骤，不引入 CDN。

## 提交前自检

```bash
make lint     # 全部 Python 语法检查
make up       # 能起来
make verify   # 三个入口都活着
```

## 提交规范

Conventional Commits：

```
feat(sqli): add medium tier with boolean-blind variant
fix(upload): correct MIME check bypass hint
docs(readme): document the webshell container
```

## 安全底线

**不要把靶场往公网放。** 提 PR 时不要顺手改 `docker-compose.yml` 里的端口绑定，`127.0.0.1` 前缀是安全绳。