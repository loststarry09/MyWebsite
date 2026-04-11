# MyWebsite 维护与操作指南

## 1. 项目概览

- 前端：Vue 3 + Vite + Tailwind CSS（目录：`/home/runner/work/MyWebsite/MyWebsite/frontend`）
- 后端：Flask（目录：`/home/runner/work/MyWebsite/MyWebsite/backend`）
- API 前缀：`/api`
- 后端入口：`/home/runner/work/MyWebsite/MyWebsite/backend/app.py`

## 2. 目录与关键文件

- 前端依赖与脚本：`/home/runner/work/MyWebsite/MyWebsite/frontend/package.json`
- 后端依赖：`/home/runner/work/MyWebsite/MyWebsite/backend/requirements.txt`
- 路由定义：`/home/runner/work/MyWebsite/MyWebsite/backend/routes/program.py`
- 后端数据文件：`/home/runner/work/MyWebsite/MyWebsite/backend/data.json`

## 3. 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

## 4. 本地运行（Linux/macOS）

### 4.1 启动后端

```bash
cd /home/runner/work/MyWebsite/MyWebsite/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

默认监听：`0.0.0.0:5000`

### 4.2 启动前端

```bash
cd /home/runner/work/MyWebsite/MyWebsite/frontend
npm ci
npm run dev
```

默认地址通常为：`http://127.0.0.1:5173`

## 5. 本地运行（Windows PowerShell）

### 5.1 启动后端

```powershell
cd D:\MyWebsite\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### 5.2 启动前端

```powershell
cd D:\MyWebsite\frontend
npm ci
npm run dev
```

## 6. 构建与基础校验

### 6.1 前端构建

```bash
cd /home/runner/work/MyWebsite/MyWebsite/frontend
npm run build
```

### 6.2 后端语法校验

```bash
cd /home/runner/work/MyWebsite/MyWebsite
python -m compileall backend
```

## 7. 生产部署（Nginx + Gunicorn）

### 7.1 启动 Gunicorn

```bash
cd /home/runner/work/MyWebsite/MyWebsite/backend
source .venv/bin/activate
gunicorn -w 2 -b 127.0.0.1:5000 "app:create_app()"
```

### 7.2 Nginx 反向代理关键点

- 将 `/api/` 代理到 `http://127.0.0.1:5000`
- 保留 `Host`、`X-Real-IP`、`X-Forwarded-For`、`X-Forwarded-Proto`
- 推荐使用 systemd 托管 Gunicorn 并设置自动重启

## 8. 1Panel（可选）

1. 前端执行 `npm ci && npm run build`，上传 `frontend/dist` 到站点目录  
2. 后端安装依赖并以 Gunicorn 启动  
3. 在站点中将 `/api/` 反向代理到 `127.0.0.1:5000`  
4. 配置 HTTPS 证书并仅对内开放 5000 端口

## 9. 日常维护建议

- 依赖管理  
  - 前端变更依赖后执行 `npm ci` + `npm run build` 验证  
  - 后端变更后执行 `python -m compileall backend`
- 数据维护  
  - 定期备份 `backend/data.json`
- 发布前检查  
  - 本地联调前后端  
  - 核对 API 路径是否统一为 `/api/*`  
  - 检查 Nginx 代理与 Gunicorn 运行状态

## 10. 常见故障排查

- 前端请求失败（404/502）  
  - 检查后端是否运行在 5000  
  - 检查 Nginx 是否正确代理 `/api/`
- 前端构建失败  
  - 先执行 `npm ci` 再执行 `npm run build`
- 后端启动失败  
  - 检查虚拟环境是否激活  
  - 检查是否已执行 `pip install -r requirements.txt`
- 接口路径错误  
  - 确认前端请求是否带 `/api` 前缀

