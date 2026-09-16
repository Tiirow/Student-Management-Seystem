# ============================================================
# TEACHER ADMIN
# ============================================================

from django.contrib import admin

from .models import TeacherAssignment


# ============================================================
# TEACHER ASSIGNMENT ADMIN
# ============================================================

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "teacher",
        "class_room",
        "subject",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "class_room",
        "subject",
    )

    search_fields = (
        "teacher__username",
        "teacher__first_name",
        "teacher__last_name",
        "teacher__email",
        "class_room__name",
        "subject__name",
        "subject__code",
    )

    ordering = (
        "teacher__username",
        "class_room__name",
        "subject__name",
    )
    