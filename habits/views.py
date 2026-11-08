from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Habit
from .pagination import HabitLimitOffsetPagination
from .permissions import IsOwner
from .serializers import HabitSerializer

_id_param = OpenApiParameter(
    name="id",
    type=int,
    location=OpenApiParameter.PATH,
    description="ID привычки",
)


@extend_schema_view(
    retrieve=extend_schema(parameters=[_id_param]),
    update=extend_schema(parameters=[_id_param]),
    partial_update=extend_schema(parameters=[_id_param]),
    destroy=extend_schema(parameters=[_id_param]),
)
class HabitViewSet(viewsets.ModelViewSet):
    """CRUD-операции с привычками.

    list:  список своих привычек (с пагинацией limit/offset)
    create / retrieve / update / destroy:  только свои
    public:  список публичных привычек (только чтение)
    """

    serializer_class = HabitSerializer
    pagination_class = HabitLimitOffsetPagination

    def get_queryset(self):
        if self.action == "public":
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.action == "public":
            return [permissions.AllowAny()]
        if self.action in ("list", "create"):
            return [permissions.IsAuthenticated()]
        if self.action in ("retrieve", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.AllowAny],
    )
    def public(self, request):
        """Публичные привычки. Изменение/удаление недоступно."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
