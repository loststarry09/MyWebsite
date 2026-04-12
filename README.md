# MyWebsite

前后端分离项目：

- 前端：Vue 3 + Vite + Tailwind（`frontend/`）
- 后端：Flask（`backend/`）
- API 前缀：`/api`

---

## 1. 本地开发（兼顾联调）

### 1.1 环境准备（Ubuntu 24.04）

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx
```

> 建议 Python 3.10+，Node 18+。

### 1.2 启动后端

```bash
cd /home/runner/work/MyWebsite/MyWebsite/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
APP_DEBUG=1 APP_HOST=0.0.0.0 APP_PORT=5000 python app.py
```

后端校验：

```bash
curl http://127.0.0.1:5000/api/programs
```

### 1.3 启动前端

```bash
cd /home/runner/work/MyWebsite/MyWebsite/frontend
npm ci
npm run dev
```

前端开发时已内置代理：

- `http://127.0.0.1:5173/api/*` → `http://127.0.0.1:5000/api/*`
- 可通过环境变量覆盖代理目标：`VITE_API_PROXY_TARGET=http://127.0.0.1:5000 npm run dev`

---

## 2. Ubuntu 24.04 生产部署（Gunicorn + Nginx + systemd）

下面以：

- 项目目录：`/var/www/MyWebsite`
- 前端静态目录：`/var/www/mywebsite-frontend`
- 域名：`your-domain.com`

为例，请按实际替换。

### 2.1 拉取代码并安装依赖

```bash
sudo mkdir -p /var/www
cd /var/www
sudo git clone <your-repo-url> MyWebsite
sudo chown -R $USER:$USER /var/www/MyWebsite
```

后端依赖：

```bash
cd /var/www/MyWebsite/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

前端构建：

```bash
cd /var/www/MyWebsite/frontend
npm ci
npm run build
sudo mkdir -p /var/www/mywebsite-frontend
sudo rsync -av --delete dist/ /var/www/mywebsite-frontend/
```

### 2.2 手动验证 Gunicorn

```bash
cd /var/www/MyWebsite/backend
source .venv/bin/activate
APP_DEBUG=0 .venv/bin/gunicorn -c /var/www/MyWebsite/deploy/gunicorn.conf.py wsgi:app
```

新开终端测试：

```bash
curl http://127.0.0.1:5000/api/programs
```

### 2.3 配置 systemd（托管 Gunicorn）

复制模板并启用：

```bash
sudo cp /var/www/MyWebsite/deploy/mywebsite-backend.service /etc/systemd/system/
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
sudo cp /var/www/MyWebsite/deploy/mywebsite.nginx.conf /etc/nginx/sites-available/mywebsite
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

## 3. 项目里已做的部署/调试适配优化

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

---

## 4. 常见故障排查

### 4.1 前端请求 404/502

- 确认后端是否在本机 `127.0.0.1:5000` 运行
- 确认 Nginx `location /api/` 生效并已 reload
- 通过 `curl http://127.0.0.1:5000/api/programs` 先验证后端自身

### 4.2 页面空白或路由刷新 404

- 确认 Nginx 对 `/` 使用：`try_files $uri $uri/ /index.html;`

### 4.3 后端更新不生效

- 执行 `sudo systemctl restart mywebsite-backend`
- 查看日志 `sudo journalctl -u mywebsite-backend -f`

### 4.4 前端更新不生效

- 重新构建并覆盖静态目录：
  - `npm run build`
  - `rsync -av --delete dist/ /var/www/mywebsite-frontend/`

---

## 5. 开发校验命令

```bash
# 后端语法校验（项目根目录）
cd /home/runner/work/MyWebsite/MyWebsite
python -m compileall backend

# 前端构建校验
cd /home/runner/work/MyWebsite/MyWebsite/frontend
npm run build
```
