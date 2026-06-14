"""管理面板 API 视图."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import Product, Report
from apps.products.services import approve_product, reject_product
from apps.transactions.models import Order
from apps.users.models import CreditRecord
from apps.users.services import add_credit_record, create_notification
from core.utils import build_success_response

User = get_user_model()


def _require_staff(request):
    """检查管理员权限，非管理员返回 403."""
    if not request.user.is_staff:
        return Response(
            {"success": False, "data": None, "error": {"code": "FORBIDDEN", "message": "仅管理员可访问"}},
            status=403,
        )
    return None


# ═══════════════════════════════════════════════════════════
# 数据看板
# ═══════════════════════════════════════════════════════════
class DashboardView(APIView):
    """管理仪表盘数据.

    GET /api/admin/dashboard/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="管理仪表盘",
        description="返回平台核心统计数据（仅管理员）",
    )
    def get(self, request):
        err = _require_staff(request)
        if err:
            return err

        total_users = User.objects.filter(is_active=True).count()
        active_products = Product.objects.filter(status=Product.Status.ACTIVE).count()
        pending_products = Product.objects.filter(status=Product.Status.PENDING).count()
        pending_orders = Order.objects.filter(status=Order.Status.PENDING).count()
        completed_orders = Order.objects.filter(status=Order.Status.COMPLETED).count()
        pending_reports = Report.objects.filter(status=Report.Status.PENDING).count()

        recent_users = User.objects.filter(is_active=True).order_by("-date_joined")[:5]
        recent_users_data = [
            {
                "id": str(u.id),
                "username": u.username,
                "nickname": u.get_display_name(),
                "credit_score": u.credit_score,
                "date_joined": u.date_joined,
            }
            for u in recent_users
        ]

        data = {
            "total_users": total_users,
            "active_products": active_products,
            "pending_products": pending_products,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "pending_reports": pending_reports,
            "recent_registrations": recent_users_data,
        }
        return Response(build_success_response(data))


# ═══════════════════════════════════════════════════════════
# 商品审核
# ═══════════════════════════════════════════════════════════
class AdminProductListView(APIView):
    """管理员商品列表.

    GET /api/admin/products/
    默认筛选待审核商品。
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        err = _require_staff(request)
        if err:
            return err

        status_filter = request.query_params.get("status", "pending")
        search = request.query_params.get("search", "")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))

        qs = Product.objects.select_related("seller", "category").prefetch_related("images", "tags")

        if status_filter:
            qs = qs.filter(status=status_filter)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        total = qs.count()
        qs = qs.order_by("-created_at")[(page - 1) * page_size : page * page_size]

        products_data = []
        for p in qs:
            first_img = p.images.first()
            products_data.append({
                "id": str(p.id),
                "title": p.title,
                "price": str(p.price),
                "status": p.status,
                "seller": {
                    "id": str(p.seller.id),
                    "username": p.seller.username,
                    "nickname": p.seller.get_display_name(),
                },
                "category": {"id": str(p.category.id), "name": p.category.name} if p.category else None,
                "image": first_img.image.url if first_img else None,
                "view_count": p.view_count,
                "created_at": p.created_at,
            })

        return Response(build_success_response({
            "products": products_data,
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }))


class AdminProductApproveView(APIView):
    """审核商品.

    POST /api/admin/products/<id>/moderate/?action=approve  → 审核通过（仅待审核状态）
    POST /api/admin/products/<id>/moderate/?action=hide     → 下架/驳回
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        err = _require_staff(request)
        if err:
            return err

        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response(
                {"success": False, "data": None, "error": {"message": "商品不存在"}},
                status=404,
            )

        action = request.query_params.get("action", "approve")

        if action == "approve":
            if product.status != Product.Status.PENDING:
                return Response(
                    {"success": False, "data": None, "error": {"message": "只能审核待审核状态的商品"}},
                    status=400,
                )
            approve_product(product)
            create_notification(
                recipient=product.seller,
                ntype="system",
                title="商品审核通过",
                content=f"你的商品「{product.title}」已通过审核，现已上架。",
                related_product=product,
            )
        elif action == "hide":
            reject_product(product)
            create_notification(
                recipient=product.seller,
                ntype="system",
                title="商品审核未通过",
                content=f"你的商品「{product.title}」未通过审核，已被驳回。",
                related_product=product,
            )
        else:
            return Response(
                {"success": False, "data": None, "error": {"message": f"无效操作: {action}"}},
                status=400,
            )

        return Response(build_success_response({
            "id": str(product.id),
            "status": product.status,
        }))


# ═══════════════════════════════════════════════════════════
# 举报管理
# ═══════════════════════════════════════════════════════════
class AdminReportListView(APIView):
    """管理员举报列表.

    GET /api/admin/reports/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        err = _require_staff(request)
        if err:
            return err

        status_filter = request.query_params.get("status", "")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))

        qs = Report.objects.select_related("reporter", "product").order_by("-created_at")
        if status_filter:
            qs = qs.filter(status=status_filter)

        total = qs.count()
        qs = qs[(page - 1) * page_size : page * page_size]

        reports_data = []
        for r in qs:
            reports_data.append({
                "id": str(r.id),
                "reason": r.reason,
                "description": r.description,
                "status": r.status,
                "reporter": {
                    "id": str(r.reporter.id),
                    "username": r.reporter.username,
                    "nickname": r.reporter.get_display_name(),
                },
                "product": {
                    "id": str(r.product.id),
                    "title": r.product.title,
                    "status": r.product.status,
                },
                "handled_note": r.handled_note,
                "created_at": r.created_at,
            })

        return Response(build_success_response({
            "reports": reports_data,
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }))


class AdminReportHandleView(APIView):
    """处理举报.

    POST /api/admin/reports/<id>/handle/
    body: {"action": "resolve"|"dismiss", "note": "处理备注"}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        err = _require_staff(request)
        if err:
            return err

        try:
            report = Report.objects.get(id=id)
        except Report.DoesNotExist:
            return Response(
                {"success": False, "data": None, "error": {"message": "举报不存在"}},
                status=404,
            )

        action = request.data.get("action", "resolve")
        note = request.data.get("note", "")

        product = report.product
        reporter = report.reporter
        seller = product.seller

        if action == "dismiss":
            # 驳回举报：不动商品，通知举报人
            report.status = Report.Status.DISMISSED
            create_notification(
                recipient=reporter,
                ntype="system",
                title="举报已驳回",
                content=f"你对「{product.title}」的举报经审核已被驳回。",
                related_product=product,
            )
        else:
            # 举报成立：下架商品 + 扣分 + 通知双方
            report.status = Report.Status.RESOLVED
            Product.objects.filter(pk=product.pk).update(status=Product.Status.BANNED)
            add_credit_record(
                user=seller,
                change=-20,
                reason="violation",
                description=f"商品「{product.title}」被举报，管理员已处理",
            )
            create_notification(
                recipient=reporter,
                ntype="system",
                title="举报已处理",
                content=f"你对「{product.title}」的举报已处理，该商品已被下架，感谢反馈。",
                related_product=product,
            )
            create_notification(
                recipient=seller,
                ntype="system",
                title="商品违规下架",
                content=f"你的商品「{product.title}」因被举报已被管理员下架，信用分扣除 20 分。",
                related_product=product,
            )

        report.handled_by = request.user
        report.handled_note = note
        report.save(update_fields=["status", "handled_by", "handled_note", "updated_at"])

        return Response(build_success_response({
            "id": str(report.id),
            "status": report.status,
            "handled_note": report.handled_note,
        }))


# ═══════════════════════════════════════════════════════════
# 用户管理
# ═══════════════════════════════════════════════════════════
class AdminUserListView(APIView):
    """管理员用户列表.

    GET /api/admin/users/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        err = _require_staff(request)
        if err:
            return err

        search = request.query_params.get("search", "")
        is_active = request.query_params.get("is_active", "")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))

        qs = User.objects.order_by("-date_joined")
        if search:
            qs = qs.filter(Q(username__icontains=search) | Q(nickname__icontains=search))
        if is_active == "true":
            qs = qs.filter(is_active=True)
        elif is_active == "false":
            qs = qs.filter(is_active=False)

        total = qs.count()
        qs = qs[(page - 1) * page_size : page * page_size]

        users_data = []
        for u in qs:
            users_data.append({
                "id": str(u.id),
                "username": u.username,
                "nickname": u.get_display_name(),
                "email": u.email,
                "campus": u.campus,
                "credit_score": u.credit_score,
                "is_active": u.is_active,
                "is_staff": u.is_staff,
                "date_joined": u.date_joined,
            })

        return Response(build_success_response({
            "users": users_data,
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }))


class AdminUserBanView(APIView):
    """封禁/解封用户.

    POST /api/admin/users/<id>/ban/
    body: {"is_active": true|false}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        err = _require_staff(request)
        if err:
            return err

        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(
                {"success": False, "data": None, "error": {"message": "用户不存在"}},
                status=404,
            )

        if user.is_staff and not request.user.is_superuser:
            return Response(
                {"success": False, "data": None, "error": {"message": "不能封禁管理员"}},
                status=403,
            )

        is_active = request.data.get("is_active", False)
        user.is_active = is_active
        user.save(update_fields=["is_active"])

        # 封禁联动：下架商品 + 取消订单 + 通知交易对方
        if not is_active:
            CreditRecord.objects.create(
                user=user,
                change=0,
                reason=CreditRecord.ChangeReason.VIOLATION,
                description="管理员封禁账号",
                score_after=user.credit_score,
            )

            # 1. 下架所有非终态商品
            Product.objects.filter(
                seller=user,
                status__in=[Product.Status.PENDING, Product.Status.ACTIVE, Product.Status.RESERVED],
            ).update(status=Product.Status.HIDDEN)

            # 2. 找出所有进行中的订单（用户作为买家或卖家）
            ongoing_statuses = [Order.Status.PENDING, Order.Status.ACCEPTED, Order.Status.FACE_CONFIRM]
            affected_orders = list(
                Order.objects.filter(
                    Q(buyer=user) | Q(seller=user),
                    status__in=ongoing_statuses,
                ).select_related("buyer", "seller", "product")
            )

            # 3. 批量取消订单
            if affected_orders:
                order_ids = [o.id for o in affected_orders]
                Order.objects.filter(id__in=order_ids).update(
                    status=Order.Status.CANCELLED,
                    cancel_reason="对方账号已被封禁",
                    cancel_by=request.user,
                )

            # 4. 通知所有交易对方
            banned_name = user.get_display_name()
            for order in affected_orders:
                counterparty = order.seller if order.buyer == user else order.buyer
                create_notification(
                    recipient=counterparty,
                    ntype="system",
                    title="交易对方账号已封禁",
                    content=(
                        f"用户「{banned_name}」的账号已被管理员封禁，"
                        f"商品「{order.product.title}」的相关订单已自动取消。"
                    ),
                    related_order=order,
                )

        return Response(build_success_response({
            "id": str(user.id),
            "is_active": user.is_active,
        }))
