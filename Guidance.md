# 源码结构与修改指南（解耦部署 + Markdown 渲染链路）

> 目标：让维护者快速理解 `/home/admin/program/MyWebsite/` 下的物理隔离架构，并准确修改前端 Markdown 渲染逻辑。

---

## 一、全局路径与部署约定

统一工作区（示例用户：admin）：`/home/admin/program/MyWebsite/`

- 源代码路径：`/home/admin/program/MyWebsite/code/`
- 数据库存放：`/home/admin/program/MyWebsite/database/`
- 日志目录：`/home/admin/program/MyWebsite/logs/`
- 前端静态产物：`/home/admin/program/MyWebsite/frontend-dist/`

> 文档中涉及源码路径时，统一使用 `/home/admin/program/MyWebsite/code/`，不再使用旧的 `/path/to/MyWebsite/` 或 `/var/www/...` 写法。

---

## 二、项目结构

### 2.1 代码目录速览（`/home/admin/program/MyWebsite/code/`）

前端核心：

- `frontend/src/views/`：页面逻辑（Home、Programs、Fun、Blog*）
- `frontend/src/components/`：复用组件
- `frontend/src/router/index.js`：前端路由
- `frontend/src/utils/markdown.js`：Markdown 渲染与净化核心

后端核心：

- `backend/app.py`：Flask 启动与蓝图注册
- `backend/routes/blog.py`：博客 CRUD API
- `backend/routes/program.py`：Program/Fun API
- `backend/database/db.py`：SQLAlchemy 初始化、SQLite 校验、建表与迁移
- `backend/models/blog.py`：博客模型
- `backend/services/runner.py`：Program/Fun JSON 数据处理

### 2.2 服务器部署物理拓扑

工作区采用四目录平级解耦：

- `code/`：仅存放 Git 管理的源代码与部署脚本
- `database/`：仅存放 SQLite 数据文件（`blog.db`）
- `logs/`：仅存放 Gunicorn/应用运行日志
- `frontend-dist/`：仅存放前端构建产物（Nginx 直接挂载）

关键收益：

- `blog.db` 被剥离到 `database/` 后，后续无论 `git pull`、回滚代码，甚至误执行 `rm -rf code`，用户数据仍安全保留。
- 代码、数据、日志权限边界清晰，排障与运维成本显著降低。

---

## 三、后端与数据库运行约束

数据库文件固定路径：

- `/home/admin/program/MyWebsite/database/blog.db`

systemd 必配项：

- `User=admin`
- `Group=admin`
- `WorkingDirectory=/home/admin/program/MyWebsite/code/backend`
- `ExecStart=/home/admin/program/MyWebsite/code/backend/.venv/bin/gunicorn -c /home/admin/program/MyWebsite/code/deploy/gunicorn.conf.py wsgi:app`
- `Environment="SQLALCHEMY_DATABASE_URI=sqlite:////home/admin/program/MyWebsite/database/blog.db"`

> SQLite 绝对路径 URI 必须是 `sqlite:////`（4 个斜杠）。

---

## 四、前端关键目录与修改入口

- 页面与交互：`/home/admin/program/MyWebsite/code/frontend/src/views/*.vue`
- 路由：`/home/admin/program/MyWebsite/code/frontend/src/router/index.js`
- 全局样式：`/home/admin/program/MyWebsite/code/frontend/src/style.css`
- Markdown 渲染统一入口：`/home/admin/program/MyWebsite/code/frontend/src/utils/markdown.js`

---

## 五、前后端交互说明

### 5.1 Program/Fun

`Vue 页面` → `/api/*` → `routes/program.py` → `services/runner.py` → `backend/data.json`

### 5.2 Blog

`Vue 页面` → `/api/blog*` → `routes/blog.py` → SQLAlchemy → `database/blog.db`

---

## 六、Markdown 渲染与高亮机制

### 6.1 解析与防御

1. 后端只返回 Markdown 纯文本（不返回已拼接的危险 HTML）。
2. 前端使用 `marked` 将 Markdown 解析为 HTML。
3. 解析结果立即进入 `DOMPurify.sanitize(...)` 进行净化。
4. 净化后的结果再通过 `v-html` 渲染到页面。

### 6.2 防 XSS 与高亮共存的关键点

- `highlight.js` 会为代码片段注入 `hljs` 等 `class`。
- 若 `DOMPurify` 不允许 `class`，这些高亮类会被清洗掉，最终“有代码块但无高亮”。
- 因此必须确保净化配置保留 `class`（可用 `ADD_ATTR: ['class']`，或与当前实现一致在 `ALLOWED_ATTR` 中包含 `class`）。

### 6.3 样式与冲突处理

- 外层统一使用 Tailwind Typography 的 `.prose` 托管正文排版。
- `.prose` 会影响 `<pre>` 默认样式，可能覆盖代码块背景色。
- 在 Vue 组件使用 `<style scoped>` + `:deep(.prose pre)` 并配合 `!important` 强制覆写背景（如 `#1f2937`），即可稳定呈现深色代码块。
- 建议同时保留 `:deep(.prose pre code)` 的透明背景覆写，避免双层背景冲突。

---

## 七、开发与发布自检

```bash
# 后端语法检查
cd /home/admin/program/MyWebsite/code/
python -m compileall backend

# 前端构建检查
cd /home/admin/program/MyWebsite/code/frontend
npm run build
```

部署后核对：

```bash
sudo systemctl status mywebsite-backend --no-pager
curl http://127.0.0.1:5000/api/programs
curl -I http://your-domain.com
```

---

## 八、常见问题速查

- `Address already in use`
  - `sudo fuser -k 5000/tcp`
  - `sudo systemctl restart mywebsite-backend`

- `unable to open database file`
  - 检查 URI 是否为 `sqlite:////...`（4 斜杠）
  - 检查 `database/` 目录是否已创建且可写

- `attempt to write a readonly database`
  - 检查 `database/` 与 `blog.db` 所有者是否为运行用户（如 `admin`）
  - 避免使用 `sudo` 创建或调试数据库目录

- Nginx 读不到静态文件
  - 确认已执行：`chmod +x /home/admin /home/admin/program /home/admin/program/MyWebsite`

---

## 九、维护原则

1. 坚持 `code/database/logs/frontend-dist` 四目录物理隔离。
2. Markdown 渲染逻辑统一在 `frontend/src/utils/markdown.js` 维护，禁止页面私有分叉实现。
3. 禁止将 SQLite 放回源码目录。
4. 生产变更后必须执行 `daemon-reload + restart + status + curl` 完整验收。
