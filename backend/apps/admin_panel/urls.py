"""管理面板 API 路由."""

from django.urls import path

from apps.admin_panel.views import (
    AdminProductApproveView,
    AdminProductListView,
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
    # 用户管理
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    path("users/<uuid:id>/ban/", AdminUserBanView.as_view(), name="admin-user-ban"),
]
