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

## 本地调试说明（Windows 11）

推荐使用 **PowerShell**，以下命令假设项目路径为 `D:\MyWebsite`（请按你的实际路径替换）。

### 1）后端调试（Flask）

在目录 `D:\MyWebsite\backend` 下执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

启动后端后，可在浏览器访问 `http://127.0.0.1:5000/api/programs` 验证接口。

### 2）前端调试（Vue + Vite）

新开一个 PowerShell 窗口，在目录 `D:\MyWebsite\frontend` 下执行：

```powershell
npm ci
npm run dev
```

默认访问地址通常为 `http://127.0.0.1:5173`。

### 3）联调与常见排查

- 保证后端先启动，再启动前端
- 若 PowerShell 不允许激活虚拟环境，可先执行：`Set-ExecutionPolicy -Scope Process RemoteSigned`
- 若端口占用，请关闭占用进程或修改前后端启动端口
- 前端请求后端时，统一使用 `/api` 前缀

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

