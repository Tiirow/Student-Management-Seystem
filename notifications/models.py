from django.db import models
from django.contrib.auth.models import User

from project_app.models import Project


class Notification(models.Model):

    # ============================================================
    # NOTIFICATION TYPES
    # ============================================================

    NOTIFICATION_TYPES = (
        ('project_created', 'Project Created'),
        ('project_updated', 'Project Updated'),
        ('project_deleted', 'Project Deleted'),
        ('permission_changed', 'Permission Changed'),
        ('user_registered', 'User Registered'),
        ('general', 'General'),
    )

    # ============================================================
    # RECIPIENT
    # ============================================================
    #
    # Notification-ka waxaa loo dirayaa user-kan.
    #
    # ============================================================

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    # ============================================================
    # MESSAGE
    # ============================================================

    message = models.TextField()

    # ============================================================
    # NOTIFICATION TYPE
    # ============================================================

    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        default='general'
    )

    # ============================================================
    # RELATED PROJECT
    # ============================================================
    #
    # Haddii notification-ku project la xiriirto,
    # project-ka halkan ayaan ku kaydinaynaa.
    #
    # null=True:
    # Notification-ka wuxuu jiri karaa project la'aan.
    #
    # ============================================================

    related_project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )

    # ============================================================
    # READ STATUS
    # ============================================================

    is_read = models.BooleanField(
        default=False
    )

    # ============================================================
    # CREATED
    # ============================================================

    created = models.DateTimeField(
        auto_now_add=True
    )

    # ============================================================
    # STRING
    # ============================================================

    def __str__(self):

        return (
            f"{self.recipient.username} - "
            f"{self.message}"
        )

    # ============================================================
    # META
    # ============================================================

    class Meta:

        ordering = ['-created']

        verbose_name = 'Notification'

        verbose_name_plural = 'Notifications'