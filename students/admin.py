# ============================================================
# STUDENTS APP ADMIN
# ============================================================

from django.contrib import admin

from .models import (
    Student,
    ClassRoom,
)


# ============================================================
# CLASS ROOM ADMIN
# ============================================================

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "status",
        "created_at",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "status",
    )

    ordering = (
        "name",
    )


# ============================================================
# STUDENT ADMIN
# ============================================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "student_id",
        "first_name",
        "last_name",
        "class_room",
        "user",
    )

    search_fields = (
        "student_id",
        "first_name",
        "last_name",
        "user__username",
        "user__first_name",
        "user__last_name",
    )

    list_filter = (
        "class_room",
    )

    autocomplete_fields = (
        "user",
        "class_room",
    )

    ordering = (
        "first_name",
        "last_name",
    )

