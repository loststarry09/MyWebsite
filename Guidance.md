# Guidance.md

> MyWebsite 内部架构手册与防呆运维宝典（FastAPI 时代）

---

## 篇章一：极简无痛流架构理念

### 1.1 统一工作区与 5 大平级物理隔离目录

固定工作区：`/home/admin/program/MyWebsite/`

```text
/home/admin/program/MyWebsite/
├── code/           # 代码仓库（仅源码）
├── database/       # SQLite 数据库文件
├── logs/           # 应用与运维日志
├── frontend-dist/  # 前端构建产物（Nginx 直出）
└── uploads/        # 图床上传目录（Nginx 直出）
```

目录职责铁律：

- `code/` 只放代码，允许安全 `git pull`、回滚。
- `database/` 只放数据库，避免代码更新覆盖数据。
- `logs/` 集中排障，便于 systemd / journal 关联分析。
- `frontend-dist/` 放前端静态产物，由 Nginx 直接读取。
- `uploads/` 放图片上传文件，由 Nginx 直接读取。

### 1.2 Nginx 静态与图床穿透读取机制（绕过 FastAPI）

请求分流原则：

1. `location /`：Nginx 从 `frontend-dist/` 直接返回静态资源。
2. `location /uploads/`：Nginx 从 `uploads/` 直接返回图床文件。
3. `location /api/`：仅 API 请求代理到 FastAPI（127.0.0.1:5000）。

这样可显著降低 Python 进程压力，提升吞吐与稳定性。

### 1.3 Trailing Slash 结尾斜杠防坑指南

Nginx `alias` 使用规则必须严格匹配：

```nginx
location /uploads/ {
    alias /home/admin/program/MyWebsite/uploads/;
}
```

防坑要点：

- `location /uploads/` 与 `alias .../uploads/` 两端都要保留结尾 `/`。
- 少一个斜杠，容易导致路径拼接错误、资源 404 或错位。

---

## 篇章二：从零开始的生产环境部署指南（防呆版）

### 2.1 用户与环境初始化（禁止 root 直接部署）

仅 root 做系统初始化，业务部署必须使用 `admin`：

```bash
adduser admin
usermod -aG sudo admin
su - admin
whoami
```

安装基础环境（Ubuntu）：

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx git sqlite3 curl
```

### 2.2 初始化目录与代码

创建 5 大平级目录：

```bash
mkdir -p /home/admin/program/MyWebsite/{code,database,logs,frontend-dist,uploads}
sudo chown -R admin:admin /home/admin/program/MyWebsite
chmod 755 /home/admin/program/MyWebsite/{code,database,logs,frontend-dist,uploads}
```

配置 SSH 并拉取代码：

```bash
ssh-keygen -t ed25519 -C "admin@mywebsite-server"
cat ~/.ssh/id_ed25519.pub
ssh -T git@github.com

cd /home/admin/program/MyWebsite/code
git clone <你的仓库SSH地址> .
```

### 2.3 前端构建与同步

```bash
cd /home/admin/program/MyWebsite/code/frontend
npm install
npm run build
cp -r dist/* ../frontend-dist/
```

建议发布到绝对路径（更防呆）：

```bash
cp -r dist/* /home/admin/program/MyWebsite/frontend-dist/
```

### 2.4 后端守护与 Nginx

后端虚拟环境与依赖：

```bash
cd /home/admin/program/MyWebsite/code/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

systemd 配置模板：`/etc/systemd/system/mywebsite.service`

```ini
[Unit]
Description=MyWebsite FastAPI Service
After=network.target

[Service]
User=admin
Group=admin
WorkingDirectory=/home/admin/program/MyWebsite/code/backend
Environment="PATH=/home/admin/program/MyWebsite/code/backend/venv/bin"
ExecStart=/home/admin/program/MyWebsite/code/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:5000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

加载与启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable mywebsite
sudo systemctl restart mywebsite
sudo systemctl status mywebsite --no-pager
```

数据库权限防呆（必须执行）：

```bash
sudo chown -R admin:admin /home/admin/program/MyWebsite/database
ls -ld /home/admin/program/MyWebsite/database
```

Nginx 站点示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /home/admin/program/MyWebsite/frontend-dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /uploads/ {
        alias /home/admin/program/MyWebsite/uploads/;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

生效命令：

```bash
sudo ln -sf /etc/nginx/sites-available/mywebsite /etc/nginx/sites-enabled/mywebsite
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## 篇章三：日常运维与服务器代码热更新 SOP（防呆流水线）

### 前提：必须切换至 admin 用户

```bash
su - admin
cd /home/admin/program/MyWebsite/code
```

### 第 1 步：拉取最新代码

```bash
git pull
```

### 第 2 步：更新前端静态产物（若前端有变动）

```bash
cd frontend
npm install
npm run build
rm -rf /home/admin/program/MyWebsite/frontend-dist/*
cp -r dist/* /home/admin/program/MyWebsite/frontend-dist/
# 注：覆盖后直接刷新浏览器即可见效，无需重启 Nginx
```

### 第 3 步：更新后端服务引擎（若后端有变动）

```bash
cd ../backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart mywebsite
# 查错防呆命令：sudo journalctl -u mywebsite -n 50 --no-pager
```

### 热更新后快速验收清单

```bash
sudo systemctl status mywebsite --no-pager
curl -I http://127.0.0.1:5000/docs
sudo nginx -t
```

- 页面可正常访问，且静态资源来自 `frontend-dist/`。
- 图床图片路径 `/uploads/...` 可直接访问。
- API 请求可正常透传至 FastAPI。

---

## 附：高频故障防呆速查

1. **readonly database**：优先检查 `database/` 是否为 `admin:admin`。
2. **uploads 404**：检查 `location /uploads/` 与 `alias .../uploads/` 斜杠是否双匹配。
3. **服务启动失败**：用 `sudo journalctl -u mywebsite -n 50 --no-pager` 定位。
4. **前端更新不生效**：确认 `frontend-dist/` 已被新 `dist` 覆盖。
