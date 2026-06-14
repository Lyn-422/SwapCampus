"""初始化测试数据 — 涵盖所有功能场景.
Usage: python manage.py seed_users
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.products.models import Category, Product
from apps.transactions.models import Order, Review
from apps.users.models import CreditRecord, User


class Command(BaseCommand):
    help = "创建完整测试数据（用户 + 商品 + 订单 + 评价 + 信用记录）"

    def handle(self, *args, **options):
        # ── 确保有分类（依赖 seed_products） ──
        if not Category.objects.exists():
            self.stdout.write(self.style.ERROR("请先运行 python manage.py seed_products"))
            return

        default_category = Category.objects.first()

        # ═══════════════════════════════════════════════
        # 1. 创建用户
        # ═══════════════════════════════════════════════
        users = {}
        user_defs = [
            ("admin", "admin123", "管理员", True, True),
            ("20250001", "123456", "小明", False, False),
            ("20250002", "123456", "小刚", False, False),
            ("20250003", "123456", "小林", False, False),
            ("20250004", "123456", "小美", False, False),
        ]
        for username, pwd, nickname, is_staff, is_superuser in user_defs:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"nickname": nickname, "is_staff": is_staff, "is_superuser": is_superuser},
            )
            if created:
                user.set_password(pwd)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"创建用户 {username}（{nickname}）"))
            else:
                self.stdout.write(self.style.WARNING(f"跳过 {username}（已存在）"))
            users[username] = user

        # ═══════════════════════════════════════════════
        # 2. 设置用户状态和信用记录
        # ═══════════════════════════════════════════════
        now = timezone.now()

        # 小林 — 可信卖家：信用155 + 完成3单 + 无违规
        xiaolin = users["20250003"]
        xiaolin.credit_score = 155
        xiaolin.save(update_fields=["credit_score"])
        # 给小林补初始分记录
        if not CreditRecord.objects.filter(user=xiaolin, reason=CreditRecord.ChangeReason.INITIAL).exists():
            CreditRecord.objects.create(
                user=xiaolin, change=55, reason=CreditRecord.ChangeReason.INITIAL,
                description="初始积分（模拟信用优秀）", score_after=155,
            )

        # 小明 — 200天前有违规（已过180天窗口），当前信用120
        xiaoming = users["20250001"]
        xiaoming.credit_score = 120
        xiaoming.save(update_fields=["credit_score"])
        if not CreditRecord.objects.filter(user=xiaoming, reason=CreditRecord.ChangeReason.VIOLATION).exists():
            rec = CreditRecord.objects.create(
                user=xiaoming, change=-20, reason=CreditRecord.ChangeReason.VIOLATION,
                description="商品违规下架（200天前，已过期）", score_after=120,
            )
            rec.created_at = now - timedelta(days=200)
            rec.save(update_fields=["created_at"])

        # 小刚 — 30天前有违规（仍在180天内），曾被封禁，当前信用90
        xiaogang = users["20250002"]
        xiaogang.credit_score = 90
        xiaogang.save(update_fields=["credit_score"])
        if not CreditRecord.objects.filter(user=xiaogang, reason=CreditRecord.ChangeReason.VIOLATION).exists():
            rec = CreditRecord.objects.create(
                user=xiaogang, change=-20, reason=CreditRecord.ChangeReason.VIOLATION,
                description="管理员封禁账号（30天前，仍在180天窗口内）", score_after=90,
            )
            rec.created_at = now - timedelta(days=30)
            rec.save(update_fields=["created_at"])

        # 小美 — 新用户，信用100初始
        xiaomei = users["20250004"]
        xiaomei.credit_score = 100
        xiaomei.save(update_fields=["credit_score"])

        # ═══════════════════════════════════════════════
        # 3. 创建商品
        # ═══════════════════════════════════════════════
        products = {}
        product_defs = [
            # (卖家, 标题, 价格, 状态)
            (xiaolin, "二手高数教材（几乎全新）", 25, Product.Status.ACTIVE),
            (xiaolin, "机械键盘 Cherry MX 红轴", 200, Product.Status.ACTIVE),
            (xiaolin, "电风扇 落地扇 三档", 58, Product.Status.SOLD),
            (xiaolin, "台灯 LED 护眼", 40, Product.Status.SOLD),
            (xiaoming, "四级单词书 星火英语", 15, Product.Status.ACTIVE),
            (xiaogang, "蓝牙耳机 漫步者", 88, Product.Status.ACTIVE),
            (xiaomei, "瑜伽垫 加厚 防滑", 35, Product.Status.ACTIVE),
        ]
        for seller, title, price, status in product_defs:
            p, created = Product.objects.get_or_create(
                title=title, seller=seller,
                defaults={
                    "price": price, "status": status,
                    "description": f"{title} — 校园面交，欢迎咨询。",
                    "category": default_category,
                },
            )
            key = f"{seller.username}_{title[:4]}"
            products[key] = p
            if created:
                self.stdout.write(self.style.SUCCESS(f"  创建商品「{title}」({seller.nickname})"))

        # ═══════════════════════════════════════════════
        # 4. 创建订单（展示各种状态）
        # ═══════════════════════════════════════════════

        # 4a. 小林完成3笔作为卖家的订单 → 满足可信卖家条件
        for buyer, prod_title in [
            (xiaoming, "台灯 LED 护眼"),
            (xiaogang, "电风扇 落地扇 三档"),
            (xiaomei, "二手高数教材（几乎全新）"),
        ]:
            prod = Product.objects.get(title=prod_title, seller=xiaolin)
            order, created = Order.objects.get_or_create(
                buyer=buyer, seller=xiaolin, product=prod,
                defaults={
                    "status": Order.Status.COMPLETED,
                    "completed_at": now - timedelta(days=10),
                },
            )
            if created and order.status == Order.Status.COMPLETED:
                prod.status = Product.Status.SOLD
                prod.save(update_fields=["status"])

        # 恢复前两个商品为 ACTIVE（小林仍有两件在售）
        for t in ["二手高数教材（几乎全新）", "机械键盘 Cherry MX 红轴"]:
            Product.objects.filter(title=t, seller=xiaolin).update(status=Product.Status.ACTIVE)

        # 修复：台灯和电风扇保持 SOLD，但高数教材改成被小美买了然后完成
        # 实际上小美的订单已经创建了（高数教材），但小林还需要另一笔完成订单
        # 目前已完成：小明买台灯、小刚买电风扇、小美买高数教材 → 3笔 ✓

        # 4b. 待确认订单（pending）
        keyboard = products.get(f"{xiaolin.username}_机械")
        if keyboard and not Order.objects.filter(product=keyboard, status=Order.Status.PENDING).exists():
            Order.objects.get_or_create(
                buyer=xiaomei, seller=xiaolin, product=keyboard,
                defaults={"status": Order.Status.PENDING},
            )

        # 4c. 已接受（accepted）
        headphones = Product.objects.get(title="蓝牙耳机 漫步者", seller=xiaogang)
        if not Order.objects.filter(product=headphones, status=Order.Status.ACCEPTED).exists():
            Order.objects.get_or_create(
                buyer=xiaoming, seller=xiaogang, product=headphones,
                defaults={"status": Order.Status.ACCEPTED, "meet_location": "图书馆门口"},
            )

        # 4d. 面交确认中（face_confirm）
        yoga = Product.objects.get(title="瑜伽垫 加厚 防滑", seller=xiaomei)
        if not Order.objects.filter(product=yoga, status=Order.Status.FACE_CONFIRM).exists():
            Order.objects.get_or_create(
                buyer=xiaolin, seller=xiaomei, product=yoga,
                defaults={"status": Order.Status.FACE_CONFIRM, "meet_location": "体育馆"},
            )

        # 4e. 已取消（cancelled）
        wordbook = Product.objects.get(title="四级单词书 星火英语", seller=xiaoming)
        if not Order.objects.filter(product=wordbook, status=Order.Status.CANCELLED).exists():
            Order.objects.get_or_create(
                buyer=xiaogang, seller=xiaoming, product=wordbook,
                defaults={
                    "status": Order.Status.CANCELLED,
                    "cancel_reason": "不想要了",
                    "cancel_by": xiaogang,
                },
            )

        order_count = Order.objects.count()
        self.stdout.write(self.style.SUCCESS(f"  共 {order_count} 笔订单"))

        # ═══════════════════════════════════════════════
        # 5. 创建评价（演示追评）
        # ═══════════════════════════════════════════════
        # 找一个已完成的订单：小明买台灯（小林是卖家）
        lamp = Product.objects.get(title="台灯 LED 护眼", seller=xiaolin)
        completed_order = Order.objects.filter(
            product=lamp, buyer=xiaoming, status=Order.Status.COMPLETED,
        ).first()

        if completed_order:
            # 小明（买家）首次评价卖家小林 → 好评5星
            r1, created = Review.objects.get_or_create(
                order=completed_order, reviewer=xiaoming, review_type=Review.ReviewType.BUYER_TO_SELLER,
                defaults={
                    "reviewee": xiaolin, "rating": 5,
                    "content": "卖家很热情，台灯成色很好，面交顺利！",
                },
            )
            if created:
                completed_order.buyer_review_count = 1
                completed_order.save(update_fields=["buyer_review_count"])

            # 小明追评卖家小林
            r2, created = Review.objects.get_or_create(
                order=completed_order,
                reviewer=xiaoming,
                review_type=Review.ReviewType.BUYER_TO_SELLER,
                content="用了一周，质量确实不错，追评推荐！",
                defaults={"reviewee": xiaolin, "rating": 5},
            )
            if created:
                completed_order.buyer_review_count = 2
                completed_order.save(update_fields=["buyer_review_count"])
                self.stdout.write(self.style.SUCCESS("  创建追评示例：小明→小林（首次+追评）"))

            # 小林评价买家小明 → 好评4星
            r3, created = Review.objects.get_or_create(
                order=completed_order, reviewer=xiaolin, review_type=Review.ReviewType.SELLER_TO_BUYER,
                defaults={
                    "reviewee": xiaoming, "rating": 4,
                    "content": "买家很爽快，准时到达约定地点。",
                },
            )
            if created:
                completed_order.seller_review_count = 1
                completed_order.save(update_fields=["seller_review_count"])

        # ═══════════════════════════════════════════════
        # 6. 总结
        # ═══════════════════════════════════════════════
        self.stdout.write(self.style.SUCCESS(
            "\n测试数据初始化完成！\n"
            f"  用户: admin(管理员) / 20250001小明 / 20250002小刚 / 20250003小林 / 20250004小美\n"
            f"  密码: admin的密码是admin123，其余都是123456\n\n"
            "功能演示场景：\n"
            "  [可信卖家] 小林 — 信用155 + 3笔卖单 + 无违规 -> 商品卡片和个人主页有绿色标签\n"
            "  [违规过期] 小明 — 200天前违规已过期（180天外），信用120\n"
            "  [违规期内] 小刚 — 30天前违规仍在窗口内（180天内），不可信\n"
            "  [追评演示] 小明对台灯订单评价了两次（小明->小林：5星 + 追评）\n"
            "  [订单状态] pending/accepted/face_confirm/completed/cancelled 全覆盖\n"
            "  [通知演示] 下单/交易完成后，登录对应账号查看通知\n"
            "  [管理后台] 登录admin账号访问 /admin 可体验管理功能"
        ))
