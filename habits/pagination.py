from rest_framework.pagination import LimitOffsetPagination


class HabitLimitOffsetPagination(LimitOffsetPagination):
    """Пагинация limit/offset с параметрами по умолчанию."""

    default_limit = 5
    max_limit = 50
