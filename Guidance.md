# 二次开发指南（Markdown 渲染架构 + 数据库抽离）

> 目标：帮助维护者在新目录架构下快速定位代码、理解 Markdown 渲染链路，并稳定迭代数据库相关功能。

---

## 1. 新部署架构总览

统一工作区（示例用户：admin）：`/home/admin/program/MyWebsite`

- 源代码目录：`/home/admin/program/MyWebsite/code`
- 数据库目录：`/home/admin/program/MyWebsite/database`
- 日志目录：`/home/admin/program/MyWebsite/logs`
- 前端静态目录：`/home/admin/program/MyWebsite/frontend-dist`

设计目标：

1. 代码与数据物理隔离，避免发布覆盖数据库。
2. 日志独立存放，便于追踪线上故障。
3. 前端静态产物独立目录，便于 Nginx 挂载。

---

## 2. 代码结构与职责

### 2.1 前端

- `code/frontend/src/views/`：页面逻辑（Home、Programs、Fun、Blog*）
- `code/frontend/src/components/`：复用组件
- `code/frontend/src/router/index.js`：前端路由
- `code/frontend/src/utils/markdown.js`：Markdown 渲染与净化核心

### 2.2 后端

- `code/backend/app.py`：Flask 启动与蓝图注册
- `code/backend/routes/blog.py`：博客 CRUD API
- `code/backend/routes/program.py`：Program/Fun API
- `code/backend/database/db.py`：SQLAlchemy 初始化、SQLite 校验、建表与迁移
- `code/backend/models/blog.py`：博客模型
- `code/backend/services/runner.py`：Program/Fun JSON 数据处理

---

## 3. Markdown 渲染架构（最新）

渲染链路：

1. 页面输入/读取 Markdown（`BlogEditor.vue`、`BlogDetail.vue`）
2. `marked.parse(...)` 解析 Markdown
3. `DOMPurify.sanitize(...)` 白名单净化 HTML
4. 通过 `v-html` 渲染净化结果

高亮能力：

- 在 `code/frontend/src/utils/markdown.js` 使用 `marked-highlight + highlight.js`
- 仅注册必要语言（js/ts/json/xml/bash）

维护原则：

- 新增 Markdown 能力优先在 `markdown.js` 统一扩展
- 禁止在页面绕过净化直接注入 HTML
- 任何渲染策略修改要同时验证编辑预览与详情展示

---

## 4. 数据库抽离与运行约束

数据库文件固定放在：

- `/home/admin/program/MyWebsite/database/blog.db`

systemd 必配项：

- `User=admin`
- `Group=admin`
- `WorkingDirectory=/home/admin/program/MyWebsite/code/backend`
- `ExecStart=/home/admin/program/MyWebsite/code/backend/.venv/bin/gunicorn -c /home/admin/program/MyWebsite/code/deploy/gunicorn.conf.py wsgi:app`
- `Environment="SQLALCHEMY_DATABASE_URI=sqlite:////home/admin/program/MyWebsite/database/blog.db"`

> 绝对路径 URI 必须是 `sqlite:////`（4 个斜杠）。

补充说明：

- 代码仓库不会包含 `database` 目录，部署时需手动创建。
- Flask 启动后会自动创建数据库文件（若不存在）。

---

## 5. 前后端请求链路

### 5.1 Program/Fun

`Vue 页面` → `/api/*` → `routes/program.py` → `services/runner.py` → `code/backend/data.json`

### 5.2 Blog

`Vue 页面` → `/api/blog*` → `routes/blog.py` → SQLAlchemy → `database/blog.db`

---

## 6. 二次开发建议

### 6.1 页面与交互改动

优先修改：

- `code/frontend/src/views/*.vue`
- `code/frontend/src/router/index.js`
- `code/frontend/src/style.css`

### 6.2 博客字段改动

同步修改：

- 模型：`code/backend/models/blog.py`
- 路由序列化：`code/backend/routes/blog.py`
- 前端表单与展示：`BlogEditor.vue` / `BlogDetail.vue`

### 6.3 渲染能力改动

统一入口：`code/frontend/src/utils/markdown.js`

不要在单个页面增加临时渲染分支，保持全站渲染行为一致。

---

## 7. 开发与发布自检

```bash
# 后端语法检查
cd /home/admin/program/MyWebsite/code
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

## 8. 常见问题速查

- `Address already in use`
  - `sudo fuser -k 5000/tcp`
  - `sudo systemctl restart mywebsite-backend`

- `unable to open database file`
  - 检查 URI 是否为 `sqlite:////...`（4 斜杠）
  - 检查 `database` 目录是否已创建且可写

- Nginx 读不到静态文件
  - 确认已执行：`chmod +x /home/admin /home/admin/program /home/admin/program/MyWebsite`

---

## 9. 维护原则

1. 坚持 `code/database/logs/frontend-dist` 四目录隔离。
2. Markdown 渲染逻辑统一在 `code/frontend/src/utils/markdown.js` 维护。
3. 禁止将 SQLite 放回源码目录。
4. 生产变更后必须执行 `daemon-reload + restart + status + curl` 完整验收。
