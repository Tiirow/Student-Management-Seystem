# ============================================================
# GRADES MODELS
# ============================================================

from django.db import models

from students.models import Student
from subjects.models import Subject


# ============================================================
# SEMESTER MODEL
# ============================================================

class Semester(models.Model):

    # --------------------------------------------------------
    # SEMESTER NAME
    # --------------------------------------------------------

    name = models.CharField(
        max_length=100,
        unique=True
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    STATUS_CHOICES = [

        ("Active", "Active"),

        ("Inactive", "Inactive"),

    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Active"
    )

    # --------------------------------------------------------
    # CREATED AT
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # --------------------------------------------------------
    # UPDATED AT
    # --------------------------------------------------------

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    def __str__(self):

        return self.name

    # --------------------------------------------------------
    # META
    # --------------------------------------------------------

    class Meta:

        ordering = ["name"]

        verbose_name = "Semester"

        verbose_name_plural = "Semesters"


# ============================================================
# GRADE MODEL
# ============================================================

class Grade(models.Model):

    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="grades",
    )

    # --------------------------------------------------------
    # SUBJECT
    # --------------------------------------------------------

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="grades",
    )

    # --------------------------------------------------------
    # SEMESTER
    # --------------------------------------------------------

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    # --------------------------------------------------------
    # CREATED AT
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # --------------------------------------------------------
    # UPDATED AT
    # --------------------------------------------------------

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # --------------------------------------------------------
    # META
    # --------------------------------------------------------

    class Meta:

        ordering = [
            "subject__name",
        ]

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "student",
                    "subject",
                    "semester",
                ],

                name="unique_student_subject_semester",

            )

        ]

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    def __str__(self):

        return (
            f"{self.student} - "
            f"{self.subject} - "
            f"{self.semester} - "
            f"{self.score}"
        )

    # --------------------------------------------------------
    # LETTER GRADE
    # --------------------------------------------------------

    @property
    def letter_grade(self):

        if self.score >= 90:
            return "A+"

        elif self.score >= 85:
            return "A"

        elif self.score >= 80:
            return "B+"

        elif self.score >= 75:
            return "B"

        elif self.score >= 70:
            return "C+"

        elif self.score >= 60:
            return "C"

        elif self.score >= 50:
            return "D"

        return "F"

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    @property
    def result(self):

        if self.score >= 50 and self.score <= 59:
            return "RE-EXAM"

        elif self.score < 50:
            return "FAIL"

        return "PASS"
    