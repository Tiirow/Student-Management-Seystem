# ============================================================
# NOTIFICATIONS APP URLS
# ============================================================

from django.urls import path

from . import views


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # ========================================================
    # NOTIFICATIONS LIST / DASHBOARD
    # URL: /notifications/
    # ========================================================

    path(
        "",
        views.notifications,
        name="notifications",
    ),

    # ========================================================
    # MARK NOTIFICATION AS READ
    # URL: /notifications/read/<id>/
    # ========================================================

    path(
        "read/<int:pk>/",
        views.mark_notification_as_read,
        name="mark_notification_as_read",
    ),
]

