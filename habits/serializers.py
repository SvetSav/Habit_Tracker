from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор привычки с прогонкой модели через full_clean()."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "last_notification_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "last_notification_date",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance if self.instance is not None else Habit()
        for field, value in attrs.items():
            setattr(instance, field, value)
        try:
            instance.full_clean(exclude=["user"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs
