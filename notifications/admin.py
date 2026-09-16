from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        'recipient',
        'notification_type',
        'message',
        'is_read',
        'created',
    )

    list_filter = (
        'notification_type',
        'is_read',
        'created',
    )

    search_fields = (
        'recipient__username',
        'message',
    )

    ordering = (
        '-created',
    )
    #Tani waxay kuu oggolaaneysaa Django Admin inaad 
    # si professional ah u aragto notifications-ka.


        # Notification
    #────────────────────────────────────
 #Recipient          Mohamed
 #Message            New project created
 #Type               Project Created
 #Related Project    DevSearch
 #Read               ❌ False
 #Created            2026-08-16 08:...

 #Marka user-ku notification-ka akhriyo:
 #Read = ✅ True