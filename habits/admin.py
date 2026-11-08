from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "time",
        "place",
        "periodicity",
        "duration",
        "is_pleasant",
        "is_public",
    )
    list_filter = ("is_pleasant", "is_public", "periodicity")
    search_fields = ("action", "place", "user__username")
