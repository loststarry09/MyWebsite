# MyWebsiteV1.1

前后端分离项目：

- 前端：Vue 3 + Vite + Tailwind（`frontend/`）
- 后端：Flask（`backend/`）
- API 前缀：`/api`

---

## 1. 本地开发（兼顾联调）

> 以下示例中，项目目录统一以 `MyWebsiteV1.1` 命名。

### 1.1 环境准备（Windows 11）

- 安装 Python 3.10+（勾选 `Add python.exe to PATH`）
- 安装 Node.js 18+（建议 LTS）
- 使用 PowerShell 7 或 Windows PowerShell

### 1.2 启动后端（Windows PowerShell）

```powershell
cd C:\dev\MyWebsiteV1.1\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:APP_DEBUG="1"
$env:APP_HOST="127.0.0.1"
$env:APP_PORT="5000"
python app.py
```

后端校验：

```powershell
curl http://127.0.0.1:5000/api/programs
```

### 1.3 启动前端（Windows PowerShell）

```powershell
cd C:\dev\MyWebsiteV1.1\frontend
npm ci
npm run dev
```

### 1.4 环境准备（Ubuntu 24.04，可选）

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx
```

> 建议 Python 3.10+，Node 18+。

### 1.5 启动后端（Ubuntu）

```bash
cd /path/to/MyWebsiteV1.1/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
APP_DEBUG=1 APP_HOST=0.0.0.0 APP_PORT=5000 python app.py
```

后端校验：

```bash
curl http://127.0.0.1:5000/api/programs
```

### 1.6 启动前端（Ubuntu）

```bash
cd /path/to/MyWebsiteV1.1/frontend
npm ci
npm run dev
```

### 1.7 Windows 11 本地调试建议

- 后端：保持 `APP_DEBUG=1`，在 VS Code 中以 Python 解释器 `.venv` 启动 `backend/app.py` 进行断点调试
- 前端：在 `npm run dev` 启动后，使用浏览器开发者工具（F12）查看 Network / Console

前端开发时已内置代理：

- `http://127.0.0.1:5173/api/*` → `http://127.0.0.1:5000/api/*`
- 可通过环境变量覆盖代理目标：`VITE_API_PROXY_TARGET=http://127.0.0.1:5000 npm run dev`

---

## 2. Ubuntu 24.04 生产部署（Gunicorn + Nginx + systemd）

下面以：

- 项目目录：`/var/www/MyWebsiteV1.1`
- 前端静态目录：`/var/www/mywebsite-frontend`
- 域名：`your-domain.com`

为例，请按实际替换。

### 2.1 拉取代码并安装依赖

```bash
sudo mkdir -p /var/www
cd /var/www
sudo git clone <your-repo-url> MyWebsiteV1.1
sudo chown -R $USER:$USER /var/www/MyWebsiteV1.1
```

后端依赖：

```bash
cd /var/www/MyWebsiteV1.1/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

前端构建：

```bash
cd /var/www/MyWebsiteV1.1/frontend
npm ci
npm run build
sudo mkdir -p /var/www/mywebsite-frontend
sudo rsync -av --delete dist/ /var/www/mywebsite-frontend/
```

### 2.2 手动验证 Gunicorn

```bash
cd /var/www/MyWebsiteV1.1/backend
source .venv/bin/activate
APP_DEBUG=0 .venv/bin/gunicorn -c /var/www/MyWebsiteV1.1/deploy/gunicorn.conf.py wsgi:app
```

新开终端测试：

```bash
curl http://127.0.0.1:5000/api/programs
```

### 2.3 配置 systemd（托管 Gunicorn）

复制模板并启用：

```bash
sudo cp /var/www/MyWebsiteV1.1/deploy/mywebsite-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mywebsite-backend
sudo systemctl start mywebsite-backend
sudo systemctl status mywebsite-backend --no-pager
```

常用运维命令：

```bash
sudo systemctl restart mywebsite-backend
sudo journalctl -u mywebsite-backend -f
```

### 2.4 配置 Nginx

```bash
sudo cp /var/www/MyWebsiteV1.1/deploy/mywebsite.nginx.conf /etc/nginx/sites-available/mywebsite
sudo ln -sf /etc/nginx/sites-available/mywebsite /etc/nginx/sites-enabled/mywebsite
sudo nginx -t
sudo systemctl reload nginx
```

### 2.5 HTTPS（推荐）

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 3. 项目更新与服务重启指南（Ubuntu 24.04）

> 适用场景：前端（Vue3 + Vite）已构建为 `dist`，后端 Flask 通过 Gunicorn + systemd 托管，Nginx 提供对外访问。

### 3.1 查看服务状态

为什么要做：先确认当前服务状态，避免在异常状态下直接更新。

```bash
sudo systemctl status mywebsite-backend --no-pager
sudo systemctl is-active mywebsite-backend
```

用途：确认服务是否已启动、是否异常退出。

### 3.2 停止后端服务

为什么要做：更新后端代码前先停服务，避免更新过程中请求命中不完整代码。

```bash
sudo systemctl stop mywebsite-backend
sudo systemctl status mywebsite-backend --no-pager
```

用途：确保 Flask/Gunicorn 进程已停止，再执行代码替换。

### 3.3 更新后端代码

为什么要做：让服务启动时加载最新后端逻辑与依赖。

```bash
cd /var/www/MyWebsiteV1.1
git pull
cd /var/www/MyWebsiteV1.1/backend
source .venv/bin/activate
pip install -r requirements.txt
```

用途：更新 `backend` 目录并同步依赖。  
注意：若非 `git pull`，请直接替换 `/var/www/MyWebsiteV1.1/backend`；同时确认部署用户对该目录有读写权限。

### 3.4 更新前端代码（重要）

为什么要做：前端部署的是构建产物 `dist`，不重新构建不会生效。

```bash
cd /path/to/MyWebsiteV1.1/frontend
npm ci
npm run build
```

```bash
rsync -av --delete /path/to/MyWebsiteV1.1/frontend/dist/ /var/www/mywebsite-frontend/
```

用途：先本地生成最新 `dist`，再覆盖服务器静态目录。  
注意：`--delete` 会删除目标目录中源目录不存在的文件，执行前请确认源路径为正确的 `dist/`。  
重点：只改源码但不执行 `npm run build`，线上页面不会更新。

### 3.5 重新启动服务

为什么要做：让 systemd 重新拉起 Gunicorn，加载更新后的代码与依赖。

```bash
sudo systemctl restart mywebsite-backend
sudo systemctl status mywebsite-backend --no-pager
```

用途：推荐 `restart`，一次完成停止与启动，减少遗漏风险。

### 3.6 验证更新是否生效

为什么要做：确认前后端都已切换到新版本。

```bash
curl http://127.0.0.1:5000/api/programs
curl -I http://your-domain.com
```

用途：`curl` 验证 API 与站点响应；同时在浏览器访问首页与关键页面确认前端更新。

### 3.7 查看日志（排查问题）

为什么要做：当服务启动失败、接口报错时，日志是第一定位入口。

```bash
sudo journalctl -u mywebsite-backend -n 100 --no-pager
sudo journalctl -u mywebsite-backend -f
```

用途：查看最近日志与实时日志，快速定位部署或运行错误。

### 3.8 Nginx 相关说明（简要）

为什么要做：只有修改了 Nginx 配置时才需要 reload，使配置生效且不中断服务。

```bash
sudo nginx -t
sudo systemctl reload nginx
```

用途：先校验配置，再平滑重载。

### 3.9 常见问题

- 修改代码后未生效：通常是忘记重启后端服务，执行 `sudo systemctl restart mywebsite-backend`。  
- 前端更新无变化：通常是未重新构建，执行 `npm run build` 并重新覆盖 `dist`。  
- 权限问题：若出现 `Permission denied`，检查部署用户对 `/var/www/MyWebsiteV1.1` 与 `/var/www/mywebsite-frontend` 的目录权限。

---

## 4. 项目里已做的部署/调试适配优化

1. **后端环境化启动参数**
   - `APP_HOST`、`APP_PORT`、`APP_DEBUG` 可配置
   - 本地调试和生产部署共用同一套应用代码

2. **后端反向代理适配**
   - 启用 `ProxyFix`，更好处理 Nginx 转发后的 `X-Forwarded-*` 头

3. **新增 Gunicorn 入口与配置模板**
   - `backend/wsgi.py`
   - `deploy/gunicorn.conf.py`

4. **新增 systemd 与 Nginx 模板**
   - `deploy/mywebsite-backend.service`
   - `deploy/mywebsite.nginx.conf`

5. **前端本地联调优化**
   - Vite 增加 `/api` 开发代理
   - 继续使用相对路径请求，生产走同域反向代理

6. **博客时间显示时区修正**
   - 后端博客时间以 UTC（`...Z`）保存
   - 前端展示时转换为浏览器本地时区，避免出现创建时间少 8 小时等偏差

---

## 5. 常见故障排查

### 5.1 前端请求 404/502

- 确认后端是否在本机 `127.0.0.1:5000` 运行
- 确认 Nginx `location /api/` 生效并已 reload
- 通过 `curl http://127.0.0.1:5000/api/programs` 先验证后端自身

### 5.2 页面空白或路由刷新 404

- 确认 Nginx 对 `/` 使用：`try_files $uri $uri/ /index.html;`

### 5.3 后端更新不生效

- 执行 `sudo systemctl restart mywebsite-backend`
- 查看日志 `sudo journalctl -u mywebsite-backend -f`

### 5.4 前端更新不生效

- 重新构建并覆盖静态目录：
  - `npm run build`
  - `rsync -av --delete dist/ /var/www/mywebsite-frontend/`

---

## 6. 开发校验命令

```bash
# 后端语法校验（项目根目录）
cd /path/to/MyWebsiteV1.1
python -m compileall backend

# 前端构建校验
cd /path/to/MyWebsiteV1.1/frontend
npm run build
```
