# MyWebsite

前后端分离项目：

- 前端：Vue 3 + Vite + Tailwind（`frontend/`）
- 后端：Flask（`backend/`）
- API 前缀：`/api`

---

## 1. 本地开发（兼顾联调）

> 以下示例中，项目目录统一以 `MyWebsite` 命名。

### 1.1 环境准备（Windows 11）

- 安装 Python 3.10+（勾选 `Add python.exe to PATH`）
- 安装 Node.js 18+（建议 LTS）
- 使用 PowerShell 7 或 Windows PowerShell

### 1.2 启动后端（Windows PowerShell）

```powershell
cd C:\dev\MyWebsite\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:APP_DEBUG="1"
$env:APP_HOST="127.0.0.1"
$env:APP_PORT="5000"
$env:SQLALCHEMY_DATABASE_URI="sqlite:///blog.db"
python app.py
```

后端校验：

```powershell
curl http://127.0.0.1:5000/api/programs
```

### 1.3 启动前端（Windows PowerShell）

```powershell
cd C:\dev\MyWebsite\frontend
npm ci
npm run dev
```

### 1.4 环境准备（Ubuntu 24.04，可选）

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip nodejs npm nginx rsync psmisc  # psmisc 提供 fuser
```

> 建议 Python 3.10+，Node 18+。

### 1.5 启动后端（Ubuntu）

```bash
cd /path/to/MyWebsite/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
APP_DEBUG=1 APP_HOST=0.0.0.0 APP_PORT=5000 SQLALCHEMY_DATABASE_URI=sqlite:///blog.db python app.py
```

后端校验：

```bash
curl http://127.0.0.1:5000/api/programs
```

### 1.6 启动前端（Ubuntu）

```bash
cd /path/to/MyWebsite/frontend
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

### 前置说明（强烈建议先读）

本项目采用 **用户目录部署方案（User-level Deployment）**，统一放在 `/home/admin/program/` 下，目标是彻底规避 Web 目录部署时常见的 `www-data` 与普通用户权限冲突。

本文示例统一使用：

- 代码目录：`/home/admin/program/MyWebsite`
- 前端静态目录：`/home/admin/program/mywebsite-frontend`
- 数据库目录：`/home/admin/program/MyWebsiteDatabase`
- 服务运行身份：`admin`

> `admin` 为示例用户名，请按你的实际用户名替换。

### 2.0 首部署前检查清单

- 已将域名 DNS 指向服务器公网 IP（若暂时无域名，可先用服务器 IP 验证 HTTP）
- 服务器已安装必要工具：`git`、`python3-venv`、`nodejs`、`npm`、`nginx`、`rsync`、`psmisc`
- 防火墙放行 Web 端口（如启用 UFW）：

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

### 2.1 拉取代码与依赖（普通用户，无 sudo clone/chown）

```bash
mkdir -p /home/admin/program
cd /home/admin/program
git clone <your-repo-url> MyWebsite
```

创建数据库隔离目录：

```bash
mkdir -p /home/admin/program/MyWebsiteDatabase
chmod 775 /home/admin/program/MyWebsiteDatabase
chgrp admin /home/admin/program/MyWebsiteDatabase
```

后端依赖：

```bash
cd /home/admin/program/MyWebsite/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

前端构建：

```bash
cd /home/admin/program/MyWebsite/frontend
npm ci
npm run build
mkdir -p /home/admin/program/mywebsite-frontend
rsync -av --delete dist/ /home/admin/program/mywebsite-frontend/
```

### 2.2 手动验证 Gunicorn

```bash
cd /home/admin/program/MyWebsite/backend
source .venv/bin/activate
APP_DEBUG=0 SQLALCHEMY_DATABASE_URI="sqlite:////home/admin/program/MyWebsiteDatabase/blog.db" \
.venv/bin/gunicorn -c /home/admin/program/MyWebsite/deploy/gunicorn.conf.py wsgi:app
```

新开终端测试：

```bash
curl http://127.0.0.1:5000/api/programs
```

### 2.3 配置 systemd（托管 Gunicorn）

复制模板并修改服务文件：

```bash
sudo cp /home/admin/program/MyWebsite/deploy/mywebsite-backend.service /etc/systemd/system/mywebsite-backend.service
sudo nano /etc/systemd/system/mywebsite-backend.service
```

请重点确认以下配置：

- `User=admin`
- `Group=admin`
- `WorkingDirectory=/home/admin/program/MyWebsite/backend`
- `ExecStart=/home/admin/program/MyWebsite/backend/.venv/bin/gunicorn -c /home/admin/program/MyWebsite/deploy/gunicorn.conf.py wsgi:app`
- **`Environment="SQLALCHEMY_DATABASE_URI=sqlite:////home/admin/program/MyWebsiteDatabase/blog.db"`**

> **注意： SQLite 绝对路径 URI 必须是 `sqlite:////`（4 个斜杠）**。少一个斜杠会导致 `unable to open database file` 或路径解析错误。

启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable mywebsite-backend
sudo systemctl restart mywebsite-backend
sudo systemctl status mywebsite-backend --no-pager
```

常用运维命令：

```bash
sudo systemctl restart mywebsite-backend
sudo journalctl -u mywebsite-backend -f
```

### 2.4 配置 Nginx

```bash
sudo cp /home/admin/program/MyWebsite/deploy/mywebsite.nginx.conf /etc/nginx/sites-available/mywebsite
sudo ln -sf /etc/nginx/sites-available/mywebsite /etc/nginx/sites-enabled/mywebsite
sudo rm -f /etc/nginx/sites-enabled/default
```

为保证 Nginx（`www-data`）可穿透用户目录访问前端静态文件，请执行：

```bash
sudo chmod +x /home/admin /home/admin/program
```

> 说明： 目录的执行权限（`x`）用于“可进入目录”，没有该权限时，即使文件本身可读，Nginx 也无法访问。

按需修改站点配置并生效：

```bash
sudo nano /etc/nginx/sites-available/mywebsite
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl reload nginx
```

### 2.5 HTTPS（推荐）

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 3. 项目更新与服务重启指南（Ubuntu 24.04）

### 3.1 更新后端

```bash
cd /home/admin/program/MyWebsite
git pull
cd /home/admin/program/MyWebsite/backend
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2 更新前端

```bash
cd /home/admin/program/MyWebsite/frontend
npm ci
npm run build
rsync -av --delete /home/admin/program/MyWebsite/frontend/dist/ /home/admin/program/mywebsite-frontend/
```

### 3.3 重启并验证

```bash
sudo systemctl daemon-reload
sudo systemctl restart mywebsite-backend
sudo systemctl status mywebsite-backend --no-pager
curl http://127.0.0.1:5000/api/programs
curl -I http://your-domain.com
```

### 3.4 日志排查

```bash
sudo journalctl -u mywebsite-backend -n 100 --no-pager
sudo journalctl -u mywebsite-backend -f
```

---

## 4. 项目里已做的部署/调试适配优化

1. 后端环境化启动参数：`APP_HOST`、`APP_PORT`、`APP_DEBUG`、`SQLALCHEMY_DATABASE_URI`
2. 反向代理适配：启用 `ProxyFix`
3. Gunicorn 入口与配置：`backend/wsgi.py`、`deploy/gunicorn.conf.py`
4. systemd 与 Nginx 模板：`deploy/mywebsite-backend.service`、`deploy/mywebsite.nginx.conf`
5. 前端联调代理：`/api` 通过 Vite/Nginx 转发
6. 博客时间统一 UTC 存储 + 前端本地时区展示

---

## 5. 常见故障排查

### 5.1 报错 `[Errno 98] Address already in use`

端口 5000 被遗留 gunicorn 进程占用：

```bash
sudo fuser -k 5000/tcp
```

然后重启服务：

```bash
sudo systemctl restart mywebsite-backend
```

### 5.2 报错 `unable to open database file`

常见原因：`SQLALCHEMY_DATABASE_URI` 写错，尤其是斜杠数量错误。

正确写法（绝对路径，4 个斜杠）：

```bash
sqlite:////home/admin/program/MyWebsiteDatabase/blog.db
```

请同时检查：

- `MyWebsiteDatabase` 目录是否存在
- 运行用户（`admin`）是否可写该目录

### 5.3 前端更新不生效

- 忘记执行 `npm run build`
- 忘记同步 `dist` 到 `/home/admin/program/mywebsite-frontend`

### 5.4 API 404/502

- 检查 `mywebsite-backend` 服务状态
- 检查 Nginx 的 `/api/` 反向代理是否正确并已 `reload`

---

## 6. 开发校验命令

```bash
# 后端语法校验（项目根目录）
cd /path/to/MyWebsite
python -m compileall backend

# 前端构建校验
cd /path/to/MyWebsite/frontend
npm run build
```
