# ============================================================
# SUBJECT FORMS
# ============================================================

from django import forms

from .models import Subject


# ============================================================
# SUBJECT FORM
# ============================================================

class SubjectForm(forms.ModelForm):
    """
    Form used to create and update subjects.

    Subject code is generated automatically from the
    subject name by the view.

    Example:

        Mathematics
            ->
        MAT-001

        English
            ->
        ENG-001
    """

    class Meta:

        model = Subject

        fields = [
            "name",
            "description",
            "credit_hours",
            "status",
        ]

        widgets = {

            # ------------------------------------------------
            # SUBJECT NAME
            # ------------------------------------------------

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Mathematics",
                    "autocomplete": "off",
                }
            ),

            # ------------------------------------------------
            # DESCRIPTION
            # ------------------------------------------------

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Enter subject description..."
                    ),
                }
            ),

            # ------------------------------------------------
            # CREDIT HOURS
            # ------------------------------------------------

            "credit_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 20,
                    "step": 1,
                }
            ),

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    # ========================================================
    # CLEAN NAME
    # ========================================================

    def clean_name(self):
        """
        Clean and validate subject name.
        """

        name = self.cleaned_data.get(
            "name",
            ""
        ).strip()

        if not name:

            raise forms.ValidationError(
                "Subject name is required."
            )

        return name

