from django.db import models

from students.models import Student
from subjects.models import Subject


# ============================================================
# ENROLLMENT MODEL
# ============================================================
#
# Connects a Student with a Subject.
#
# Also stores:
# - Marks
# - Grade
# - Result
#
# Example:
#
# Mohamed Ali → Mathematics → 92 → A+ → Pass
# Mohamed Ali → English     → 55 → D  → Re-exam
#
# ============================================================


class Enrollment(models.Model):

    # ========================================================
    # STUDENT
    # ========================================================

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    # ========================================================
    # SUBJECT
    # ========================================================

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    # ========================================================
    # MARKS
    # ========================================================
    #
    # Teacher / Manager / Administrator can enter the marks
    # manually.
    #
    # Example:
    #
    # 85
    # 78
    # 92
    # 69
    #
    # Grade and Result are calculated automatically.
    #
    # ========================================================

    marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    # ========================================================
    # GRADE
    # ========================================================
    #
    # Automatically generated from marks.
    #
    # 90-100 → A+
    # 85-89  → A
    # 80-84  → B+
    # 75-79  → B
    # 70-74  → C+
    # 60-69  → C
    # 50-59  → D
    # 0-49   → F
    #
    # ========================================================

    GRADE_CHOICES = (
        ("A+", "A+"),
        ("A", "A"),
        ("B+", "B+"),
        ("B", "B"),
        ("C+", "C+"),
        ("C", "C"),
        ("D", "D"),
        ("F", "F"),
    )

    grade = models.CharField(
        max_length=2,
        choices=GRADE_CHOICES,
        blank=True,
        default=""
    )

    # ========================================================
    # RESULT
    # ========================================================
    #
    # D and F → Re-exam
    # A+, A, B+, B, C+, C → Pass
    #
    # ========================================================

    RESULT_CHOICES = (
        ("Pass", "Pass"),
        ("Re-exam", "Re-exam"),
    )

    result = models.CharField(
        max_length=10,
        choices=RESULT_CHOICES,
        blank=True,
        default=""
    )

    # ========================================================
    # ENROLLMENT DATE
    # ========================================================

    enrolled_at = models.DateTimeField(
        auto_now_add=True
    )

    # ========================================================
    # STATUS
    # ========================================================

    STATUS_CHOICES = (
        ("Active", "Active"),
        ("Dropped", "Dropped"),
        ("Completed", "Completed"),
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Active"
    )

    # ========================================================
    # UPDATED AT
    # ========================================================

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ========================================================
    # CALCULATE GRADE
    # ========================================================

    def calculate_grade(self):

        if self.marks is None:
            return ""

        marks = float(self.marks)

        if marks >= 90:
            return "A+"

        elif marks >= 85:
            return "A"

        elif marks >= 80:
            return "B+"

        elif marks >= 75:
            return "B"

        elif marks >= 70:
            return "C+"

        elif marks >= 60:
            return "C"

        elif marks >= 50:
            return "D"

        else:
            return "F"

    # ========================================================
    # CALCULATE RESULT
    # ========================================================

    def calculate_result(self):

        if not self.grade:
            return ""

        if self.grade in ["D", "F"]:
            return "Re-exam"

        return "Pass"

    # ========================================================
    # SAVE
    # ========================================================
    #
    # Whenever marks are entered or changed:
    #
    # Marks → Grade → Result
    #
    # are automatically updated.
    #
    # ========================================================

    def save(self, *args, **kwargs):

        # Calculate Grade from Marks
        self.grade = self.calculate_grade()

        # Calculate Result from Grade
        self.result = self.calculate_result()

        # Save record
        super().save(*args, **kwargs)

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __str__(self):

        return (
            f"{self.student.first_name} "
            f"{self.student.last_name} - "
            f"{self.subject.name}"
        )

    # ========================================================
    # META
    # ========================================================

    class Meta:

        ordering = ["-enrolled_at"]

        # ----------------------------------------------------
        # Prevent the same student from being enrolled
        # in the same subject more than once.
        # ----------------------------------------------------

        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject"],
                name="unique_student_subject"
            )
        ]

        verbose_name = "Enrollment"

        verbose_name_plural = "Enrollments"
        