from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Telegram", {"fields": ("telegram_chat_id",)}),)
    list_display = ("username", "email", "telegram_chat_id", "is_staff")
