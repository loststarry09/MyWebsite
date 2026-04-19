# 🗺️ MyWebsite 源码导读与全栈魔改指南 (Tutorial)

欢迎来到 MyWebsite 的源码世界！🎉 
无论你是刚刚接手这个项目的作者本人（用来唤醒记忆），还是偶然路过想学习 **Vue 3 + FastAPI** 现代前后端分离开发的新手，这份指南都将是你最好的“武功秘籍”。

本项目主打**“极简无痛”**，摒弃了复杂的微服务、Redis 缓存或臃肿的中间件，极其适合作为全栈入门的**实战教材**。只要你懂一点点 HTML/JS 和 Python，跟着这篇教程，你就能完全掌控这个网站！

---

## 🏗️ 第一章：上帝视角看架构 (The Big Picture)

当你克隆下代码后，整个项目分为两个完全独立的宇宙：
*   **`frontend/` (前端)**：用户的脸面。基于 Vue 3 (Composition API) + Vite + Tailwind CSS。负责长得好看、响应点击、展示数据。
*   **`backend/` (后��)**：幕后的大脑。基于 FastAPI + SQLAlchemy + SQLite。负责操作数据库、处理逻辑、保存图片。

### 🔄 一个请求的旅行路线
当用户在浏览器点击“查看博客”时，发生了什么？
1. **前端呼叫**：Vue 组件通过 `axios` 或 `fetch` 向 `/api/blog` 发送网络请求。
2. **网关指路**：生产环境中的 `Nginx` 收到请求，一看带了 `/api/` 前缀，立刻原封不动地把它转发给服务器本地的 `5000` 端口。
3. **后端接客**：FastAPI 监听着 5000 端口，路由匹配到 `@app.get("/api/blog")`，触发对应的 Python 函数。
4. **查询数据**：Python 函数通过 SQLAlchemy（ORM）向 SQLite 数据库要数据。
5. **返回数据**：FastAPI 将查到的数据打包成标准的 JSON 格式返回。
6. **前端渲染**：Vue 拿到 JSON 数据，响应式变量（`ref`）发生变化，页面瞬间刷新出博客列表！

---

## 🎨 第二章：前端源码深度解剖 (`frontend/`)

前端使用 Vite 构建，开发时极速热重载。核心代码都在 `frontend/src/` 目录下。

### 📂 核心目录与文件字典
*   **`index.html`**：一切的起点，里面有个 `<div id="app"></div>`，Vue 就会把整个网站“塞”进这个 div 里。
*   **`src/main.js` (或 `main.ts`)**：前端总司令。负责实例化 Vue，挂载路由（Router），挂载全局样式。
*   **`src/App.vue`**：网站的“骨架”。通常包含顶部的 `Navbar` 和底部的 `Footer`，中间用 `<router-view />` 挖了个坑，用来根据网址切换不同的页面。
*   **`src/router/index.js`**：导航员。配置了“什么网址对应什么组件”，比如 `path: '/blog/:id'` 对应 `BlogDetail.vue`。
*   **`src/views/`**：大页面级别的组件（如首页 `Home.vue`，博客列表 `BlogList.vue`）。
*   **`src/components/`**：可复用的小零件（如导航栏 `Navbar.vue`，Markdown 编辑器）。
*   **`src/assets/`**：放静态资源（如 CSS 全局文件、Logo 图片）。

### 🧠 Vue 3 核心语法速成
我们使用的是 Vue 3 的 `<script setup>` 语法，非常简洁：
*   **`ref`**：用来定义会变的变量。比如 `const title = ref('你好')`，在模板里用 `{{ title }}` 显示。只要 `title.value = '世界'`，页面会自动变成“世界”。
*   **`onMounted`**：页面刚加载完时执行的函数。通常在这里向后端发请求拿数据。

---

## ⚙️ 第三章：后端源码深度解剖 (`backend/`)

后端使用的是 Python 圈目前最火的 **FastAPI**，它天生支持异步，且自带 API 文档。

### 📂 核心目录与文件字典
*   **`main.py`**：后端入口。初始化 `FastAPI()`，配置跨域 `CORS`，挂载各个路由模块。
*   **`config.py`**：全局配置中心。项目里所有的绝对路径（如数据库位置、图片保存的 `uploads/` 目录）都在这里统一管理，杜��代码里到处写死路径。
*   **`database.py`**：数据库连接器。负责连接 SQLite，提供 `get_db()` 依赖函数，确保每次请求结束后自动关闭数据库连接，防止锁死。
*   **`models.py`**：数据表结构（SQLAlchemy）。定义硬盘里的数据库长什么样。例如 `class Blog(Base):` 就是一张博客表。
*   **`schemas.py`**：数据校验员（Pydantic）。定义前端传来的 JSON 或返回给前端的 JSON 长什么样。如果不符合规矩，FastAPI 会自动拦截并报错。
*   **`routers/blog.py`**：具体的业务路由。包含增删改查（CRUD）和图片上传的 API 逻辑。

### 🧠 FastAPI 核心语法速成
```python
@app.get("/api/blog/{blog_id}", response_model=schemas.BlogResponse)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    # 1. 路由装饰器：定义请求方法、路径、返回格式
    # 2. 参数注入：自动提取 URL 中的 blog_id，并向 database 要一个 db 会话
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="博客找不到啦！")
    return blog
```

---

## 🛠️ 第四章：全栈魔改实战教学 (Hands-on Modding)

光看不练假把式。接下来我们进行几个极具代表性的实战修改！

### 💡 玩法 1：纯前端修改 —— 更改网站主题色
本项目使用 Tailwind CSS，改颜色极其简单，不需要写传统的 CSS。
1. 打开 `frontend/src/components/Navbar.vue`。
2. 找到背景色 `bg-blue-600`。
3. 把它改成 `bg-emerald-600`（翠绿色）或 `bg-indigo-600`（靛蓝色）。
4. 保存代码，浏览器会自动刷新，颜色瞬间改变！Tailwind 的颜色字典可以去官网查阅。

### 💡 玩法 2：纯后端修改 —— 增加图片大小限制防呆
为了防止别人上传几个 G 的图片把服务器塞满，我们需要在上传接口加个限制。
1. 打开 `backend/routers/blog.py`，找到图片上传的路由 `@router.post("/upload")`。
2. 在处理文件保存的代码之前，加上这几行：
   ```python
   # 读取文件内容获取大小
   content = await file.read()
   if len(content) > 5 * 1024 * 1024:  # 限制为 5MB
       raise HTTPException(status_code=400, detail="图片超过 5MB 啦！")
   # 检查完大小后，千万记得把文件读取指针移回开头，否则存下来是空文件！
   await file.seek(0)
   ```

### 👑 玩法 3：全栈打通挑战 —— 给文章增加“阅读量 (Views)”功能
这是一个经典的贯穿前后端的完整流程！你需要按顺序做以下 4 步：

**第 1 步：改数据库模型 (Backend)**
打开 `backend/models.py`，在 `Blog` 类里增加一个字段：
```python
views = Column(Integer, default=0)  # 默认阅读量为 0
```
*(注意：修改模型后，由于 SQLite 不太支持复杂的动态改表，最粗暴的方法是在本地开发时删掉 `blog.db` 让它重新生成。)*

**第 2 步：改数据校验 Schema (Backend)**
打开 `backend/schemas.py`，在返回给前端的 `BlogResponse` (或类似名称的类) 里加上：
```python
views: int
```

**第 3 步：改业务路由逻辑 (Backend)**
打开 `backend/routers/blog.py`，找到获取单篇文章详情的接口 `get_blog`。在 `return blog` 之前，让阅读量 +1 并保存：
```python
blog.views += 1
db.commit()      # 保存到数据库
db.refresh(blog) # 刷新最新状态
```

**第 4 步：改前端页面显示 (Frontend)**
打开 `frontend/src/views/BlogDetail.vue`，在显示标题或日期的地方旁边，加上绑定的变量：
```html
<span class="text-gray-500 text-sm">阅读量: {{ blog.views }}</span>
```
**恭喜！你已经掌握了全栈开发的核心命脉！**

---

## 🔧 第五章：日常运维与排错必杀技 (DevOps Survival Guide)

在服务器（Ubuntu）上运行项目时，难免会遇到问题。掌握以下几招，足以应付 99% 的故障。

### 1. 后端挂了 / 报 502 Bad Gateway 怎么办？
502 说明 Nginx 还在，但 FastAPI 没响应。
*   **查看后端报错日志（最重要的一条命令）**：
    ```bash
    sudo journalctl -u mywebsite -n 100 --no-pager
    ```
    看最后几行报了什么错（比如 Python 语法错误、包没找到等）。
*   **重启后端服务**：
    ```bash
    sudo systemctl restart mywebsite
    ```
*   **查看服务状态**：
    ```bash
    sudo systemctl status mywebsite
    ```

### 2. 报 404 Not Found / 接口连不上怎么办？
大概率是 Nginx 的路由没配好。
*   检查 Nginx 配置：`sudo nano /etc/nginx/sites-available/mywebsite`。
*   **绝对红线**：代理后端的 `location /api/ { proxy_pass http://127.0.0.1:5000; }`，**5000 的末尾绝对不能有斜杠 `/`**，否则路径会被截断！
*   改完后重启 Nginx：`sudo systemctl reload nginx`。

### 3. 报 "attempt to write a readonly database" 怎么办？
这是经典的 Linux 权限地狱问题。SQLite 需要对所在的文件夹有写权限。
*   执行权限修复（确保你是以 admin 身份）：
    ```bash
    sudo chown -R admin:admin /home/admin/program/MyWebsite/database
    ```

### 4. 前端页面白屏 / 样式没更新怎么办？
如果是本地开发，看看终端 `npm run dev` 有没有报错。
如果是服务器生产环境，说明你刚拉了代码但没重新打包！
*   去前端目录执行：
    ```bash
    npm run build
    rm -rf /home/admin/program/MyWebsite/frontend-dist/*
    cp -r dist/* /home/admin/program/MyWebsite/frontend-dist/
    ```
*   然后在浏览器按 `Ctrl + F5` 强制刷新缓存。

---

## 🚀 写在最后

软件工程没有魔法，所有的 Bug 都在日志里，所有的逻辑都在源码中。
勇敢地去修改代码吧！哪怕弄坏了，敲一句 `git restore .` 就能时光倒流。

**Happy Coding, Hacker! 愿你在 MyWebsite 的源码里玩得开心！**