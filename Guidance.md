# 二次开发指南（Markdown 渲染架构 + 数据库抽离）

> 目标：帮助维护者快速理解本项目最新的前后端架构、Markdown 渲染链路、SQLite 数据库隔离方案，并安全进行功能迭代。

---

## 1. 架构总览

### 1.1 技术栈

- 前端：Vue 3 + Vite + Tailwind
- 后端：Flask + SQLAlchemy
- 存储：SQLite（博客）+ JSON（program/fun）

### 1.2 部署基线（User-level Deployment）

统一使用用户目录：

- 代码目录：`/home/admin/program/MyWebsite`
- 前端静态目录：`/home/admin/program/mywebsite-frontend`
- 数据库目录：`/home/admin/program/MyWebsiteDatabase`
- Gunicorn 运行用户：`admin`

> 通过“代码目录/静态目录/数据库目录”三段隔离，减少权限串扰和误删风险。

---

## 2. 代码结构与职责

### 2.1 前端核心目录

- `frontend/src/views/`：页面级逻辑（Home、Programs、Fun、Blog*）
- `frontend/src/components/`：复用组件层
- `frontend/src/router/index.js`：路由注册与页面映射
- `frontend/src/utils/markdown.js`：Markdown 渲染安全管线（核心）

### 2.2 后端核心目录

- `backend/app.py`：Flask 应用与蓝图注册入口
- `backend/routes/blog.py`：博客 CRUD API
- `backend/routes/program.py`：Program/Fun API
- `backend/database/db.py`：数据库初始化、SQLite 安全校验、建表与迁移
- `backend/models/blog.py`：博客模型与标签模型
- `backend/services/runner.py`：Program/Fun 的 JSON 读写逻辑

---

## 3. Markdown 渲染架构（最新）

### 3.1 渲染链路

1. 页面输入 Markdown（`BlogEditor.vue`）或加载 Markdown（`BlogDetail.vue`）
2. `marked.parse(...)` 生成 HTML（支持异步）
3. `DOMPurify.sanitize(...)` 进行白名单净化
4. `v-html` 渲染净化后的 HTML

### 3.2 高亮链路

在 `frontend/src/utils/markdown.js` 中：

- `highlight.js` 只注册所需语言（js/ts/json/xml/bash）
- 通过 `marked-highlight` 接入 `marked`
- 统一 `langPrefix`，保证代码块样式稳定

### 3.3 安全边界

- 允许标签和属性走白名单
- 禁止直接把未净化 HTML 注入页面
- 新增 Markdown 功能时，优先扩展 `markdown.js` 白名单与解析配置，不要在页面临时“绕过净化”

### 3.4 维护建议

- 若新增语言高亮：只在 `markdown.js` 注册必要语言，避免打包体积膨胀
- 若修改渲染配置：同时验证 `BlogEditor` 预览和 `BlogDetail` 展示
- 若引入新插件：先评估 XSS 风险，再接入

---

## 4. 数据库抽离与路径约束

### 4.1 为什么要抽离数据库目录

将 SQLite 文件放到独立目录 `/home/admin/program/MyWebsiteDatabase`，可实现：

- 与代码仓库解耦，避免 `git pull`/部署覆盖数据库
- 与前端静态目录解耦，降低误操作风险
- 权限模型更清晰（Gunicorn 用 `admin` 运行，天然可读写）

### 4.2 必须遵守的 URI 规则

生产环境统一使用：

```bash
SQLALCHEMY_DATABASE_URI=sqlite:////home/admin/program/MyWebsiteDatabase/blog.db
```

> 必须是 `sqlite:////`（4 个斜杠，绝对路径）。

### 4.3 systemd 建议配置

`/etc/systemd/system/mywebsite-backend.service` 关键项：

- `User=admin`
- `Group=admin`
- `WorkingDirectory=/home/admin/program/MyWebsite/backend`
- `ExecStart=/home/admin/program/MyWebsite/backend/.venv/bin/gunicorn -c /home/admin/program/MyWebsite/deploy/gunicorn.conf.py wsgi:app`
- `Environment="SQLALCHEMY_DATABASE_URI=sqlite:////home/admin/program/MyWebsiteDatabase/blog.db"`

修改后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl restart mywebsite-backend
```

---

## 5. 前后端数据流

### 5.1 Program/Fun

`Vue (Programs/Fun)` → `/api/*` → `routes/program.py` → `services/runner.py` → `backend/data.json`

### 5.2 Blog

`Vue (BlogList/BlogDetail/BlogEditor)` → `/api/blog*` → `routes/blog.py` → SQLAlchemy → SQLite

---

## 6. 二次开发改动建议

### 6.1 改前端页面

优先改：

- 页面：`frontend/src/views/*.vue`
- 路由：`frontend/src/router/index.js`
- 公共样式：`frontend/src/style.css`

### 6.2 改博客字段/行为

同步修改：

- 模型：`backend/models/blog.py`
- API 序列化：`backend/routes/blog.py`
- 前端展示与编辑：`BlogDetail.vue` / `BlogEditor.vue`

### 6.3 改 Markdown 能力

统一入口：`frontend/src/utils/markdown.js`

不要直接在页面写临时渲染逻辑；应保持“解析 + 净化 + 渲染”一致链路。

---

## 7. 更新与自检流程

### 7.1 开发自检

```bash
cd /home/admin/program/MyWebsite
python -m compileall backend

cd /home/admin/program/MyWebsite/frontend
npm run build
```

### 7.2 部署后检查

```bash
sudo systemctl status mywebsite-backend --no-pager
curl http://127.0.0.1:5000/api/programs
curl -I http://your-domain.com
```

### 7.3 常见故障速查

- `Address already in use`：

```bash
sudo fuser -k 5000/tcp
sudo systemctl restart mywebsite-backend
```

- `unable to open database file`：优先检查 `SQLALCHEMY_DATABASE_URI` 是否为 `sqlite:////...`（4 斜杠）以及数据库目录可写。

---

## 8. 长期维护原则

1. 保持 `/home/admin/program/` 目录约定一致，避免多路径并存。
2. Markdown 渲染能力只在 `frontend/src/utils/markdown.js` 统一演进。
3. SQLite 物理文件与代码目录分离，禁止回退到仓库目录内存储数据库。
4. 生产变更后统一走 `systemctl daemon-reload && systemctl restart mywebsite-backend` 验证。 
