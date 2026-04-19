# MyWebsite

前后端分离个人网站项目（V1.4）：

- 前端：Vue 3 + Vite + Tailwind CSS（`/home/runner/work/MyWebsite/MyWebsite/frontend`）
- 后端：FastAPI + Pydantic + SQLAlchemy + SQLite（`/home/runner/work/MyWebsite/MyWebsite/backend`）
- API 文档：`/docs`、`/redoc`

---

## 1. 项目定位

MyWebsite 不再只是“轻量 Flask 博客”，而是一个可持续演进的现代全栈项目：

- 前端负责展示与交互
- FastAPI 负责 API 与业务编排
- SQLite 负责轻量持久化
- Nginx 负责静态直出与反向代理

核心目标：简单、稳定、可维护。

---

## 2. 目录结构（开发仓库）

```text
/home/runner/work/MyWebsite/MyWebsite/
├── backend/
├── deploy/
├── frontend/
├── README.md
└── Guidance.md
```

> 生产环境建议采用 5 目录物理隔离：`code/`、`database/`、`logs/`、`frontend-dist/`、`uploads/`（详见 `Guidance.md`）。

---

## 3. 本地开发快速开始

## 3.1 后端（FastAPI）

```bash
cd /home/runner/work/MyWebsite/MyWebsite/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 5000 --reload
```

后端启动后可访问：

- http://127.0.0.1:5000/docs
- http://127.0.0.1:5000/redoc

## 3.2 前端（Vue）

```bash
cd /home/runner/work/MyWebsite/MyWebsite/frontend
npm ci
npm run dev
```

默认开发地址（Vite）：http://127.0.0.1:5173

---

## 4. 生产部署概要（Ubuntu 24.04）

推荐采用“极简无痛流”部署模型：

- 禁止使用 `/var/www` 承载业务
- 统一使用用户目录（示例：`/home/admin/program/MyWebsite`）
- 采用 5 目录平级隔离（代码/数据库/日志/前端产物/上传文件）

运行组合：

- FastAPI 进程：Gunicorn + Uvicorn Worker
- 反向代理：Nginx
- 守护：systemd

标准生产启动命令：

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:5000
```

---

## 5. Nginx 关键原则

- `frontend-dist/` 由 Nginx 直接服务（SPA）
- `uploads/` 由 Nginx 静态映射直出
- `/api/` 代理到 FastAPI（127.0.0.1:5000）

这样可以让静态内容和上传资源绕过 Python 进程，提高吞吐并降低后端负载。

---

## 6. 常见问题速查

### 6.1 SQLite 路径写法错误

生产绝对路径必须为 4 斜杠：

```text
sqlite:////home/admin/program/MyWebsite/database/my_website.db
```

### 6.2 数据库只读报错

报错：`attempt to write a readonly database`

通常是目录/文件归属错误（例如被 root 创建），修复时需同时检查：

- `database/` 目录写权限
- 数据库文件 owner/group

### 6.3 服务启动方式不兼容

FastAPI 生产环境请使用 Gunicorn + Uvicorn Worker，避免使用旧 Flask 启动方式。

---

## 7. 文档说明

- `README.md`：对外/开发者快速上手与架构概览
- `Guidance.md`：内部部署手册与避坑宝典（推荐运维必读）
