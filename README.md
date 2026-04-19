# MyWebsite

MyWebsite 是一个前后端分离的个人网站项目，当前已完成图床能力、移动端适配、后端 FastAPI 重构与用户家目录隔离部署架构升级。

## 技术栈

- 前端：Vue 3 + Vite + Tailwind CSS
- 后端：FastAPI + Pydantic + Uvicorn
- 数据库：SQLite

## 核心亮点

1. 📱 **Mobile-First 响应式设计**：完美适配手机与桌面端。
2. 🖼️ **轻量级本地图床**：基于物理目录隔离的安全图片上传。
3. ⚡ **现代化极速 API**：FastAPI 驱动，自带 `/docs` 交互式文档。
4. 🛡️ **用户家目录隔离部署**：极致安全的权限闭环架构。

## 本地开发快速启动

### 前端

```bash
cd /path/to/MyWebsite/frontend
npm install
npm run dev
```

### 后端

```bash
cd /path/to/MyWebsite/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

后端默认可访问：

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## 目录说明

```text
MyWebsite/
├── backend/
├── frontend/
├── deploy/
├── README.md
└── Guidance.md
```

---

## 生产部署与运维入口

> **生产环境的从零部署与日常代码热更新，请务必严格查阅 `Deployment.md`**。
