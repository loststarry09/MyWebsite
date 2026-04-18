#!/usr/bin/env bash

DB_DIR="${DB_DIR:-/home/admin/program/MyWebsiteDatabase}"
DB_GROUP="${DB_GROUP:-admin}"
SERVICE_NAME="mywebsite-backend"
PORT="5000"
HAS_ERROR=0

echo "[INFO] 开始执行一键安全化部署脚本..."

echo "[STEP 1] 清理占用 ${PORT} 端口的遗留 Gunicorn 进程..."
if command -v fuser >/dev/null 2>&1; then
    if fuser "${PORT}/tcp" >/dev/null 2>&1; then
        if fuser -k "${PORT}/tcp" >/dev/null 2>&1; then
            echo "[OK] 已清理占用 ${PORT} 端口的进程。"
        else
            echo "[WARN] 清理 ${PORT} 端口进程失败，请手动检查。"
            HAS_ERROR=1
        fi
    else
        echo "[INFO] 未发现占用 ${PORT} 端口的进程。"
    fi
else
    echo "[WARN] 系统未安装 fuser，跳过端口清理。"
    HAS_ERROR=1
fi

echo "[STEP 2] 修复 ${DB_DIR} 目录权限与所属组..."
if [ -d "${DB_DIR}" ]; then
    if chmod 775 "${DB_DIR}"; then
        echo "[OK] 已设置目录权限为 775。"
    else
        echo "[WARN] chmod 775 ${DB_DIR} 失败。"
        HAS_ERROR=1
    fi

    if chgrp "${DB_GROUP}" "${DB_DIR}"; then
        echo "[OK] 已将目录所属组设置为 ${DB_GROUP}。"
    else
        echo "[WARN] chgrp ${DB_GROUP} ${DB_DIR} 失败。"
        HAS_ERROR=1
    fi
else
    echo "[WARN] 目录不存在：${DB_DIR}"
    HAS_ERROR=1
fi

echo "[STEP 3] 重新加载 systemd 并重启 ${SERVICE_NAME}..."
if systemctl daemon-reload; then
    echo "[OK] systemd daemon-reload 完成。"
else
    echo "[WARN] systemctl daemon-reload 失败。"
    HAS_ERROR=1
fi

if systemctl restart "${SERVICE_NAME}"; then
    echo "[OK] ${SERVICE_NAME} 重启成功。"
else
    echo "[WARN] ${SERVICE_NAME} 重启失败，请查看日志。"
    HAS_ERROR=1
fi

if [ "${HAS_ERROR}" -eq 0 ]; then
    echo "[DONE] 部署脚本执行完成，所有关键步骤成功。"
else
    echo "[DONE] 部署脚本执行完成，但存在告警，请根据上文提示处理。"
fi

exit "${HAS_ERROR}"
