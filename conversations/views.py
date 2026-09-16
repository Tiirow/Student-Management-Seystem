# ============================================================
# CONVERSATIONS VIEWS
# ============================================================

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone

from .models import (
    Conversation,
    Message,
)


# ============================================================
# ROLE NAMES USED BY THE SYSTEM
# ============================================================

ADMINISTRATOR_ROLE = "Administrator"
MANAGER_ROLE = "Manager"
TEACHER_ROLE = "Teacher"
STUDENT_ROLE = "Student"


# ============================================================
# GET USER ROLE
# ============================================================

def get_user_role(user):
    """
    Return the user's Profile role.

    Superuser is treated as Administrator.
    """

    if not user or not user.is_authenticated:
        return ""

    # --------------------------------------------------------
    # SUPERUSER
    # --------------------------------------------------------

    if user.is_superuser:
        return ADMINISTRATOR_ROLE

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    try:
        return str(
            user.profile.role or ""
        ).strip()

    except Exception:
        return ""


# ============================================================
# STAFF CHECK
# ============================================================

def is_conversation_staff(user):
    """
    Conversation staff are:

        Administrator
        Manager

    Django superuser is treated as Administrator.
    """

    if not user or not user.is_authenticated:
        return False

    role = get_user_role(user)

    return role in [
        ADMINISTRATOR_ROLE,
        MANAGER_ROLE,
    ]


# ============================================================
# ADMINISTRATOR CHECK
# ============================================================

def is_conversation_administrator(user):
    """
    Administrator-only helper.
    """

    if not user or not user.is_authenticated:
        return False

    return get_user_role(user) == ADMINISTRATOR_ROLE


# ============================================================
# TEACHER CHECK
# ============================================================

def is_conversation_teacher(user):
    """
    Teacher-only helper.
    """

    if not user or not user.is_authenticated:
        return False

    return get_user_role(user) == TEACHER_ROLE


# ============================================================
# STUDENT CHECK
# ============================================================

def is_conversation_student(user):
    """
    Student-only helper.
    """

    if not user or not user.is_authenticated:
        return False

    return get_user_role(user) == STUDENT_ROLE


# ============================================================
# CONVERSATION ACCESS
# ============================================================

def conversation_access(request, conversation):
    """
    Check whether the logged-in user is a participant
    in the selected conversation.

    Conversation model uses:

        user
        staff

    Access is granted ONLY when the current user is
    one of these two participants.

    This prevents Teacher / Student / Manager / Administrator
    from opening another person's conversation by manually
    changing the conversation ID in the URL.
    """

    if not request.user.is_authenticated:
        return False

    # --------------------------------------------------------
    # USER-SIDE PARTICIPANT
    # --------------------------------------------------------

    if conversation.user_id == request.user.id:
        return True

    # --------------------------------------------------------
    # STAFF-SIDE PARTICIPANT
    # --------------------------------------------------------

    if conversation.staff_id == request.user.id:
        return True

    # --------------------------------------------------------
    # NO ACCESS
    # --------------------------------------------------------

    return False


# ============================================================
# CONVERSATION LIST / INBOX
# ============================================================

def conversationList(request):
    """
    Conversation inbox.

    Administrator:
        Sees only conversations in which they participate.

    Manager:
        Sees only conversations in which they participate.

    Teacher:
        Sees only their own conversations.

    Student:
        Sees only their own conversations.

    Other users:
        See only their own conversations.
    """

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    if not request.user.is_authenticated:
        return redirect("users:login")

    # --------------------------------------------------------
    # BASE QUERY
    # --------------------------------------------------------

    if is_conversation_staff(request.user):

        # ----------------------------------------------------
        # ADMINISTRATOR / MANAGER
        # ----------------------------------------------------
        #
        # They can see conversations where they are either:
        #
        #   conversation.staff
        #
        # OR
        #
        #   conversation.user
        #
        # This is important because the Conversation model
        # supports both participant positions.
        #
        # ----------------------------------------------------

        conversations = Conversation.objects.filter(
            Q(staff=request.user)
            |
            Q(user=request.user)
        ).distinct()

    else:

        # ----------------------------------------------------
        # TEACHER / STUDENT / OTHER USER
        # ----------------------------------------------------
        #
        # They can ONLY see conversations belonging to them.
        #
        # They cannot see:
        #
        #   Teacher A's conversations
        #   Student B's conversations
        #   Manager's private conversations
        #   Administrator's other conversations
        #
        # ----------------------------------------------------

        conversations = Conversation.objects.filter(
            user=request.user
        )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    if search_query:

        conversations = conversations.filter(

            Q(user__username__icontains=search_query)
            |
            Q(user__first_name__icontains=search_query)
            |
            Q(user__last_name__icontains=search_query)

            |

            Q(staff__username__icontains=search_query)
            |
            Q(staff__first_name__icontains=search_query)
            |
            Q(staff__last_name__icontains=search_query)

        )

    # --------------------------------------------------------
    # UNREAD COUNT PER CONVERSATION
    # --------------------------------------------------------

    conversations = (
        conversations
        .annotate(
            unread_count=Count(
                "messages",
                filter=(
                    Q(messages__is_read=False)
                    &
                    ~Q(
                        messages__sender=request.user
                    )
                ),
            )
        )
        .select_related(
            "user",
            "staff",
        )
        .order_by(
            "-updated_at"
        )
    )

    # --------------------------------------------------------
    # TOTAL UNREAD
    # --------------------------------------------------------

    unread_count = (
        Message.objects
        .filter(
            conversation__in=conversations,
            is_read=False,
        )
        .exclude(
            sender=request.user
        )
        .count()
    )

    # --------------------------------------------------------
    # CURRENT ROLE
    # --------------------------------------------------------

    current_role = get_user_role(
        request.user
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {
        "conversations": conversations,
        "search_query": search_query,
        "unread_count": unread_count,

        "is_staff": is_conversation_staff(
            request.user
        ),

        "current_role": current_role,
    }

    # --------------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------------

    return render(
        request,
        "conversations/conversation_list.html",
        context,
    )


# ============================================================
# CONVERSATION DETAIL
# ============================================================

def conversationDetail(
    request,
    conversation_id,
):
    """
    Display one conversation and its messages.

    IMPORTANT:
        A user must be one of the conversation participants.
    """

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    if not request.user.is_authenticated:
        return redirect("users:login")

    # --------------------------------------------------------
    # GET CONVERSATION
    # --------------------------------------------------------

    conversation = get_object_or_404(
        Conversation.objects.select_related(
            "user",
            "staff",
        ),
        id=conversation_id,
    )

    # --------------------------------------------------------
    # ACCESS CONTROL
    # --------------------------------------------------------

    if not conversation_access(
        request,
        conversation,
    ):

        return render(
            request,
            "users/access_denied.html",
            status=403,
        )

    # --------------------------------------------------------
    # MARK RECEIVED MESSAGES AS READ
    # --------------------------------------------------------

    unread_messages = (
        conversation.messages
        .filter(
            is_read=False
        )
        .exclude(
            sender=request.user
        )
    )

    unread_messages.update(
        is_read=True,
        read_at=timezone.now(),
    )

    # --------------------------------------------------------
    # GET MESSAGES
    # --------------------------------------------------------

    messages_list = (
        conversation.messages
        .select_related(
            "sender"
        )
        .order_by(
            "created_at"
        )
    )

    # --------------------------------------------------------
    # OTHER USER
    # --------------------------------------------------------

    if conversation.user_id == request.user.id:
        other_user = conversation.staff
    else:
        other_user = conversation.user

    # --------------------------------------------------------
    # CURRENT ROLE
    # --------------------------------------------------------

    current_role = get_user_role(
        request.user
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {
        "conversation": conversation,
        "messages_list": messages_list,
        "other_user": other_user,

        "current_role": current_role,

        "is_staff": is_conversation_staff(
            request.user
        ),
    }

    # --------------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------------

    return render(
        request,
        "conversations/conversation_detail.html",
        context,
    )


# ============================================================
# START CONVERSATION
# ============================================================

def startConversation(request):
    """
    Start a new conversation.

    PERMISSION RULES
    ----------------

    Administrator:
        Can start a conversation with ANY active user.

    Manager:
        Can start a conversation with ANY active user.

    Teacher:
        Can start a conversation with Administrator ONLY.

    Student:
        Can start a conversation with Administrator ONLY.

    Other users:
        Can start a conversation with Administrator ONLY.

    Backend security is enforced even if somebody manually
    modifies the recipient_id in the POST request.
    """

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    if not request.user.is_authenticated:
        return redirect("users:login")

    # ========================================================
    # CURRENT USER ROLE
    # ========================================================

    current_role = get_user_role(
        request.user
    )

    current_user_is_staff = (
        current_role in [
            ADMINISTRATOR_ROLE,
            MANAGER_ROLE,
        ]
    )

    # ========================================================
    # RECIPIENTS
    # ========================================================

    if current_user_is_staff:

        # ----------------------------------------------------
        # ADMINISTRATOR / MANAGER
        # ----------------------------------------------------
        #
        # Can start with any active user.
        #
        # Current user is excluded.
        #
        # ----------------------------------------------------

        recipients = (
            User.objects
            .filter(
                is_active=True
            )
            .exclude(
                id=request.user.id
            )
            .select_related(
                "profile"
            )
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        recipient_label = "Select User"

        recipient_help = (
            "You can start a conversation with any active "
            "user in the system."
        )

    else:

        # ----------------------------------------------------
        # TEACHER / STUDENT / OTHER USER
        # ----------------------------------------------------
        #
        # Administrator ONLY.
        #
        # ----------------------------------------------------

        recipients = (
            User.objects
            .filter(
                is_active=True,
                profile__role=ADMINISTRATOR_ROLE,
            )
            .exclude(
                id=request.user.id
            )
            .select_related(
                "profile"
            )
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        recipient_label = "Select Administrator"

        recipient_help = (
            "For support or complaints, choose an Administrator."
        )

    # ========================================================
    # POST REQUEST
    # ========================================================

    if request.method == "POST":

        # ----------------------------------------------------
        # RECIPIENT ID
        # ----------------------------------------------------

        recipient_id = (
            request.POST.get(
                "recipient_id",
                "",
            ).strip()
        )

        # ----------------------------------------------------
        # MESSAGE BODY
        # ----------------------------------------------------

        body = (
            request.POST.get(
                "body",
                "",
            ).strip()
        )

        # ----------------------------------------------------
        # VALIDATE RECIPIENT ID
        # ----------------------------------------------------

        if not recipient_id:

            messages.error(
                request,
                "Fadlan dooro qofka aad rabto inaad la hadasho.",
            )

            return render(
                request,
                "conversations/start_conversation.html",
                {
                    "users": recipients,
                    "is_staff": current_user_is_staff,
                    "current_role": current_role,
                    "recipient_label": recipient_label,
                    "recipient_help": recipient_help,
                },
            )

        # ====================================================
        # BACKEND RECIPIENT SECURITY
        # ====================================================

        if current_user_is_staff:

            # ------------------------------------------------
            # ADMINISTRATOR / MANAGER
            # ------------------------------------------------
            #
            # Any active user except current user.
            #
            # ------------------------------------------------

            target_user = get_object_or_404(
                User,
                id=recipient_id,
                is_active=True,
            )

        else:

            # ------------------------------------------------
            # TEACHER / STUDENT / OTHER USER
            # ------------------------------------------------
            #
            # Administrator ONLY.
            #
            # This prevents somebody from manually posting
            # another user's ID.
            #
            # ------------------------------------------------

            target_user = get_object_or_404(
                User,
                id=recipient_id,
                is_active=True,
                profile__role=ADMINISTRATOR_ROLE,
            )

        # ====================================================
        # PREVENT SELF CONVERSATION
        # ====================================================

        if target_user.id == request.user.id:

            messages.error(
                request,
                "Naftaada conversation lama bilaabi kartid.",
            )

            return render(
                request,
                "conversations/start_conversation.html",
                {
                    "users": recipients,
                    "is_staff": current_user_is_staff,
                    "current_role": current_role,
                    "recipient_label": recipient_label,
                    "recipient_help": recipient_help,
                },
            )

        # ====================================================
        # VALIDATE MESSAGE
        # ====================================================

        if not body:

            messages.error(
                request,
                "Fadlan geli fariinta.",
            )

            return render(
                request,
                "conversations/start_conversation.html",
                {
                    "users": recipients,
                    "is_staff": current_user_is_staff,
                    "current_role": current_role,
                    "recipient_label": recipient_label,
                    "recipient_help": recipient_help,
                },
            )

        # ====================================================
        # DETERMINE CONVERSATION PARTICIPANTS
        # ====================================================
        #
        # Conversation model:
        #
        #     user
        #     staff
        #
        # Normal user -> Administrator:
        #
        #     user  = current user
        #     staff = Administrator
        #
        # Administrator/Manager -> anyone:
        #
        #     user  = target user
        #     staff = current user
        #
        # ====================================================

        if current_user_is_staff:

            conversation_user = target_user
            conversation_staff = request.user

        else:

            conversation_user = request.user
            conversation_staff = target_user

        # ====================================================
        # GET OR CREATE CONVERSATION
        # ====================================================

        conversation, created = (
            Conversation.objects.get_or_create(
                user=conversation_user,
                staff=conversation_staff,
                defaults={
                    "is_active": True,
                },
            )
        )

        # ====================================================
        # REOPEN CLOSED CONVERSATION
        # ====================================================

        if not conversation.is_active:

            conversation.is_active = True

            conversation.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ]
            )

        # ====================================================
        # CREATE MESSAGE
        # ====================================================

        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=body,
        )

        # ====================================================
        # UPDATE CONVERSATION
        # ====================================================

        conversation.updated_at = timezone.now()

        conversation.save(
            update_fields=[
                "updated_at",
            ]
        )

        # ====================================================
        # REDIRECT
        # ====================================================

        return redirect(
            "conversations:conversation-detail",
            conversation_id=conversation.id,
        )

    # ========================================================
    # GET REQUEST
    # ========================================================

    context = {
        "users": recipients,
        "is_staff": current_user_is_staff,
        "current_role": current_role,
        "recipient_label": recipient_label,
        "recipient_help": recipient_help,
    }

    # ========================================================
    # TEMPLATE
    # ========================================================

    return render(
        request,
        "conversations/start_conversation.html",
        context,
    )


# ============================================================
# SEND MESSAGE / REPLY
# ============================================================

def sendMessage(
    request,
    conversation_id,
):
    """
    Send a reply inside an existing conversation.

    Both participants can reply.

    A user who is not a participant cannot send a message,
    even if they manually change the conversation ID.
    """

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    if not request.user.is_authenticated:
        return redirect("users:login")

    # ========================================================
    # ONLY POST
    # ========================================================

    if request.method != "POST":

        return redirect(
            "conversations:conversation-detail",
            conversation_id=conversation_id,
        )

    # ========================================================
    # GET CONVERSATION
    # ========================================================

    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
    )

    # ========================================================
    # ACCESS CONTROL
    # ========================================================

    if not conversation_access(
        request,
        conversation,
    ):

        return render(
            request,
            "users/access_denied.html",
            status=403,
        )

    # ========================================================
    # ACTIVE CHECK
    # ========================================================

    if not conversation.is_active:

        messages.error(
            request,
            "Conversation-kan waa xiran yahay.",
        )

        return redirect(
            "conversations:conversation-detail",
            conversation_id=conversation.id,
        )

    # ========================================================
    # MESSAGE BODY
    # ========================================================

    body = (
        request.POST.get(
            "body",
            "",
        ).strip()
    )

    # ========================================================
    # EMPTY MESSAGE
    # ========================================================

    if not body:

        messages.error(
            request,
            "Fadlan geli fariin.",
        )

        return redirect(
            "conversations:conversation-detail",
            conversation_id=conversation.id,
        )

    # ========================================================
    # CREATE MESSAGE
    # ========================================================

    Message.objects.create(
        conversation=conversation,
        sender=request.user,
        body=body,
    )

    # ========================================================
    # UPDATE CONVERSATION
    # ========================================================

    conversation.updated_at = timezone.now()

    conversation.save(
        update_fields=[
            "updated_at",
        ]
    )

    # ========================================================
    # REDIRECT
    # ========================================================

    return redirect(
        "conversations:conversation-detail",
        conversation_id=conversation.id,
    )
