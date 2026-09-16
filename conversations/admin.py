from django.contrib import admin

from .models import (
    Conversation,
    Message,
)


# ============================================================
# MESSAGE INLINE
# ============================================================
#
# Messages waxaa lagu arki karaa gudaha Conversation-ka.
#
# ============================================================


class MessageInline(admin.TabularInline):

    model = Message

    extra = 0

    fields = (
        'sender',
        'body',
        'is_read',
        'read_at',
        'created_at',
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        'created_at',
    )


# ============================================================
# CONVERSATION ADMIN
# ============================================================


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):

    # ========================================================
    # LIST DISPLAY
    # ========================================================

    list_display = (
        'id',
        'user',
        'staff',
        'is_active',
        'created_at',
        'updated_at',
    )

    # ========================================================
    # FILTERS
    # ========================================================

    list_filter = (
        'is_active',
        'created_at',
        'updated_at',
    )

    # ========================================================
    # SEARCH
    # ========================================================

    search_fields = (
        'user__username',
        'user__email',
        'staff__username',
        'staff__email',
    )

    # ========================================================
    # ORDERING
    # ========================================================

    ordering = (
        '-updated_at',
    )

    # ========================================================
    # READ ONLY
    # ========================================================

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # ========================================================
    # INLINE MESSAGES
    # ========================================================

    inlines = [
        MessageInline,
    ]


# ============================================================
# MESSAGE ADMIN
# ============================================================


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    # ========================================================
    # LIST DISPLAY
    # ========================================================

    list_display = (
        'id',
        'conversation',
        'sender',
        'short_body',
        'is_read',
        'read_at',
        'created_at',
    )

    # ========================================================
    # FILTERS
    # ========================================================

    list_filter = (
        'is_read',
        'created_at',
        'read_at',
    )

    # ========================================================
    # SEARCH
    # ========================================================

    search_fields = (
        'body',
        'sender__username',
        'conversation__user__username',
        'conversation__staff__username',
    )

    # ========================================================
    # ORDERING
    # ========================================================

    ordering = (
        '-created_at',
    )

    # ========================================================
    # READ ONLY
    # ========================================================

    readonly_fields = (
        'created_at',
    )

    # ========================================================
    # SHORT MESSAGE
    # ========================================================

    @admin.display(
        description='Message'
    )
    def short_body(self, obj):

        if len(obj.body) > 60:

            return f'{obj.body[:60]}...'

        return obj.body
    