# ============================================================
# NOTIFICATIONS VIEWS
# ============================================================
#
# Student Management System
#
# Features:
#   - Notification list
#   - Unread notification count
#   - Mark notification as read
#   - Mark all notifications as read
#
# Security:
#   - Login required
#   - Users can ONLY access their own notifications
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .models import Notification


# ============================================================
# NOTIFICATIONS LIST
# ============================================================
#
# URL:
#     /notifications/
#
# Displays notifications belonging ONLY to the
# currently authenticated user.
#
# ============================================================

@login_required(login_url="login")
def notifications(request):

    user_notifications = (
        Notification.objects
        .filter(
            recipient=request.user
        )
        .order_by("-created")
    )

    unread_count = (
        Notification.objects
        .filter(
            recipient=request.user,
            is_read=False,
        )
        .count()
    )

    context = {
        "notifications": user_notifications,
        "unread_count": unread_count,
    }

    return render(
        request,
        "notifications/notifications.html",
        context,
    )


# ============================================================
# MARK ONE NOTIFICATION AS READ
# ============================================================
#
# URL:
#     /notifications/read/<id>/
#
# SECURITY:
#
# The notification MUST belong to request.user.
#
# Example:
#
# Mohamed -> can mark Mohamed's notification as read.
# Mohamed -> CANNOT mark Ahmed's notification as read.
#
# ============================================================

@login_required(login_url="login")
def mark_notification_as_read(request, pk):

    notification = get_object_or_404(
        Notification,
        id=pk,
        recipient=request.user,
    )

    if not notification.is_read:

        notification.is_read = True

        notification.save(
            update_fields=["is_read"]
        )

    return redirect(
        "notifications"
    )


# ============================================================
# MARK ALL NOTIFICATIONS AS READ
# ============================================================
#
# URL:
#     /notifications/read-all/
#
# Marks ONLY the current user's unread notifications
# as read.
#
# ============================================================

@login_required(login_url="login")
def mark_all_notifications_as_read(request):

    Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).update(
        is_read=True
    )

    return redirect(
        "notifications"
    )

