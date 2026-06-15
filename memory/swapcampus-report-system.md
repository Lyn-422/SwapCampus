---
name: swapcampus-report-system
description: 完善了 SwapCampus 举报处理系统的开发和优化过程
metadata: 
  node_type: memory
  type: project
  date: 2026-06-13
  originSessionId: 1a2f5c1f-8d5f-4038-9b54-bf718b10c57f
---

## 举报功能开发与优化

### 1. Bug 修复
- **问题**：用户用其他账号举报商品时，提示"不能举报自己的商品"
- **原因**：`product.seller == request.user` 比较的是模型实例对象而非主键，可能导致误判
- **修复**：改为比较主键 `product.seller_id == request.user.id`
- **文件**：`backend/apps/products/views.py:317`

### 2. 举报处理系统完善
原系统只有提交举报，没有处理流程。新增完整闭环：

#### 模型扩展（Report）
- `action_taken`：处理方式（枚举）
- `credit_deducted`：扣除信用分数值
- `seller_banned_days`：封禁天数（-1为永久）

#### 处理方式（8种）
| 操作 | 效果 |
|------|------|
| 仅下架商品 | 隐藏商品，不处罚 |
| 下架+警告 | 下架 + 发通知 |
| 下架+扣10/20/50分 | 下架 + 扣分 + 通知 |
| 下架+封禁7天 | 下架 + 扣分 + 临时封号 |
| 下架+永久封禁 | 下架 + 扣分 + 永久封号 |
| 举报不成立 | 驳回 + 通知举报人 |

#### 自动通知
- 卖家收到：商品下架、扣分、封禁通知
- 举报人收到：举报处理结果通知

### 3. Django Admin 界面优化
- 彩色标签区分不同原因/状态
- 批量操作按钮（8种处理方式）
- 显示卖家当前信用分
- 优化标签样式防止文字换行

### 4. 协作注意事项
- **makemigrations**：修改模型后执行，生成的迁移文件要提交到 Git
- **migrate**：所有人部署时执行，不提交
- 管理员设置：通过 Django shell 设置 `is_staff=True` 和 `is_superuser=True`

### 相关文件
- `backend/apps/products/views.py` - 举报创建接口
- `backend/apps/products/models.py` - Report 模型
- `backend/apps/products/admin.py` - Admin 界面配置
- `backend/apps/admin_panel/views.py` - 管理 API

**Why:** 原举报系统只是个"标记已读"，没有实际约束作用，管理员处理起来没有依据和手段。

**How to apply:** 参考本次的模型设计，举报处理应该包含：处理方式枚举、处罚措施记录、双方通知机制、后台可视化操作界面。
