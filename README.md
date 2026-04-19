# MyWebsite

前后端分离个人网站项目（V1.4.1）：

- 前端：Vue 3 + Vite + Tailwind（`frontend/`）
- 后端：FastAPI + Pydantic + Uvicorn（`backend/`）
- 数据库：SQLite
- API 文档：`/docs`、`/redoc`

---

## 1. 项目定位

MyWebsite 不再只是“轻量博客”，而是一个可持续演进的现代全栈项目：

- 前端负责展示与交互
- FastAPI 负责 API 与业务编排
- SQLite 负责轻量持久化
- Nginx 负责静态直出与反向代理

核心目标：简单、稳定、可维护。

---

## 2. 核心特性（V1.4.1）

- 极致轻量化：SQLite + FastAPI，低资源占用即可稳定运行
- FastAPI + Pydantic 提供类型安全的数据校验与更清晰的接口边界
- 自带现代化 API 文档：`/docs` 与 `/redoc`
- 基于用户家目录隔离部署（User-level Deployment），彻底规避 `/var/www/` 权限混乱
- 基于用户家目录隔离的本地图床（`uploads/` 持久化 + Nginx 直出）
- 全局配置中心（`backend/config.py`）统一管理数据库与上传路径

---

## 3. 目录结构（开发仓库）

```text
/path/to/MyWebsite/
├── backend/
├── deploy/
├── frontend/
├── README.md
└── Guidance.md
```

> 生产环境建议采用 5 目录物理隔离：`code/`、`database/`、`logs/`、`frontend-dist/`、`uploads/`（详见 `Guidance.md`）。

---

## 4. 本地开发（稍详细）

### 4.1 环境准备

- Python 3.10+（建议 3.11）
- Node.js 18+（建议 20+）
- npm 9+

### 4.2 启动后端（FastAPI）

> 建议在一个独立终端执行。

```bash
cd /path/to/MyWebsite/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
MYWEBSITE_BASE_PATH=/path/to/MyWebsite uvicorn main:app --host 127.0.0.1 --port 5000 --reload
```

说明：

- `MYWEBSITE_BASE_PATH` 在本地开发时建议显式指定到仓库根目录，避免默认落到生产路径 `/home/admin/program/MyWebsite`
- 后端 API 与文档地址：
  - http://127.0.0.1:5000/api/ping
  - http://127.0.0.1:5000/docs
  - http://127.0.0.1:5000/redoc

### 4.3 启动前端（Vue + Vite）

> 在另一个终端执行。

```bash
cd /path/to/MyWebsite/frontend
npm install
npm run dev
```

默认开发地址（Vite）：http://127.0.0.1:5173  
默认会把 `/api` 请求代理到 `http://127.0.0.1:5000`。

---

## 5. 前端部署流闭环（标准防呆）

```bash
cd /path/to/MyWebsite/frontend
npm install
npm run build
cp -r dist/* ../frontend-dist/
```

---

## 6. 生产部署（先看这里）

生产环境部署请**务必先完整阅读**：

- `Guidance.md`

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

## 7. Nginx 关键原则

- `frontend-dist/` 由 Nginx 直接服务（SPA）
- `uploads/` 由 Nginx 静态映射直出
- `/api/` 代理到 FastAPI（127.0.0.1:5000）

这样可以让静态内容和上传资源绕过 Python 进程，提高吞吐并降低后端负载。

---

## 8. 常见问题速查

### 6.1 SQLite 路径写法错误

生产绝对路径必须为 4 斜杠：

```text
sqlite:////home/admin/program/MyWebsite/database/blog.db
```

### 6.2 数据库只读报错

报错：`attempt to write a readonly database`

通常是目录/文件归属错误（例如被 root 创建），修复时需同时检查：

- `database/` 目录写权限
- 数据库文件 owner/group

### 6.3 服务启动方式不兼容

FastAPI 生产环境请使用 Gunicorn + Uvicorn Worker，避免使用旧 Flask 启动方式。

---

## 9. 文档说明

- `README.md`：对外/开发者快速上手与架构概览
- `Guidance.md`：内部部署手册与避坑宝典（含保姆级生产部署教程，运维必读）
