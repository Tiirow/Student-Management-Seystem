from django.contrib import admin

from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "credit_hours",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "code",
        "name",
    )

    ordering = (
        "name",
    )
    