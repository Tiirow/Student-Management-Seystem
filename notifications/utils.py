from django.contrib.auth.models import User

from .models import Notification


def create_notification(
    recipient,
    message,
    notification_type='general',
    related_project=None
):
    """
    Samee notification cusub.

    recipient:
        User-ka notification-ka loo dirayo.

    message:
        Fariinta notification-ka.

    notification_type:
        Nooca notification-ka.

    related_project:
        Project-ka notification-ku la xiriirayo.
    """

    return Notification.objects.create(
        recipient=recipient,
        message=message,
        notification_type=notification_type,
        related_project=related_project,
    )


def notify_all_users(
    message,
    notification_type='general',
    related_project=None,
    exclude_user=None
    # Waxaan exclude_user u sameynay si, tusaale ahaan, Mohamed project sameeyo, 
    #uusan isaga notification-kaas isaga laftiisa loogu soo celin haddii aanan rabin.
):
    """
    Notification u dir dhammaan users-ka.

    exclude_user:
        Haddii user-ka sameeyay action-ka aan rabno
        inaan notification loo dirin.
    """

    users = User.objects.filter(
        is_active=True
    )

    if exclude_user:
        users = users.exclude(
            id=exclude_user.id
        )

    notifications = []

    for user in users:

        notifications.append(
            Notification(
                recipient=user,
                message=message,
                notification_type=notification_type,
                related_project=related_project,
            )
        )

    Notification.objects.bulk_create(
        notifications
    )
