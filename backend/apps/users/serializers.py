"""用户体系序列化器."""

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import CreditRecord, Notification

User = get_user_model()


# ═══════════════════════════════════════════════════════════
# 注册
# ═══════════════════════════════════════════════════════════
class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器.

    学号作为 username，密码需符合 Django 密码验证策略。
    """

    password = serializers.CharField(
        write_only=True, required=True
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value):
        """自定义密码验证，提供更清晰的错误提示."""
        from django.core.exceptions import ValidationError as DjangoValidationError
        from django.contrib.auth.password_validation import validate_password

        try:
            validate_password(value)
        except DjangoValidationError as e:
            # 将 Django 的错误消息转换为更友好的中文提示
            error_messages = []
            for msg in e.messages:
                if "at least" in msg or "太短" in msg:
                    error_messages.append("密码太短（至少 8 个字符）")
                elif "numeric" in msg or "数字" in msg:
                    error_messages.append("密码不能全为数字")
                elif "common" in msg or "常见" in msg or "太常见" in msg:
                    error_messages.append("密码太简单（如 12345678、password 等），请使用更复杂的密码")
                elif "similar" in msg or "相似" in msg:
                    error_messages.append("密码不能与学号过于相似")
                else:
                    error_messages.append(msg)
            raise serializers.ValidationError(error_messages)
        return value

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "password_confirm",
            "email",
            "nickname",
            "campus",
            "student_id_card",
        ]
        extra_kwargs = {
            "username": {
                "help_text": "北京林业大学学号（8-9 位数字）",
                "min_length": 8,
                "max_length": 9,
            },
            "email": {"required": False},
            "nickname": {"required": False},
            "campus": {"required": False},
            "student_id_card": {"required": True},
        }

    def validate_student_id_card(self, value):
        max_size_mb = 5
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"学生证照片不能超过 {max_size_mb} MB"
            )
        if hasattr(value, "content_type") and value.content_type not in (
            "image/jpeg", "image/png", "image/webp",
        ):
            raise serializers.ValidationError("仅支持 JPEG、PNG、WebP 格式的图片")
        return value

    def validate_username(self, value):
        """校验学号格式：8-9 位数字."""
        if not re.match(r"^\d{8,9}$", value):
            raise serializers.ValidationError("学号必须为 8-9 位数字")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该学号已注册")
        return value

    def validate(self, attrs):
        """校验两次密码一致."""
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "两次密码输入不一致"})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        student_id_card = validated_data.pop("student_id_card", None)
        user = User.objects.create_user(
            **validated_data,
            is_active=False,
            status=User.AccountStatus.PENDING,
        )
        user.set_password(password)
        if student_id_card:
            user.student_id_card = student_id_card
            user.save(update_fields=["student_id_card"])
        return user


# ═══════════════════════════════════════════════════════════
# 用户信息
# ═══════════════════════════════════════════════════════════
class UserSerializer(serializers.ModelSerializer):
    """用户公开信息序列化器.

    供商品详情页展示卖家信息、聊天列表显示对话用户等场景使用。
    不暴露 email、手机号等隐私字段。
    """

    credit_level = serializers.CharField(read_only=True)
    is_trusted_seller = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nickname",
            "avatar",
            "credit_score",
            "credit_level",
            "is_trusted_seller",
            "campus",
            "bio",
            "date_joined",
        ]
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    """用户个人信息序列化器（仅本人可查看/编辑）.

    包含 email 等隐私字段，用于个人主页展示。
    """

    credit_level = serializers.CharField(read_only=True)
    is_trusted_seller = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "nickname",
            "avatar",
            "credit_score",
            "credit_level",
            "is_trusted_seller",
            "campus",
            "bio",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "username",
            "credit_score",
            "is_staff",
            "is_trusted_seller",
            "credit_level",
            "date_joined",
        ]

    def update(self, instance, validated_data):
        """更新用户信息，avatar 字段需要特殊处理."""
        # 如果 avatar 在数据中且是空字符串，视为清除头像
        if "avatar" in validated_data and (
            validated_data["avatar"] is None
            or validated_data["avatar"] == ""
        ):
            instance.avatar.delete(save=False)
            validated_data.pop("avatar", None)
        return super().update(instance, validated_data)


class UserUpdateSerializer(UserProfileSerializer):
    """用户信息更新序列化器（不包含任何只读字段）.

    专门处理 PATCH 请求，允许部分更新。
    """

    pass


class UserDetailSerializer(serializers.ModelSerializer):
    """管理员用户详情序列化器（含学生证、状态等敏感字段）."""

    student_id_card_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "nickname", "email", "campus",
            "credit_score", "is_active", "is_staff", "status",
            "student_id_card_url", "rejection_reason", "date_joined",
        ]

    def get_student_id_card_url(self, obj):
        if obj.student_id_card:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.student_id_card.url)
            return obj.student_id_card.url
        return None


# ═══════════════════════════════════════════════════════════
# 积分记录
# ═══════════════════════════════════════════════════════════
class CreditRecordSerializer(serializers.ModelSerializer):
    """信用积分记录序列化器."""

    reason_display = serializers.CharField(source="get_reason_display", read_only=True)

    class Meta:
        model = CreditRecord
        fields = [
            "id",
            "user",
            "change",
            "reason",
            "reason_display",
            "description",
            "score_after",
            "related_order",
            "created_at",
        ]
        read_only_fields = fields


# ═══════════════════════════════════════════════════════════
# 站内通知
# ═══════════════════════════════════════════════════════════
class NotificationSerializer(serializers.ModelSerializer):
    """站内通知序列化器."""

    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id", "type", "type_display", "title", "content",
            "is_read", "related_order", "related_product", "created_at",
        ]
        read_only_fields = fields
