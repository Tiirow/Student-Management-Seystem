# ============================================================
# GRADES FORMS
# ============================================================

from django import forms

from .models import Grade


# ============================================================
# GRADE FORM
# ============================================================

class GradeForm(forms.ModelForm):
    """
    Form used by Administrator / Manager to add or edit
    one student's result.
    """

    class Meta:
        model = Grade

        fields = [
            "student",
            "subject",
            "semester",
            "score",
        ]

        widgets = {

            "student": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "subject": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "semester": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "score": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter score",
                    "min": "0",
                    "max": "100",
                    "step": "0.01",
                }
            ),
        }

    # ========================================================
    # SCORE VALIDATION
    # ========================================================

    def clean_score(self):

        score = self.cleaned_data.get("score")

        if score is None:
            return score

        if score < 0:
            raise forms.ValidationError(
                "Score cannot be below 0."
            )

        if score > 100:
            raise forms.ValidationError(
                "Score cannot be greater than 100."
            )

        return score
    