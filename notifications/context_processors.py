# ============================================================
# CONVERSATION CONTEXT PROCESSORS
# ============================================================
#
# File-kan wuxuu variables conversation ah si automatic ah
# ugu diraa dhammaan templates-ka Django.
#
# Tusaale:
#
# {{ conversation_unread_count }}
#
# Waxaa si gaar ah loogu isticmaali doonaa navbar.html.
#
# ============================================================


from django.db.models import Q

from .models import Conversation, Message


# ============================================================
# CONVERSATION NOTIFICATIONS
# ============================================================
#
# Navbar-ka wuxuu u baahan yahay:
#
# conversation_unread_count
#
# Tiradani waa messages-ka aan weli la akhrin ee user-ka
# hadda login-ka ah.
#
# ============================================================


def conversation_notifications(request):

    # ========================================================
    # DEFAULT
    # ========================================================
    #
    # Haddii user-ku uusan login ahayn, unread count = 0.
    #
    # ========================================================

    conversation_unread_count = 0


    # ========================================================
    # AUTHENTICATED USER
    # ========================================================

    if request.user.is_authenticated:

        # ====================================================
        # USER'S CONVERSATIONS
        # ====================================================
        #
        # User:
        #     conversations uu leeyahay
        #
        # Staff:
        #     conversations uu staff ahaan ku leeyahay
        #
        # ====================================================

        try:

            profile = request.user.profile

            is_staff = profile.role in [
                'Admin',
                'Manager',
            ]

        except Exception:

            is_staff = False


        # ====================================================
        # BASE CONVERSATIONS
        # ====================================================

        if is_staff:

            conversations = Conversation.objects.filter(
                staff=request.user
            )

        else:

            conversations = Conversation.objects.filter(
                user=request.user
            )


        # ====================================================
        # UNREAD MESSAGES
        # ====================================================
        #
        # Waxaan tirineynaa:
        #
        # is_read=False
        #
        # AND
        #
        # sender != current user
        #
        # ====================================================

        conversation_unread_count = Message.objects.filter(

            conversation__in=conversations,

            is_read=False,

        ).exclude(

            sender=request.user

        ).count()


    # ========================================================
    # RETURN CONTEXT
    # ========================================================

    return {

        'conversation_unread_count':
            conversation_unread_count,

    }
