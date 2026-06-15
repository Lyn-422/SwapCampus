"""管理面板 API 路由."""

from django.urls import path

from apps.admin_panel.views import (
    AdminApproveUserView,
    AdminOrderListView,
    AdminPendingUserListView,
    AdminProductApproveView,
    AdminProductListView,
    AdminRejectUserView,
    AdminReportHandleView,
    AdminReportListView,
    AdminUserBanView,
    AdminUserListView,
    DashboardView,
)

urlpatterns = [
    # 数据看板
    path("dashboard/", DashboardView.as_view(), name="admin-dashboard"),
    # 商品审核
    path("products/", AdminProductListView.as_view(), name="admin-products"),
    path("products/<uuid:id>/moderate/", AdminProductApproveView.as_view(), name="admin-product-moderate"),
    # 举报管理
    path("reports/", AdminReportListView.as_view(), name="admin-reports"),
    path("reports/<uuid:id>/handle/", AdminReportHandleView.as_view(), name="admin-report-handle"),
    # 订单管理
    path("orders/", AdminOrderListView.as_view(), name="admin-orders"),
    # 用户管理
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    # 注册审核（pending 必须放在 <uuid:id> 之前，避免被 UUID 匹配）
    path("users/pending/", AdminPendingUserListView.as_view(), name="admin-users-pending"),
    path("users/<uuid:id>/approve/", AdminApproveUserView.as_view(), name="admin-user-approve"),
    path("users/<uuid:id>/reject/", AdminRejectUserView.as_view(), name="admin-user-reject"),
    path("users/<uuid:id>/ban/", AdminUserBanView.as_view(), name="admin-user-ban"),
]
