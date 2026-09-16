from django.contrib import admin
from .models import Profile, LoginAttempt


# ============================================================
# PROFILE ADMIN
# ============================================================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'role',
        'can_view_students',
        'can_add_students',
        'can_edit_students',
        'can_delete_students',
        'can_manage_subjects',
        'can_manage_enrollment',
        'can_manage_attendance',
        'can_manage_grades',
        'can_manage_users',
        'can_view_reports',
    )

    list_filter = (
        'role',
    )

    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
    )

    ordering = (
        'user__username',
    )


# ============================================================
# LOGIN ATTEMPT ADMIN
# ============================================================

@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):

    list_display = (
        'username',
        'ip_address',
        'created',
    )

    search_fields = (
        'username',
        'ip_address',
    )

    ordering = (
        '-created',
    )

    readonly_fields = (
        'username',
        'ip_address',
        'created',
    )
    