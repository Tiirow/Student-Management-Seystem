# ============================================================
# CONVERSATIONS CONTEXT PROCESSOR
# ============================================================

from django.db.models import Q

from .models import Message


# ============================================================
# CONVERSATION NOTIFICATIONS
# ============================================================
#
# Waxaa global ahaan loogu diri doonaa templates-ka:
#
# {{ conversation_unread_count }}
#
# Navbar-ka ayaa isticmaali doona si uu u muujiyo
# unread messages.
#
# ============================================================


def conversation_notifications(request):

    # ========================================================
    # DEFAULT
    # ========================================================

    context = {
        'conversation_unread_count': 0,
    }

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    if not request.user.is_authenticated:
        return context

    # ========================================================
    # UNREAD MESSAGES
    # ========================================================
    #
    # Message:
    #
    # 1. Aan weli la akhrin
    # 2. Qofka hadda login-ka ah uusan dirin
    #
    # ========================================================

    unread_count = Message.objects.filter(
        conversation__user=request.user,
        is_read=False,
    ).exclude(
        sender=request.user
    ).count()

    # ========================================================
    # STAFF UNREAD
    # ========================================================
    #
    # Admin / Manager wuxuu leeyahay conversations
    # uu staff ahaan u yahay.
    #
    # ========================================================

    try:

        profile = request.user.profile

        if profile.role in [
            'Admin',
            'Manager',
        ]:

            staff_unread_count = Message.objects.filter(
                conversation__staff=request.user,
                is_read=False,
            ).exclude(
                sender=request.user
            ).count()

            unread_count = staff_unread_count

    except Exception:

        pass

    # ========================================================
    # RETURN
    # ========================================================

    context[
        'conversation_unread_count'
    ] = unread_count

    return context
