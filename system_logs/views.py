# ============================================================
# SYSTEM LOGS VIEWS
# ============================================================

from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from .models import AuditLog, ErrorLog

from users.models import LoginAttempt


# ============================================================
# HELPER
# ============================================================

def logs_access_allowed(user):
    """
    Kaliya Administrator iyo Manager ayaa geli kara:

        - Audit Trail
        - Error Logs
        - Login Attempts

    Django Superuser waxaa loo aqoonsanayaa Administrator.
    """

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    if not user.is_authenticated:
        return False

    # --------------------------------------------------------
    # SUPERUSER
    # --------------------------------------------------------

    if user.is_superuser:
        return True

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    try:

        role = str(
            user.profile.role or ""
        ).strip()

    except Exception:

        return False

    # --------------------------------------------------------
    # ALLOWED ROLES
    # --------------------------------------------------------

    return role in [
        "Administrator",
        "Manager",
    ]


# ============================================================
# ACCESS DENIED
# ============================================================

def logs_access_denied(request):

    return render(
        request,
        "users/access_denied.html",
        status=403,
    )


# ============================================================
# SYSTEM LOGS DASHBOARD
# ============================================================

@login_required(login_url="users:login")
def system_logs_dashboard(request):
    """
    Main System Logs Dashboard.

    Shows:

        Audit Trail
        Error Logs
        Login Attempts

    Access:

        Administrator
        Manager
    """

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not logs_access_allowed(
        request.user
    ):

        return logs_access_denied(
            request
        )

    # ========================================================
    # AUDIT LOGS
    # ========================================================

    audit_logs = (
        AuditLog.objects
        .select_related("user")
        .all()
    )

    # --------------------------------------------------------
    # AUDIT SEARCH
    # --------------------------------------------------------

    audit_search = (
        request.GET.get(
            "audit_search",
            "",
        ).strip()
    )

    if audit_search:

        audit_logs = audit_logs.filter(
            description__icontains=audit_search
        )

    # --------------------------------------------------------
    # AUDIT ACTION FILTER
    # --------------------------------------------------------

    audit_action = (
        request.GET.get(
            "audit_action",
            "",
        ).strip()
    )

    if audit_action:

        audit_logs = audit_logs.filter(
            action=audit_action
        )

    # --------------------------------------------------------
    # AUDIT STATISTICS
    # --------------------------------------------------------

    total_logs = (
        AuditLog.objects.count()
    )

    create_logs = (
        AuditLog.objects
        .filter(
            action="create"
        )
        .count()
    )

    update_logs = (
        AuditLog.objects
        .filter(
            action="update"
        )
        .count()
    )

    delete_logs = (
        AuditLog.objects
        .filter(
            action="delete"
        )
        .count()
    )

    # --------------------------------------------------------
    # LOGIN ATTEMPT STATISTICS
    # --------------------------------------------------------

    login_attempt_logs = (
        AuditLog.objects
        .filter(
            action="login_attempt"
        )
        .count()
    )

    # --------------------------------------------------------
    # LOGIN SUCCESS STATISTICS
    # --------------------------------------------------------

    login_success_logs = (
        AuditLog.objects
        .filter(
            action="login_success"
        )
        .count()
    )

    # ========================================================
    # ERROR LOGS
    # ========================================================

    error_logs = (
        ErrorLog.objects
        .select_related("user")
        .all()
    )

    # --------------------------------------------------------
    # ERROR SEARCH
    # --------------------------------------------------------

    error_search = (
        request.GET.get(
            "error_search",
            "",
        ).strip()
    )

    if error_search:

        error_logs = error_logs.filter(
            message__icontains=error_search
        )

    # --------------------------------------------------------
    # ERROR STATISTICS
    # --------------------------------------------------------

    total_errors = (
        ErrorLog.objects.count()
    )

    # ========================================================
    # LOGIN ATTEMPTS - LEGACY MODEL
    # ========================================================

    login_attempts = (
        LoginAttempt.objects.count()
    )

    # ========================================================
    # CURRENT ROLE
    # ========================================================

    if request.user.is_superuser:

        current_role = "Administrator"

    else:

        try:

            current_role = (
                request.user.profile.role
            )

        except Exception:

            current_role = "User"

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        # ----------------------------------------------------
        # CURRENT USER
        # ----------------------------------------------------

        "current_role": current_role,

        # ----------------------------------------------------
        # AUDIT TRAIL
        # ----------------------------------------------------

        "audit_logs": audit_logs,

        "total_logs": total_logs,

        "create_logs": create_logs,

        "update_logs": update_logs,

        "delete_logs": delete_logs,

        "login_attempt_logs": (
            login_attempt_logs
        ),

        "login_success_logs": (
            login_success_logs
        ),

        "audit_search": audit_search,

        "selected_action": audit_action,

        # ----------------------------------------------------
        # ERROR LOGS
        # ----------------------------------------------------

        "error_logs": error_logs,

        "total_errors": total_errors,

        "error_search": error_search,

        # ----------------------------------------------------
        # LOGIN ATTEMPTS
        # ----------------------------------------------------

        "login_attempts": login_attempts,
    }

    # ========================================================
    # TEMPLATE
    # ========================================================

    return render(
        request,
        "system_logs/logs_dashboard.html",
        context,
    )


# ============================================================
# AUDIT TRAIL
# ============================================================

def audit_trail(request):
    """
    Legacy Audit Trail page.

    Access:
        Administrator
        Manager
    """

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if not request.user.is_authenticated:

        return redirect(
            "users:login"
        )

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not logs_access_allowed(
        request.user
    ):

        return logs_access_denied(
            request
        )

    # --------------------------------------------------------
    # ALL AUDIT LOGS
    # --------------------------------------------------------

    audit_logs = (
        AuditLog.objects
        .select_related("user")
        .all()
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search = (
        request.GET.get(
            "search",
            "",
        ).strip()
    )

    if search:

        audit_logs = audit_logs.filter(
            description__icontains=search
        )

    # --------------------------------------------------------
    # ACTION FILTER
    # --------------------------------------------------------

    action = (
        request.GET.get(
            "action",
            "",
        ).strip()
    )

    if action:

        audit_logs = audit_logs.filter(
            action=action
        )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    total_logs = (
        AuditLog.objects.count()
    )

    create_logs = (
        AuditLog.objects
        .filter(
            action="create"
        )
        .count()
    )

    update_logs = (
        AuditLog.objects
        .filter(
            action="update"
        )
        .count()
    )

    delete_logs = (
        AuditLog.objects
        .filter(
            action="delete"
        )
        .count()
    )

    login_attempt_logs = (
        AuditLog.objects
        .filter(
            action="login_attempt"
        )
        .count()
    )

    login_success_logs = (
        AuditLog.objects
        .filter(
            action="login_success"
        )
        .count()
    )

    # --------------------------------------------------------
    # CURRENT ROLE
    # --------------------------------------------------------

    if request.user.is_superuser:

        current_role = "Administrator"

    else:

        try:

            current_role = (
                request.user.profile.role
            )

        except Exception:

            current_role = "User"

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        "current_role": current_role,

        "audit_logs": audit_logs,

        "total_logs": total_logs,

        "create_logs": create_logs,

        "update_logs": update_logs,

        "delete_logs": delete_logs,

        "login_attempt_logs": (
            login_attempt_logs
        ),

        "login_success_logs": (
            login_success_logs
        ),

        "search": search,

        "selected_action": action,
    }

    # --------------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------------

    return render(
        request,
        "system_logs/audit_trail.html",
        context,
    )


# ============================================================
# ERROR LOGS
# ============================================================

def error_logs(request):
    """
    Legacy Error Logs page.

    Access:
        Administrator
        Manager
    """

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if not request.user.is_authenticated:

        return redirect(
            "users:login"
        )

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not logs_access_allowed(
        request.user
    ):

        return logs_access_denied(
            request
        )

    # --------------------------------------------------------
    # ALL ERROR LOGS
    # --------------------------------------------------------

    logs = (
        ErrorLog.objects
        .select_related("user")
        .all()
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search = (
        request.GET.get(
            "search",
            "",
        ).strip()
    )

    if search:

        logs = logs.filter(
            message__icontains=search
        )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    total_errors = (
        ErrorLog.objects.count()
    )

    # --------------------------------------------------------
    # CURRENT ROLE
    # --------------------------------------------------------

    if request.user.is_superuser:

        current_role = "Administrator"

    else:

        try:

            current_role = (
                request.user.profile.role
            )

        except Exception:

            current_role = "User"

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        "current_role": current_role,

        "error_logs": logs,

        "total_errors": total_errors,

        "search": search,
    }

    # --------------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------------

    return render(
        request,
        "system_logs/error_logs.html",
        context,
    )

