# SwapCampus — 校园闲置物品交易平台

北京林业大学 · 信息学院 《软件工程（课程设计）》T-02 选题项目

## 项目简介

面向北京林业大学师生的 C2C 校园闲置物品交易 Web 平台。提供商品发布与检索、站内实时通讯、面交确认、信用评价等核心功能，以提高校内资源流转率，为师生提供安全便捷的交易体验。

## 技术栈

| 层次 | 选型 |
|------|------|
| 后端 | Django 5 + Django REST Framework + Django Channels |
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 数据库 | SQLite（开发）/ PostgreSQL 16（生产） |
| 实时通讯 | WebSocket（Channels + Redis） |
| 对象存储 | MinIO |
| 容器化 | Docker + Docker Compose |

## 快速开始

```bash
# 后端
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver

# 前端
cd frontend
npm install && npm run dev

# Docker 部署
docker compose -f docker/docker-compose.yml up -d
```

## 团队

4 人，前后端分层分工。详见 [CLAUDE.md](./CLAUDE.md)

## 课程信息

- **选题编号**：T-02
- **开发周期**：D1-D14（2周集中实习）
- **指导教师**：__________
