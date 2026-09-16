# ============================================================
# SUBJECTS MODELS
# ============================================================
#
# Student Management System
#
# This model manages subjects/courses offered by the school.
#
# ============================================================

from django.db import models


# ============================================================
# SUBJECT MODEL
# ============================================================

class Subject(models.Model):

    # ========================================================
    # SUBJECT CODE
    # ========================================================

    code = models.CharField(
        max_length=20,
        unique=True
    )

    # ========================================================
    # SUBJECT NAME
    # ========================================================

    name = models.CharField(
        max_length=100
    )

    # ========================================================
    # DESCRIPTION
    # ========================================================

    description = models.TextField(
        blank=True
    )

    # ========================================================
    # CREDIT HOURS
    # ========================================================

    credit_hours = models.PositiveIntegerField(
        default=3
    )

    # ========================================================
    # STATUS
    # ========================================================

    STATUS_CHOICES = (
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Active"
    )

    # ========================================================
    # CREATED AT
    # ========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # ========================================================
    # UPDATED AT
    # ========================================================

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __str__(self):
        return f"{self.code} - {self.name}"

    # ========================================================
    # META
    # ========================================================

    class Meta:

        ordering = [
            "name"
        ]

        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        