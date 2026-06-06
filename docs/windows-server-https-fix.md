# Windows Server HTTPS 部署修复指南

## 问题背景

生产环境 `https://geleme.online` 部署后出现以下问题：

1. **消息始终显示"未读"** — 已读状态不会更新，未读徽标不会清除
2. **浏览器 Mixed Content 警告** — 图片 URL 使用 `http://` 而非 `https://`
3. **WebSocket 连接被拦截** — `ws://` 在 HTTPS 页面下被浏览器安全策略阻止

## 根因

| 问题 | 根因 | 影响 |
|------|------|------|
| 未读状态不更新 | `ChatView.vue` 硬编码 `ws://`，HTTPS 下 `new WebSocket()` 抛出 `SecurityError`，导致所有后续代码（REST 降级、轮询、已读标记）全部不执行 | 致命 |
| 图片 Mixed Content | nginx 未传递 `X-Forwarded-Proto`，Django 未配置 `SECURE_PROXY_SSL_HEADER`，导致 `build_absolute_uri()` 生成 `http://` URL | 警告 |
| WebSocket 不支持 | `deploy.bat` 仅启动 Waitress（WSGI），无 ASGI 服务器处理 WebSocket | 功能缺失 |

## 代码已修复（仓库推送）

| 文件 | 修改内容 |
|------|---------|
| `frontend/src/views/ChatView.vue` | `ws://` → 根据页面协议自动选择 `wss://` / `ws://`；`new WebSocket()` 加 try-catch 防止异常阻塞 REST 降级 |
| `backend/config/settings.py` | 生产模式添加 `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` |
| `docker/nginx.conf` | 所有 `proxy_pass` 添加 `X-Forwarded-Proto` 头；`/ws/` 块补充 `X-Forwarded-For` |
| `deploy.bat` | 新增 Uvicorn 启动（`:8001`）处理 WebSocket；部署时自动重启两个服务 |

## Windows Server 手动操作

### 1. 拉取最新代码

```powershell
cd C:\SwapCampus
git pull origin main
```

### 2. 编辑 nginx.conf

找到 Windows Server 上的 nginx 配置文件（通常在 `C:\nginx\conf\nginx.conf` 或 nginx 安装目录下的 `conf\nginx.conf`），做以下修改：

#### 2.1 新增 WebSocket 代理块

在你的 HTTPS `server` 块中添加（如果已有 `/ws/` 块则替换）：

```nginx
location /ws/ {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

#### 2.2 已有 location 块添加 X-Forwarded-Proto

在 `/api/`、`/media/`、`/admin/` 等 `location` 块中，各添加一行：

```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

#### 完整示例

```nginx
server {
    listen 443 ssl http2;
    server_name geleme.online;

    ssl_certificate     /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    client_max_body_size 20M;

    # 前端静态文件
    location / {
        root C:\SwapCampus\frontend\dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # HTTP API → Waitress :8000
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket → Uvicorn :8001
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 媒体文件 → Django :8000
    location /media/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin → Django :8000
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP 自动跳转 HTTPS
server {
    listen 80;
    server_name geleme.online;
    return 301 https://$host$request_uri;
}
```

### 3. 确认 .env 配置

确保 `C:\SwapCampus\.env`（与 `deploy.bat` 同目录）中有：

```
DJANGO_ENV=prod
DEBUG=False
ALLOWED_HOSTS=geleme.online,127.0.0.1,localhost
```

### 4. 重新构建前端

```powershell
cd C:\SwapCampus\frontend
npm install --registry=https://registry.npmmirror.com
npm run build
```

### 5. 重新部署后端

```powershell
cd C:\SwapCampus
deploy.bat
```

`deploy.bat` 启动的两个服务：

| 服务 | 端口 | 技术栈 | 职责 |
|------|------|--------|------|
| Waitress | 8000 | WSGI | HTTP REST API |
| Uvicorn | 8001 | ASGI | WebSocket 实时通讯 |

### 6. 重载 nginx

```powershell
nginx -s reload
```

### 7. 验证

浏览器访问 `https://geleme.online`，打开开发者工具（F12）：

- **Console**：不应再有 `Mixed Content` 或 `SecurityError: WebSocket` 错误
- **Network → WS**：应该能看到 `wss://geleme.online/ws/chat/...` 连接成功（状态 101）
- **功能**：聊天消息发送后，对方打开会话，已读/未读标签应正常切换

## 回滚

如果出现问题，恢复到修改前的版本：

```powershell
cd C:\SwapCampus
git stash
# 手动还原 nginx.conf 配置
nginx -s reload
deploy.bat
```

---

> 修改日期：2026-06-06
> 关联 Commit：见仓库提交记录
