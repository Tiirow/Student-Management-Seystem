# ============================================================
# ATTENDANCE MODELS
# ============================================================
#
# Student Management System
#
# Stores student attendance records.
#
# Attendance is connected to:
#   - Student
#   - Subject
#   - Date
#   - Status
#   - Optional notes
#
# ============================================================

from django.db import models

from students.models import Student

from subjects.models import Subject


# ============================================================
# ATTENDANCE MODEL
# ============================================================

class Attendance(models.Model):

    # ========================================================
    # STATUS CHOICES
    # ========================================================

    STATUS_CHOICES = (
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Late", "Late"),
    )

    # ========================================================
    # STUDENT
    # ========================================================

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    # ========================================================
    # SUBJECT
    # ========================================================

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    # ========================================================
    # ATTENDANCE DATE
    # ========================================================

    date = models.DateField()

    # ========================================================
    # STATUS
    # ========================================================

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Present",
    )

    # ========================================================
    # NOTES
    # ========================================================

    notes = models.TextField(
        blank=True,
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
    # STRING
    # ========================================================

    def __str__(self):
        return (
            f"{self.student.full_name} - "
            f"{self.subject.name} - "
            f"{self.date} - "
            f"{self.status}"
        )

    # ========================================================
    # META
    # ========================================================

    class Meta:

        ordering = [
            "-date",
            "student__first_name",
            "student__last_name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "subject",
                    "date",
                ],
                name="unique_student_subject_date",
            )
        ]

        verbose_name = "Attendance"
        verbose_name_plural = "Attendance Records"
        