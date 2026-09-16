from django.db import models
from django.contrib.auth.models import User


# ============================================================
# AUDIT LOG
# ============================================================
#
# Diiwaangeliya actions-ka users-ku sameeyaan.
#
# Tusaale:
#
# Mohamed CREATE Project
# Ahmed UPDATE Project
# Mohamed DELETE Project
# User FAILED LOGIN
# Mohamed LOGIN SUCCESSFULLY
#
# ============================================================

class AuditLog(models.Model):

    # --------------------------------------------------------
    # ACTION TYPES
    # --------------------------------------------------------

    ACTION_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),

        # Login khaldan
        ('login_attempt', 'Login Attempt'),

        # Login sax ah
        ('login_success', 'Login Successfully'),

        ('logout', 'Logout'),
        ('permission_change', 'Permission Change'),
        ('other', 'Other'),
    )

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------
    #
    # Login Attempt-ka khaldan user-ku mararka qaar lama heli karo,
    # sidaas darteed null=True ayaa muhiim ah.
    #
    # --------------------------------------------------------

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    # --------------------------------------------------------
    # ACTION
    # --------------------------------------------------------

    action = models.CharField(
        max_length=50,
        choices=ACTION_TYPES
    )

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description = models.TextField()

    # --------------------------------------------------------
    # TARGET TYPE
    # --------------------------------------------------------
    #
    # Tusaale:
    #
    # Project
    # User
    # Permission
    # Authentication
    #
    # --------------------------------------------------------

    target_type = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # TARGET ID
    # --------------------------------------------------------
    #
    # ID-ga object-ka la saameeyay.
    #
    # --------------------------------------------------------

    target_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # IP ADDRESS
    # --------------------------------------------------------

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # CREATED
    # --------------------------------------------------------

    created = models.DateTimeField(
        auto_now_add=True
    )

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    def __str__(self):

        username = (
            self.user.username
            if self.user
            else 'Unknown User'
        )

        return (
            f"{username} - "
            f"{self.action} - "
            f"{self.description}"
        )

    # --------------------------------------------------------
    # META
    # --------------------------------------------------------

    class Meta:

        ordering = ['-created']

        verbose_name = 'Audit Log'

        verbose_name_plural = 'Audit Logs'


# ============================================================
# ERROR LOG
# ============================================================
#
# System errors-ka database-ka lagu kaydinayo.
#
# ============================================================

class ErrorLog(models.Model):

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='error_logs'
    )

    # --------------------------------------------------------
    # ERROR TYPE
    # --------------------------------------------------------

    error_type = models.CharField(
        max_length=255
    )

    # --------------------------------------------------------
    # ERROR MESSAGE
    # --------------------------------------------------------

    message = models.TextField()

    # --------------------------------------------------------
    # TRACEBACK
    # --------------------------------------------------------
    #
    # Full technical error details.
    #
    # --------------------------------------------------------

    traceback = models.TextField(
        blank=True
    )

    # --------------------------------------------------------
    # REQUEST PATH
    # --------------------------------------------------------

    path = models.CharField(
        max_length=500,
        blank=True
    )

    # --------------------------------------------------------
    # REQUEST METHOD
    # --------------------------------------------------------

    method = models.CharField(
        max_length=20,
        blank=True
    )

    # --------------------------------------------------------
    # IP ADDRESS
    # --------------------------------------------------------

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # CREATED
    # --------------------------------------------------------

    created = models.DateTimeField(
        auto_now_add=True
    )

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    def __str__(self):

        return (
            f"{self.error_type} - "
            f"{self.message[:50]}"
        )

    # --------------------------------------------------------
    # META
    # --------------------------------------------------------

    class Meta:

        ordering = ['-created']

        verbose_name = 'Error Log'

        verbose_name_plural = 'Error Logs'