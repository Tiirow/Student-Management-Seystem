# ============================================================
# TEACHER MANAGEMENT FORMS
# ============================================================

from django import forms
from django.contrib.auth.models import User

from students.models import ClassRoom, ClassSubject
from subjects.models import Subject

from .models import TeacherAssignment


# ============================================================
# ADD TEACHER FORM
# ============================================================

class TeacherForm(forms.Form):

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter first name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter last name",
            }
        ),
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter username",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter email address",
            }
        ),
    )

    password = forms.CharField(
        required=True,
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter password",
            }
        ),
    )

    confirm_password = forms.CharField(
        required=True,
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm password",
            }
        ),
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "This username is already in use."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email is already in use."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data


# ============================================================
# EDIT TEACHER FORM
# ============================================================

class TeacherEditForm(forms.Form):

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        queryset = User.objects.filter(
            email__iexact=email
        )

        if self.user:
            queryset = queryset.exclude(pk=self.user.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "This email is already in use."
            )

        return email


# ============================================================
# TEACHER ASSIGNMENT FORM
# ============================================================

class TeacherAssignmentForm(forms.ModelForm):

    class Meta:
        model = TeacherAssignment

        fields = [
            "teacher",
            "class_room",
            "subject",
        ]

        widgets = {

            "teacher": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_teacher",
                }
            ),

            "class_room": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_class_room",
                }
            ),

            "subject": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_subject",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ----------------------------------------------------
        # ONLY TEACHERS
        # ----------------------------------------------------

        self.fields["teacher"].queryset = (
            User.objects
            .filter(
                profile__role="Teacher",
                is_active=True,
            )
            .select_related("profile")
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        # ----------------------------------------------------
        # ONLY ACTIVE CLASSES
        # ----------------------------------------------------

        self.fields["class_room"].queryset = (
            ClassRoom.objects
            .filter(status="Active")
            .order_by("name")
        )

        # ----------------------------------------------------
        # SUBJECTS
        #
        # Initial queryset can contain active subjects.
        # JavaScript will replace the list after class selection.
        # Server-side validation below still enforces
        # ClassSubject.
        # ----------------------------------------------------

        self.fields["subject"].queryset = (
            Subject.objects
            .filter(status="Active")
            .order_by("name")
        )

        self.fields["teacher"].empty_label = "Select Teacher"
        self.fields["class_room"].empty_label = "Select Class"
        self.fields["subject"].empty_label = "Select Subject"

    # ========================================================
    # VALIDATION
    # ========================================================

    def clean(self):
        cleaned_data = super().clean()

        teacher = cleaned_data.get("teacher")
        class_room = cleaned_data.get("class_room")
        subject = cleaned_data.get("subject")

        if not teacher or not class_room or not subject:
            return cleaned_data

        # ----------------------------------------------------
        # MAKE SURE TEACHER REALLY HAS TEACHER ROLE
        # ----------------------------------------------------

        try:
            profile = teacher.profile
        except Exception:
            raise forms.ValidationError(
                "Selected user does not have a Teacher profile."
            )

        if profile.role != "Teacher":
            raise forms.ValidationError(
                "Selected user is not a Teacher."
            )

        # ----------------------------------------------------
        # SUBJECT MUST BELONG TO CLASS CURRICULUM
        # ----------------------------------------------------

        class_subject_exists = ClassSubject.objects.filter(
            class_room=class_room,
            subject=subject,
            status="Active",
        ).exists()

        if not class_subject_exists:
            raise forms.ValidationError(
                f"{subject.name} is not assigned to "
                f"{class_room.name}."
            )

        # ----------------------------------------------------
        # DUPLICATE ASSIGNMENT
        # ----------------------------------------------------

        duplicate = TeacherAssignment.objects.filter(
            teacher=teacher,
            class_room=class_room,
            subject=subject,
        )

        if self.instance and self.instance.pk:
            duplicate = duplicate.exclude(
                pk=self.instance.pk
            )

        if duplicate.exists():
            raise forms.ValidationError(
                "This teacher is already assigned to "
                "this class and subject."
            )

        return cleaned_data
    