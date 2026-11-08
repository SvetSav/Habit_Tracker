from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CustomTokenObtainPairSerializer,
    LinkTelegramSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Авторизация по JWT (возвращает access и refresh)."""

    serializer_class = CustomTokenObtainPairSerializer


class ProfileView(generics.RetrieveAPIView):
    """Профиль текущего пользователя."""

    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LinkTelegramView(APIView):
    """Привязка Telegram chat_id к текущему пользователю."""

    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        request=LinkTelegramSerializer,
        responses={
            200: inline_serializer(
                name="LinkTelegramResponse",
                fields={
                    "status": serializers.CharField(),
                    "chat_id": serializers.CharField(),
                },
            ),
        },
    )
    def post(self, request):
        serializer = LinkTelegramSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_id = serializer.validated_data["chat_id"]

        request.user.telegram_chat_id = chat_id
        request.user.save(update_fields=["telegram_chat_id"])

        return Response(
            {"status": "ok", "chat_id": chat_id},
            status=status.HTTP_200_OK,
        )
