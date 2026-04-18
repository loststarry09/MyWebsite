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

> 本地开发可使用相对路径 `sqlite:///blog.db`；生产环境使用绝对路径时必须写成 `sqlite:////...`（4 个斜杠）。

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
sudo apt install -y git python3 python3-venv python3-pip nodejs npm nginx rsync psmisc
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

### 1.6 启动前端（Ubuntu）

```bash
cd /path/to/MyWebsite/frontend
npm ci
npm run dev
```

---

## 2. Ubuntu 24.04 生产部署（Gunicorn + Nginx + systemd）

### 前置说明（务必先读）

本项目采用 **用户目录部署方案（User-level Deployment）**，并使用“代码、数据、日志、静态产物”隔离结构，显著降低权限冲突风险。

本文示例以 `admin` 用户为例，统一工作区如下：

- 工作区根目录：`/home/admin/program/MyWebsite`
- 源代码目录：`/home/admin/program/MyWebsite/code`
- 数据库目录：`/home/admin/program/MyWebsite/database`
- 日志目录：`/home/admin/program/MyWebsite/logs`
- 前端静态目录：`/home/admin/program/MyWebsite/frontend-dist`

> `admin` 为示例用户名，请替换为你的真实系统用户名。

### 2.1 拉取代码与依赖

创建工作区并克隆代码（普通用户执行）：

```bash
mkdir -p /home/admin/program/MyWebsite
cd /home/admin/program/MyWebsite
git clone <your-repo-url> code
```

创建运行时目录：

```bash
cd /home/admin/program/MyWebsite
mkdir -p database logs frontend-dist
```

**重要：GitHub 仓库只包含源码，不包含 `database`、`logs`、`frontend-dist` 这些运行时目录，必须手动创建。Flask 在首次启动时会在 `database` 目录自动生成 `blog.db`。**

**强烈警告：请使用普通用户直接执行 `mkdir` 创建 `database` 目录，绝不要加 `sudo`，否则极易导致目录/数据库归属变为 `root`，引发后端写入失败。**

安装后端依赖：

```bash
cd /home/admin/program/MyWebsite/code/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

构建并发布前端静态文件：

```bash
cd /home/admin/program/MyWebsite/code/frontend
npm ci
npm run build
rsync -av --delete dist/ /home/admin/program/MyWebsite/frontend-dist/
```

### 2.2 手动验证 Gunicorn

```bash
cd /home/admin/program/MyWebsite/code/backend
source .venv/bin/activate
APP_DEBUG=0 SQLALCHEMY_DATABASE_URI="sqlite:////home/admin/program/MyWebsite/database/blog.db" \
.venv/bin/gunicorn -c /home/admin/program/MyWebsite/code/deploy/gunicorn.conf.py wsgi:app
```

另开终端验证：

```bash
curl http://127.0.0.1:5000/api/programs
```

### 2.3 配置 systemd

复制服务模板：

```bash
sudo cp /home/admin/program/MyWebsite/code/deploy/mywebsite-backend.service /etc/systemd/system/mywebsite-backend.service
sudo nano /etc/systemd/system/mywebsite-backend.service
```

请确认关键项：

- `User=admin`
- `Group=admin`
- `WorkingDirectory=/home/admin/program/MyWebsite/code/backend`
- `ExecStart=/home/admin/program/MyWebsite/code/backend/.venv/bin/gunicorn -c /home/admin/program/MyWebsite/code/deploy/gunicorn.conf.py wsgi:app`
- **`Environment="SQLALCHEMY_DATABASE_URI=sqlite:////home/admin/program/MyWebsite/database/blog.db"`**

> **注意：SQLite 绝对路径必须使用 `sqlite:////`（4 个斜杠）。**

启动并设为开机自启：

```bash
sudo systemctl daemon-reload
sudo systemctl enable mywebsite-backend
sudo systemctl restart mywebsite-backend
sudo systemctl status mywebsite-backend --no-pager
```

查看日志：

```bash
sudo journalctl -u mywebsite-backend -f
```

### 2.4 配置 Nginx

```bash
sudo cp /home/admin/program/MyWebsite/code/deploy/mywebsite.nginx.conf /etc/nginx/sites-available/mywebsite
sudo ln -sf /etc/nginx/sites-available/mywebsite /etc/nginx/sites-enabled/mywebsite
sudo rm -f /etc/nginx/sites-enabled/default
```

为确保 Nginx（`www-data`）可穿透用户目录读取静态文件，请执行：

```bash
chmod +x /home/admin /home/admin/program /home/admin/program/MyWebsite
```

> 上述目录缺少执行权限（x）时，Nginx 即使有文件读权限也无法进入目录链路。

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

## 3. 项目更新与发布流程

### 3.1 更新后端

```bash
cd /home/admin/program/MyWebsite/code
git pull
cd /home/admin/program/MyWebsite/code/backend
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart mywebsite-backend
```

### 3.2 更新前端

```bash
cd /home/admin/program/MyWebsite/code/frontend
npm ci
npm run build
rsync -av --delete dist/ /home/admin/program/MyWebsite/frontend-dist/
sudo systemctl reload nginx
```

---

## 4. 常用验证命令

```bash
# 后端语法检查
cd /home/admin/program/MyWebsite/code
python -m compileall backend

# 前端构建检查
cd /home/admin/program/MyWebsite/code/frontend
npm run build
```

---

## 5. 常见故障排查

### 5.1 报错 `[Errno 98] Address already in use`

端口被遗留进程占用：

```bash
sudo fuser -k 5000/tcp
sudo systemctl restart mywebsite-backend
```

### 5.2 报错 `unable to open database file`

通常原因：

1. `SQLALCHEMY_DATABASE_URI` 写错（少写斜杠，必须是 4 个斜杠）
2. 忘记手动创建 `database` 目录

正确格式：

```bash
sqlite:////home/admin/program/MyWebsite/database/blog.db
```

快速核对：

```bash
ls -ld /home/admin/program/MyWebsite/database
sudo systemctl cat mywebsite-backend | grep SQLALCHEMY_DATABASE_URI
```

### 5.3 报错 `attempt to write a readonly database`

报错现象：

- 发布/保存博客时失败
- 后端日志出现：`sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) attempt to write a readonly database`

原因剖析：

- 常见于曾使用 `sudo` 手动创建 `database` 目录，或用 `sudo` 运行过 SQLite 调试脚本
- 导致 `/home/admin/program/MyWebsite/database` 与 `blog.db` 所有者变成 `root`
- Gunicorn 以普通用户（如 `admin`）运行时只读不可写，从而触发该错误

修复命令（以 `admin` 用户为例）：

```bash
sudo chown -R admin:admin /home/admin/program/MyWebsite/database
sudo chmod -R 775 /home/admin/program/MyWebsite/database
sudo systemctl restart mywebsite-backend
```

### 5.4 前端更新后页面不变

- 忘记执行 `npm run build`
- 忘记 `rsync` 到 `/home/admin/program/MyWebsite/frontend-dist`
- Nginx 未 reload

### 5.5 API 404/502

- 后端服务异常：`sudo systemctl status mywebsite-backend --no-pager`
- 查看日志：`sudo journalctl -u mywebsite-backend -n 100 --no-pager`
- 检查 Nginx `/api/` 反向代理目标
