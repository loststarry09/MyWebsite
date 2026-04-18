# 源码结构与修改指南（中级开发者版）

> 目标：拿到项目后，10 分钟内能定位并改动核心功能。
> 本文档示例统一以项目目录名 `MyWebsite` 为准。

## 一、文档目标

你应能快速完成：

- 找到“该改哪一层”（页面、路由、接口、后端逻辑）
- 改页面内容/跳转/样式
- 改接口地址与请求逻辑
- 新增项目数据（前端静态 or 后端接口）
- 理解前后端一次请求的完整链路

---

## 二、项目结构（按职责划分）

### 前端（Vue）

- `frontend/src/views/`  
  页面级逻辑（本项目对应你说的 `pages/` 职责，当前目录名是 `views/`）。
  - 改页面文案、按钮、交互：优先进这里。
  - 示例：`Home.vue`、`Programs.vue`、`ProgramDetail.vue`、`Fun.vue`

- `frontend/src/components/`  
  复用组件层（本项目有 `NavCard.vue`）。
  - 改“多个页面复用”的卡片/通用 UI，改这里。

- `frontend/src/router/index.js`  
  前端路由入口。
  - 新页面接入、路径调整、详情页参数路由都在这里。

- `frontend/src/App.vue`  
  全局壳层（头部导航 + `<RouterView />`）。
  - 改全站导航、全局布局优先在这里。

- `frontend/src/main.js`  
  应用挂载入口（创建 app、挂载 router）。

- `frontend/src/style.css`  
  全局基础样式。

- `frontend/src/api/index.js`  
  **当前仓库不存在该文件**。当前 axios 调用直接写在各 `views`（如 `Programs.vue`、`Fun.vue`）。
  - 需要切换后端地址时，优先通过 `VITE_API_PROXY_TARGET` 与 Nginx 代理调整，不建议直接改页面里的 `/api/*`。

### 后端（Flask）

- `backend/app.py`  
  Flask 应用入口，注册蓝图到 `/api` 前缀。
  - API 总入口挂载位置看这里。

- `backend/database/db.py`  
  数据库初始化与自动建表入口（SQLite `blog.db`），并处理历史 JSON 博客迁移。
  - 改数据库初始化、迁移逻辑、SQLite 参数时看这里。

- `backend/models/blog.py`  
  博客与标签的数据模型（SQLAlchemy）。
  - 改字段结构（如新增字段）时，需同步路由序列化逻辑。

- `backend/routes/program.py`  
  接口定义层（请求参数校验、HTTP 状态码、调用 service）。
  - 改“接口路径/参数/返回格式”，改这里。

- `backend/services/runner.py`  
  Program/Fun 的 JSON 数据读写层（`data.json`）。
  - 改“程序与娱乐”数据来源/落盘逻辑，改这里。

- `backend/routes/blog.py`  
  博客 CRUD 路由层（基于 SQLAlchemy，不走 `runner.py`）。
  - 改博客接口字段、校验、查询条件、返回格式，改这里。

---

## 三、高频修改入口（核心🔥）

## 前端常改文件

- `frontend/src/views/Home.vue`  
  首页导航卡片：博客 URL、按钮文案、按钮跳转路径
- `frontend/src/views/Programs.vue`  
  项目列表展示、添加项目弹窗、`/api/programs` 与 `/api/program` 调用
- `frontend/src/views/ProgramDetail.vue`  
  项目详情展示逻辑（当前基于 `src/data/programs.js`）
- `frontend/src/router/index.js`  
  路由 path/name/component 映射
- `frontend/src/App.vue`  
  顶部导航入口
- `frontend/src/style.css`  
  全局样式
- `frontend/src/data/programs.js`  
  前端静态项目数据（详情页当前直接依赖它）

## 后端常改文件

- `backend/routes/program.py`  
  `/api/programs`、`/api/program`、`/api/fun` 等接口定义
- `backend/services/runner.py`  
  `get_programs` / `add_program` / `get_fun_items` / `add_fun_item`
- `backend/data.json`  
  当前持久化数据文件（程序列表与娱乐项）
- `backend/routes/blog.py`  
  博客 CRUD 接口与时间字段（`createdAt` / `updatedAt`）生成逻辑（UTC）
- `backend/database/db.py`、`backend/models/blog.py`  
  博客数据库初始化与模型定义（SQLite + SQLAlchemy）

## 博客时间显示规则（新增）

- 后端以 UTC ISO 字符串保存博客时间（示例：`2026-04-12T15:17:00Z`）。
- 前端展示时需转换为用户浏览器本地时区，避免“创建于 23:17 却显示 15:17”的时差问题。

---

## 四、常见修改场景（含修改前/后示例）

### 1）修改博客跳转 URL

- 文件路径：`/path/to/MyWebsite/frontend/src/views/Home.vue`
- 修改位置：博客卡片 `href`

```vue
<!-- 修改前 -->
<NavCard
  title="博客"
  subtitle="打开外部博客"
  href="https://example.com"
  :external="true"
/>
```

```vue
<!-- 修改后 -->
<NavCard
  title="博客"
  subtitle="打开外部博客"
  href="https://your-blog-domain.com"
  :external="true"
/>
```

### 2）修改首页按钮内容或跳转路径

- 文件路径：`/path/to/MyWebsite/frontend/src/views/Home.vue`
- 修改位置：任意 `NavCard` 的 `title/subtitle/to`

```vue
<!-- 修改前 -->
<NavCard title="我的程序" subtitle="查看项目列表" to="/programs" />
```

```vue
<!-- 修改后 -->
<NavCard title="项目中心" subtitle="查看全部项目" to="/programs" />
```

```vue
<!-- 修改前 -->
<NavCard title="娱乐" subtitle="轻松一下" to="/fun" />
```

```vue
<!-- 修改后（改跳转） -->
<NavCard title="娱乐" subtitle="轻松一下" to="/coming-soon" />
```

### 3）修改 API 基础地址（localhost → 服务器）

- 推荐方式：**保持前端代码使用相对路径 `/api/*` 不变**，通过代理层切换目标地址。
- 本地开发：
  - 临时切换代理目标：
    - `VITE_API_PROXY_TARGET=http://127.0.0.1:5000 npm run dev`
  - 若后端在其他主机，替换为对应地址即可。
- 生产环境：
  - 修改 Nginx 的 `location /api/` 反向代理到后端服务。
- 不推荐在页面里把 `/api/*` 硬编码成完整域名（会增加环境切换成本）。

```js
// 当前推荐写法（保留相对路径）
await axios.get('/api/programs')
await axios.post('/api/program', payload)
```

```js
// Fun.vue 同理
await axios.get('/api/fun')
await axios.post('/api/fun', payload)
```

### 4）添加一个新项目（两种方式）

#### 方式 A：前端写死

- 文件路径：`/path/to/MyWebsite/frontend/src/data/programs.js`
- 修改位置：`programs` 数组新增对象

```js
// 修改前（节选）
export const programs = [
  {
    id: 'focus-timer',
    name: '专注计时器',
    summary: '一个轻量的番茄钟工具，支持自定义时长与阶段提醒。',
    stack: ['Vue 3', 'Tailwind CSS'],
    status: '进行中',
    repoUrl: '',
    demoUrl: '',
  },
]
```

```js
// 修改后（新增一项）
export const programs = [
  {
    id: 'focus-timer',
    name: '专注计时器',
    summary: '一个轻量的番茄钟工具，支持自定义时长与阶段提醒。',
    stack: ['Vue 3', 'Tailwind CSS'],
    status: '进行中',
    repoUrl: '',
    demoUrl: '',
  },
  {
    id: 'new-tool',
    name: '新工具',
    summary: '这是新增项目',
    stack: ['Vue 3', 'Flask'],
    status: '规划中',
    repoUrl: '',
    demoUrl: '',
  },
]
```

#### 方式 B：后端接口返回

- 文件路径：
  - 接口定义：`/path/to/MyWebsite/backend/routes/program.py`
  - 数据逻辑：`/path/to/MyWebsite/backend/services/runner.py`
  - 数据落盘：`/path/to/MyWebsite/backend/data.json`
- 修改位置：调用现有 `POST /api/program`，或直接写入 `data.json` 的 `programs` 数组
- 重要说明：`Programs.vue` 列表页可读取后端数据，但 `ProgramDetail.vue` 详情页当前读取 `frontend/src/data/programs.js` 静态数据。
  - 若你希望“后端新增项目”也能进入详情页，需要同步改 `ProgramDetail.vue` 的数据来源。

```json
// data.json 修改前（节选）
{
  "programs": [
    {
      "id": "focus-timer",
      "name": "专注计时器"
    }
  ],
  "fun": []
}
```

```json
// data.json 修改后（节选）
{
  "programs": [
    {
      "id": "new-tool",
      "name": "新工具",
      "summary": "这是新增项目",
      "stack": ["Vue 3", "Flask"],
      "status": "规划中"
    },
    {
      "id": "focus-timer",
      "name": "专注计时器"
    }
  ],
  "fun": []
}
```

### 5）修改页面样式（颜色/布局）

- 文件路径：
  - 页面局部样式类：`/path/to/MyWebsite/frontend/src/views/*.vue`
  - 全局基础样式：`/path/to/MyWebsite/frontend/src/style.css`
- 修改位置：Tailwind 类名 / 全局 CSS

```vue
<!-- App.vue 修改前 -->
<div class="min-h-screen bg-[#F7F5F2] text-gray-800">
```

```vue
<!-- App.vue 修改后（改全局背景） -->
<div class="min-h-screen bg-slate-100 text-gray-800">
```

```css
/* style.css 修改前 */
body {
  margin: 0;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
```

```css
/* style.css 修改后（示例：全局字体与背景） */
body {
  margin: 0;
  font-family: "Segoe UI", Inter, sans-serif;
  background: #f1f5f9;
}
```

---

## 五、前后端交互说明（简洁版）

### Program/Fun 请求链路

1. Vue 页面触发请求（如 `Programs.vue` 的 `axios.get('/api/programs')`）  
2. 请求进入 Flask：`app.py` 把蓝图挂载在 `/api`  
3. 路由层 `routes/program.py` 匹配接口并校验参数  
4. 调用 `services/runner.py` 读写内存 + `data.json`  
5. Flask 返回 JSON  
6. Vue 收到数据后更新 `ref`/`computed`，模板自动渲染

### Blog 请求链路

1. Vue 页面触发请求（如 `BlogList.vue` 的 `axios.get('/api/blog')`）  
2. 请求进入 `routes/blog.py`  
3. 使用 SQLAlchemy 访问 SQLite（`backend/blog.db`）  
4. 路由层完成字段校验、序列化与统一响应  
5. Vue 端据响应渲染列表/详情/编辑状态

---

## 六、开发与修改流程

## 前端

- 开发：  
  `cd /path/to/MyWebsite/frontend && npm run dev`
- 修改后：Vite 自动热更新
- 构建：  
  `cd /path/to/MyWebsite/frontend && npm run build`

## 后端

- 启动：  
  `cd /path/to/MyWebsite/backend && APP_DEBUG=1 python app.py`
- 修改后：
  - `APP_DEBUG=1` 时，Flask 开发服务支持自动重载
  - 生产环境（Gunicorn/systemd）修改后需 `sudo systemctl restart mywebsite-backend`

---

## 七、修改后自检清单（推荐每次都跑）

```bash
# 项目根目录
cd /path/to/MyWebsite
python -m compileall backend

# 前端构建校验
cd /path/to/MyWebsite/frontend
npm run build
```

浏览器/接口人工校验：

- 关键页面可打开（`/`、`/programs`、`/fun`、`/blog`）
- 关键接口可返回（`/api/programs`、`/api/fun`、`/api/blog`）
- 新增/编辑功能至少手动走一遍（项目新增、娱乐新增、博客新增/编辑）

---

## 八、常见问题（简洁版）

- 修改未生效  
  - 前端：确认 dev 服务在跑；生产环境确认已重新 `npm run build` 并替换静态文件  
  - 后端：确认已重启 Flask/Gunicorn

- API 报错/请求失败  
  - 检查后端是否启动在 `5000`  
  - 检查前端请求路径是否仍指向正确 `/api/*` 或服务器域名

- 路由跳转异常  
  - 核对 `frontend/src/router/index.js` 是否注册了目标路径  
  - 核对 `RouterLink` 的 `to` 是否拼写一致

- 跨域问题  
  - 若前端与后端不同域，后端需增加 CORS 配置  
  - 同域反向代理（Nginx `/api`）可避免大多数跨域问题
