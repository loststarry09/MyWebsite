# MyWebsite

## 项目简介

MyWebsite 是一个前后端分离示例项目：

- 前端：Vue 3 + Vite + Tailwind CSS（`/home/runner/work/MyWebsite/MyWebsite/frontend`）
- 后端：Flask（`/home/runner/work/MyWebsite/MyWebsite/backend`）
- API 前缀：`/api`（由 `backend/app.py` 注册蓝图）

---

## 目录结构

```text
MyWebsite/
├─ frontend/                # Vue 前端
│  ├─ src/
│  └─ package.json
├─ backend/                 # Flask 后端
│  ├─ app.py
│  ├─ routes/program.py
│  ├─ services/runner.py
│  └─ data.json
└─ README.md
```

---

## 一、Ubuntu 24.04 调试（开发模式）

### 1) 环境准备

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm
```

> Node.js 建议 18+，Python 建议 3.10+。

### 2) 启动后端（Flask）

```bash
cd /home/runner/work/MyWebsite/MyWebsite/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

- 默认监听：`0.0.0.0:5000`
- 验证接口：`http://127.0.0.1:5000/api/programs`

### 3) 启动前端（Vue + Vite）

新开一个终端执行：

```bash
cd /home/runner/work/MyWebsite/MyWebsite/frontend
npm ci
npm run dev
```

- 默认访问：`http://127.0.0.1:5173`
- `npm run dev` 支持热更新

### 4) 调试常用命令

```bash
# 前端构建校验
cd /home/runner/work/MyWebsite/MyWebsite/frontend
npm run build

# 后端语法校验
cd /home/runner/work/MyWebsite/MyWebsite
python -m compileall backend
```

---

## 二、Windows 11 调试（开发模式）

推荐使用 **PowerShell**，以下路径以 `D:\MyWebsite` 为例，请按实际路径替换。

### 1) 启动后端（Flask）

```powershell
cd D:\MyWebsite\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

- 验证接口：`http://127.0.0.1:5000/api/programs`

> 若激活虚拟环境报权限错误：
> `Set-ExecutionPolicy -Scope Process RemoteSigned`

### 2) 启动前端（Vue + Vite）

新开一个 PowerShell 窗口（需要管理员权限）：

```powershell
cd D:\MyWebsite\frontend
npm ci
npm run dev
```

- 默认访问：`http://127.0.0.1:5173`
- 修改代码后自动刷新

### 3) 调试常用命令

```powershell
# 前端构建
cd D:\MyWebsite\frontend
npm run build

# 后端语法校验（在项目根目录）
cd D:\MyWebsite
python -m compileall backend
```

---

## 三、Ubuntu 24.04 部署（推荐：Nginx + Gunicorn + systemd）

### 1) 后端部署

```bash
cd /home/runner/work/MyWebsite/MyWebsite/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

手动验证 Gunicorn：

```bash
gunicorn -w 2 -b 127.0.0.1:5000 "app:create_app()"
```

### 2) 前端构建与发布

```bash
cd /home/runner/work/MyWebsite/MyWebsite/frontend
npm ci
npm run build
```

将 `frontend/dist` 发布到 Nginx 静态目录（如 `/var/www/mywebsite`）。

### 3) Nginx 反向代理示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/mywebsite;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4) systemd 托管 Gunicorn（建议）

- 将 Gunicorn 配置为 systemd service
- 启用开机自启与自动重启
- 通过 `journalctl -u <service-name> -f` 查看日志

---

## 四、Windows 11 部署（可行方案：Nginx + Waitress）

> Windows 11 更适合开发环境；若用于部署，建议至少使用反向代理并将后端服务化。

### 1) 后端部署（Waitress）

在 `D:\MyWebsite\backend`：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install waitress
waitress-serve --host=127.0.0.1 --port=5000 app:create_app
```

### 2) 前端构建

```powershell
cd D:\MyWebsite\frontend
npm ci
npm run build
```

将 `frontend\dist` 放到 Nginx 静态目录（如 `D:\nginx\html\mywebsite`）。

### 3) Windows Nginx 反向代理示例

```nginx
server {
    listen 80;
    server_name localhost;

    root D:/nginx/html/mywebsite;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4) 服务化建议

- 将 `waitress-serve` 配置为 Windows 服务（如 NSSM）
- 设置失败自动重启
- 建议仅开放 80/443，对外不直接暴露 5000

---

## 五、联调与故障排查

- 前端请求失败（404/502）
  - 检查后端是否运行在 5000
  - 检查 Nginx 是否正确代理 `/api/`
- 页面修改未生效
  - 开发环境确认 `npm run dev` 仍在运行
  - 部署环境确认已重新构建并更新静态文件
- 后端改动未生效
  - 开发模式通常需手动重启 Flask
  - 部署模式需重启/重载后端服务
- 跨域问题
  - 同域反向代理（`/api`）优先
  - 若前后端分离域名，后端需配置 CORS
