# Guidance.md

> MyWebsite 内部架构手册与避坑指南（V1.4）  
> 后端已从 Flask 全量迁移到 FastAPI，并延续 V1.2 本地图床方案。

---

## 1. 文档目标与适用范围

本手册用于团队内部维护与部署，核心目标：

- 统一 MyWebsite 的部署理念与目录规范
- 固化 FastAPI 时代的运行方式（Gunicorn + Uvicorn Worker）
- 记录历史踩坑与防呆机制，降低维护风险
- 保证“极简无痛流”可复制、可扩展、可长期演进

---

## 2. “极简无痛流”核心理念

### 2.1 一条红线：彻底不用 `/var/www/`

历史经验表明，把业务代码和 Nginx 默认目录绑定，会导致：

- 权限管理混乱（root / nginx / deploy 用户交叉）
- 数据与代码混放，迁移与备份复杂
- 故障定位困难（日志、数据库、静态资源分散）

**结论：MyWebsite 永久采用用户家目录隔离部署（User-level Deployment）。**

---

## 3. 最新 5 大平级目录结构（必须遵守）

统一工作区（示例）：

```text
/home/admin/program/MyWebsite/
├── code/           # Git 源代码（前后端工程）
├── database/       # SQLite 物理隔离目录
├── logs/           # 运行日志（gunicorn / app）
├── frontend-dist/  # 前端构建产物（Nginx 直接服务）
└── uploads/        # 本地图床持久化目录（Nginx 直接穿透）
```

### 目录职责说明

1. `code/`  
   - 仅存放源码，不放数据库、不放运行日志、不放用户上传文件  
   - 允许随时 `git pull`、回滚、替换

2. `database/`  
   - 仅存放 SQLite 文件，如 `my_website.db`
   - 与代码物理隔离，避免覆盖风险

3. `logs/`  
   - 统一记录应用运行日志、错误日志
   - 便于 systemd / 运维排障

4. `frontend-dist/`  
   - 仅存放 `npm run build` 产物
   - 由 Nginx 直接返回静态内容，避免 FastAPI 参与静态文件分发

5. `uploads/`  
   - 本地图床持久化目录（V1.2 引入）
   - 由 Nginx 直接读取，绕过 FastAPI，提高访问效率并降低后端负载

---

## 4. 运行架构（V1.4）

- 前端：Vue 3 + Vite + Tailwind CSS
- 后端：FastAPI + Pydantic + SQLAlchemy + SQLite
- 进程：Gunicorn + Uvicorn Worker
- 守护：systemd
- 网关：Nginx
- 系统：Ubuntu 24.04

请求流：

1. 浏览器请求静态页面 → Nginx 直接读 `frontend-dist/`
2. 浏览器请求图片资源（uploads）→ Nginx 直接读 `uploads/`
3. 浏览器请求 API → Nginx 反向代理到 `127.0.0.1:5000`（FastAPI/Gunicorn）

---

## 5. Nginx 穿透配置逻辑（重点）

目标：让静态资源与上传资源直接由 Nginx 返回，绕过 FastAPI。

## 5.1 关键原则

- `frontend-dist/`：前端静态站点根目录
- `/uploads/`：映射到持久化上传目录
- `/api/`（或约定 API 前缀）：代理到 FastAPI
- 所有静态访问不经过 Python 进程，提升吞吐与稳定性

## 5.2 参考配置（按实际域名修改）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 1) 前端静态资源（SPA）
    root /home/admin/program/MyWebsite/frontend-dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 2) 本地图床穿透（直接读 uploads）
    location /uploads/ {
        alias /home/admin/program/MyWebsite/uploads/;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # 3) API 反向代理到 FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

> 说明：  
> - 若后端未使用 `/api` 前缀，可按实际路由调整 location。  
> - `alias` 结尾斜杠必须与 location 规范匹配，避免路径拼接错误。  

---

## 6. systemd + Gunicorn + Uvicorn Worker（重点）

FastAPI 生产启动命令必须使用：

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:5000
```

## 6.1 参考 systemd 服务文件

路径：`/etc/systemd/system/mywebsite.service`

```ini
[Unit]
Description=MyWebsite FastAPI Service
After=network.target

[Service]
User=admin
Group=admin
WorkingDirectory=/home/admin/program/MyWebsite/code/backend
Environment="PATH=/home/admin/program/MyWebsite/code/backend/.venv/bin"
ExecStart=/home/admin/program/MyWebsite/code/backend/.venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:5000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## 6.2 常用管理命令

```bash
sudo systemctl daemon-reload
sudo systemctl enable mywebsite
sudo systemctl restart mywebsite
sudo systemctl status mywebsite
journalctl -u mywebsite -f
```

---

## 7. 历史踩坑与防呆机制（避坑宝典）

## 7.1 SSH / Git 权限坑

### 症状
- `Permission denied (publickey)`
- `git pull` 失败，或仓库目录 owner 混乱

### 根因
- 使用 root 生成 SSH 密钥或拉代码
- 项目目录归属 root，admin 无法正常维护

### 防呆规则（强制）
- **严禁 root 拉代码**
- **严禁 root 生成用于项目的 SSH 密钥**
- 所有 Git/部署操作必须在 `admin` 用户下执行

### 修复建议
```bash
sudo chown -R admin:admin /home/admin/program/MyWebsite
su - admin
ssh -T git@github.com
```

---

## 7.2 Gunicorn/FastAPI 启动坑

### 症状
- 服务“看似启动”但路由 404 或无响应
- 用了 Flask 旧命令导致 ASGI 不兼容

### 根因
- 未使用 Uvicorn Worker 承载 FastAPI（ASGI）
- `ExecStart` 指向错误环境或错误目录

### 防呆规则
- 启动命令固定为：  
  `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:5000`
- 明确 `WorkingDirectory` 与虚拟环境路径
- `systemctl daemon-reload` 后再 restart

---

## 7.3 SQLite 连接字符串坑（四斜杠绝杀）

### 症状
- 找不到数据库文件
- 连接到了错误位置（相对路径导致）

### 根因
- SQLite 绝对路径写法错误

### 防呆规则（必须）
绝对路径必须是 **4 个斜杠**：

```python
sqlite:////home/admin/program/MyWebsite/database/my_website.db
```

不是 3 个，不是相对路径。

---

## 7.4 FastAPI Session 管理坑（防死锁/连接泄漏）

### 症状
- 并发下偶发数据库锁问题
- 请求后连接未正确释放

### 根因
- 未使用依赖注入统一管理 Session 生命周期

### 防呆规则（必须）
在 FastAPI 中统一使用 `Depends(get_db)` 获取会话，确保每次请求结束后关闭 Session。

---

## 7.5 SQLite “attempt to write a readonly database” 坑

### 症状
- 写入时报错：`attempt to write a readonly database`

### 常见根因
1. 数据库文件属主错误（被 root 创建）
2. `database/` 目录无写权限（SQLite 需要目录写权限）
3. 数据库文件放在只读挂载或权限受限路径

### 快速修复
```bash
sudo chown -R admin:admin /home/admin/program/MyWebsite/database
chmod 755 /home/admin/program/MyWebsite/database
chmod 664 /home/admin/program/MyWebsite/database/my_website.db
```

> 注意：目录权限与文件权限都要检查，SQLite 需要目录可写来创建锁/临时文件。

---

## 7.6 Nginx alias 路径坑（uploads 404）

### 症状
- `/uploads/...` 404 或路径错位

### 根因
- `location /uploads/` 与 `alias .../uploads/` 末尾斜杠不匹配

### 防呆规则
- `location /uploads/` + `alias /abs/path/uploads/;`（两者都保留末尾 `/`）

---

## 8. 维护建议（长期）

- 任何改动先在 `code/` 验证，再发布到 `frontend-dist/`
- 数据库每日定时备份（至少保留最近 7 天）
- 变更 Nginx/systemd 后先 `nginx -t` 与 `systemctl status`
- 生产问题先查：
  1. `journalctl -u mywebsite -f`
  2. Nginx error log
  3. `logs/` 下应用日志

---

## 9. 一键核对清单（发布前）

- [ ] 当前操作用户是 `admin`（非 root）
- [ ] 目录结构为 5 大平级目录
- [ ] SQLite URL 使用 `sqlite:////...` 绝对路径
- [ ] FastAPI 路由使用 `Depends(get_db)` 管理 Session
- [ ] systemd 启动命令为 Gunicorn + Uvicorn Worker 组合
- [ ] Nginx 已直出 `frontend-dist/` 与 `uploads/`
- [ ] `nginx -t`、`systemctl status`、接口健康检查全部通过
