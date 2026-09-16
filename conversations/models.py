from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# ============================================================
# CONVERSATION
# ============================================================
#
# Conversation waa hal wada sheekeysi oo u dhexeeya:
#
# User
#    +
# Admin / Manager
#
# Tusaale:
#
# Conversation #1
#
# Mohamed
#    ↕
# Manager
#
# Messages:
#
# Manager:
# Hello Mohamed, please update your project.
#
# Mohamed:
# Okay, I will do it.
#
# Manager:
# Thank you.
#
# Mohamed:
# Done.
#
# Dhammaan messages-kan waxay ku jiraan
# hal Conversation.
#
# ============================================================


class Conversation(models.Model):

    # ========================================================
    # USER
    # ========================================================
    #
    # User-ka conversation-ka leh.
    #
    # Tusaale:
    #
    # Mohamed
    #
    # ========================================================

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_conversations'
    )

    # ========================================================
    # STAFF
    # ========================================================
    #
    # Admin ama Manager-ka conversation-ka la leh user-ka.
    #
    # Staff halkan waxaan uga jeednaa User model-ka Django,
    # laakiin role-kiisa Profile ayaa go'aaminaya inuu yahay:
    #
    # Admin
    # ama
    # Manager
    #
    # ========================================================

    staff = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='staff_conversations'
    )

    # ========================================================
    # CREATED
    # ========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # ========================================================
    # UPDATED
    # ========================================================
    #
    # Waqtiga ugu dambeeyay ee conversation-ka la update gareeyay.
    #
    # Message cusub marka la diro,
    # field-kan waa la update gareyn doonaa.
    #
    # ========================================================

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ========================================================
    # ACTIVE
    # ========================================================
    #
    # Conversation-ka haddii la xiro:
    #
    # is_active = False
    #
    # Looma delete-gareynayo database-ka.
    #
    # ========================================================

    is_active = models.BooleanField(
        default=True
    )

    # ========================================================
    # STRING
    # ========================================================

    def __str__(self):

        return (
            f"Conversation: "
            f"{self.user.username} ↔ "
            f"{self.staff.username}"
        )

    # ========================================================
    # VALIDATION
    # ========================================================
    #
    # User iyo Staff isku qof ma noqon karaan.
    #
    # ========================================================

    def clean(self):

        if self.user_id == self.staff_id:

            raise ValidationError(
                "User iyo Staff isku qof ma noqon karaan."
            )

    # ========================================================
    # META
    # ========================================================

    class Meta:

        ordering = [
            '-updated_at'
        ]

        verbose_name = 'Conversation'

        verbose_name_plural = 'Conversations'


# ============================================================
# MESSAGE
# ============================================================
#
# Message kasta wuxuu ka tirsan yahay Conversation.
#
# Example:
#
# Conversation
#       │
#       ├── Message 1
#       ├── Message 2
#       ├── Message 3
#       └── Message 4
#
# ============================================================


class Message(models.Model):

    # ========================================================
    # CONVERSATION
    # ========================================================
    #
    # Message-kan conversation-kee ayuu ka tirsan yahay?
    #
    # ========================================================

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    # ========================================================
    # SENDER
    # ========================================================
    #
    # Qofka fariinta diray.
    #
    # Waxay noqon kartaa:
    #
    # User
    # Admin
    # Manager
    #
    # ========================================================

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    # ========================================================
    # MESSAGE BODY
    # ========================================================

    body = models.TextField()

    # ========================================================
    # READ STATUS
    # ========================================================
    #
    # False:
    # Message-ka wali lama akhrin.
    #
    # True:
    # Message-ka waa la akhriyey.
    #
    # ========================================================

    is_read = models.BooleanField(
        default=False
    )

    # ========================================================
    # READ TIME
    # ========================================================
    #
    # Waqtiga message-ka la akhriyey.
    #
    # Haddii uusan wali akhrin:
    #
    # read_at = NULL
    #
    # ========================================================

    read_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # ========================================================
    # CREATED
    # ========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # ========================================================
    # STRING
    # ========================================================

    def __str__(self):

        return (
            f"{self.sender.username}: "
            f"{self.body[:50]}"
        )

    # ========================================================
    # META
    # ========================================================

    class Meta:

        ordering = [
            'created_at'
        ]

        verbose_name = 'Message'

        verbose_name_plural = 'Messages'
        