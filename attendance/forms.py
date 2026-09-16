# ============================================================
# ATTENDANCE FORMS
# ============================================================

from django import forms

from .models import Attendance

from students.models import Student

from subjects.models import Subject


# ============================================================
# ATTENDANCE FORM
# ============================================================

class AttendanceForm(forms.ModelForm):

    class Meta:

        model = Attendance

        fields = [
            "student",
            "subject",
            "date",
            "status",
            "notes",
        ]

        widgets = {

            "student": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "subject": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Optional attendance notes",
                }
            ),
        }

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # ----------------------------------------------------
        # STUDENTS
        # ----------------------------------------------------

        self.fields["student"].queryset = (
            Student.objects
            .select_related("class_room")
            .order_by(
                "first_name",
                "last_name",
            )
        )

        # ----------------------------------------------------
        # SUBJECTS
        # ----------------------------------------------------

        self.fields["subject"].queryset = (
            Subject.objects
            .filter(
                status="Active"
            )
            .order_by(
                "name"
            )
        )

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        self.fields["date"].input_formats = [
            "%Y-%m-%d",
        ]
        