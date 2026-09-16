# ============================================================
# TEACHER MODELS
# ============================================================
#
# Student Management System
#
# Teacher Architecture:
#
# Django User
#      ↓
# users.Profile
#      ↓
# role = "Teacher"
#      ↓
# TeacherAssignment
#      ├── ClassRoom
#      └── Subject
#
# IMPORTANT:
# We do NOT create a separate Teacher User model.
# Existing Django User + users.Profile is used.
#
# ============================================================


from django.db import models
from django.contrib.auth.models import User

from students.models import ClassRoom
from subjects.models import Subject


# ============================================================
# TEACHER ASSIGNMENT MODEL
# ============================================================

class TeacherAssignment(models.Model):
    """
    Connects a Teacher (Django User) to a ClassRoom and Subject.

    Example:

        Ahmed
          ↓
        Grade 7A
          ↓
        Mathematics

    The Teacher itself is represented by:

        User + Profile(role="Teacher")
    """

    # ========================================================
    # TEACHER
    # ========================================================

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    # ========================================================
    # CLASS ROOM
    # ========================================================

    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    # ========================================================
    # SUBJECT
    # ========================================================

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
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
        default="Active",
    )

    # ========================================================
    # CREATED AT
    # ========================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # ========================================================
    # UPDATED AT
    # ========================================================

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __str__(self):
        teacher_name = self.teacher.get_full_name().strip()

        if not teacher_name:
            teacher_name = self.teacher.username

        return (
            f"{teacher_name} - "
            f"{self.class_room.name} - "
            f"{self.subject.name}"
        )

    # ========================================================
    # META
    # ========================================================

    class Meta:
        ordering = [
            "teacher__username",
            "class_room__name",
            "subject__name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "teacher",
                    "class_room",
                    "subject",
                ],
                name="unique_teacher_class_subject",
            ),
        ]

        verbose_name = "Teacher Assignment"
        verbose_name_plural = "Teacher Assignments"
        