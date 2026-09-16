from django.urls import path
from . import views


app_name = "conversations"


urlpatterns = [

    # ============================================================
    # CONVERSATION LIST
    # /conversations/
    # ============================================================
    path(
        "",
        views.conversationList,
        name="conversation-list",
    ),

    # ============================================================
    # START NEW CONVERSATION
    # /conversations/new/
    # ============================================================
    path(
        "new/",
        views.startConversation,
        name="start-conversation",
    ),

    # ============================================================
    # CONVERSATION DETAIL
    # /conversations/<conversation_id>/
    # ============================================================
    path(
        "<int:conversation_id>/",
        views.conversationDetail,
        name="conversation-detail",
    ),

    # ============================================================
    # SEND MESSAGE
    # /conversations/<conversation_id>/send/
    # ============================================================
    path(
        "<int:conversation_id>/send/",
        views.sendMessage,
        name="send-message",
    ),
]
