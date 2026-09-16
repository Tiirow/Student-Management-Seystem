from .models import AuditLog


# ============================================================
# GET CLIENT IP
# ============================================================

def get_client_ip(request):

    """
    Soo qaado IP-ga user-ka.
    """

    if not request:
        return None

    forwarded_for = request.META.get(
        'HTTP_X_FORWARDED_FOR'
    )

    if forwarded_for:

        return forwarded_for.split(',')[0].strip()

    return request.META.get(
        'REMOTE_ADDR'
    )


# ============================================================
# CREATE AUDIT LOG
# ============================================================

def create_audit_log(
    request,
    action,
    description,
    target_type=None,
    target_id=None
):

    """
    Samee Audit Log cusub.

    Tusaale:

    create_audit_log(
        request,
        'create',
        'Created project E-Commerce',
        'Project',
        project.id
    )
    """

    user = None

    if request and request.user.is_authenticated:

        user = request.user

    return AuditLog.objects.create(

        user=user,

        action=action,

        description=description,

        target_type=target_type,

        target_id=str(target_id)
        if target_id is not None
        else None,

        ip_address=get_client_ip(request),

    )

