# MyWebsite

## 项目介绍

MyWebsite 是一个前后端分离的个人项目示例：

- 前端：Vue 3 + Vite + Tailwind CSS
- 后端：Flask
- 接口前缀：`/api`

当前后端提供了项目数据查询相关接口，前端负责展示与交互。

## 前端启动方式

在目录 `/home/runner/work/MyWebsite/MyWebsite/frontend` 下执行：

```bash
npm ci
npm run dev
```

默认会启动 Vite 开发服务器（通常是 `http://127.0.0.1:5173`）。

## 后端启动方式

在目录 `/home/runner/work/MyWebsite/MyWebsite/backend` 下执行：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

后端默认监听 `0.0.0.0:5000`。

## 部署说明（Nginx + Gunicorn）

以下为 Linux 服务器典型部署方式：

1. 准备后端运行环境并安装依赖（含 `gunicorn`）
2. 使用 Gunicorn 启动 Flask 应用
3. 使用 Nginx 反向代理对外提供服务
4. （推荐）配合 systemd 管理 Gunicorn 进程

### 1）启动 Gunicorn

在目录 `/home/runner/work/MyWebsite/MyWebsite/backend` 下：

```bash
source .venv/bin/activate
gunicorn -w 2 -b 127.0.0.1:5000 "app:create_app()"
```

### 2）Nginx 反向代理示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3）（推荐）使用 systemd 托管 Gunicorn

- 将 Gunicorn 配置为 systemd service
- 设置开机自启并自动重启
- 使用 `journalctl` 查看运行日志

### 4）1Panel 服务器图形化操作界面部署（可选）

如果你使用 1Panel，可按下面方式图形化完成部署：

1. **创建网站（前端静态站点）**
   - 在 1Panel 的网站管理中创建站点（域名或端口）
   - 本地执行前端打包：`npm ci && npm run build`
   - 将 `/home/runner/work/MyWebsite/MyWebsite/frontend/dist` 上传到站点目录

2. **部署后端（Gunicorn）**
   - 在服务器 `/home/runner/work/MyWebsite/MyWebsite/backend` 创建虚拟环境并安装依赖（含 `gunicorn`）
   - 通过 1Panel 的进程管理/计划任务（或 systemd）启动命令：
     `gunicorn -w 2 -b 127.0.0.1:5000 "app:create_app()"`

3. **配置反向代理**
   - 在 1Panel 网站的反向代理配置中新增 `/api/` 转发到 `http://127.0.0.1:5000`
   - 保留 Host、X-Forwarded-For、X-Forwarded-Proto 等常用请求头

4. **HTTPS 与安全**
   - 在 1Panel 证书管理中签发或上传 SSL 证书并开启 HTTPS
   - 开放 80/443 端口，后端 5000 端口仅对本机开放
