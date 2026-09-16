# ============================================================
# STUDENT FORMS
# ============================================================
#
# Student Management System
#
# Handles:
#
#   - Student login username
#   - Student password
#   - Password confirmation
#   - Student personal information
#   - Active classroom selection
#   - Classroom creation/update
#
# IMPORTANT:
#
# Student ID is NOT entered manually.
#
# Student ID is generated automatically by the Student model:
#
#     STU001
#     STU002
#     STU003
#     ...
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

from django import forms

from django.contrib.auth.models import User

from .models import (
    Student,
    ClassRoom,
)


# ============================================================
# STUDENT FORM
# ============================================================

class StudentForm(forms.ModelForm):
    """
    Complete Student creation/update form.

    LOGIN ACCOUNT:
        username
        password
        confirm_password

    PERSONAL INFORMATION:
        first_name
        last_name
        email
        phone
        gender
        date_of_birth
        class_room
        address

    Student ID is generated automatically by the model.
    """

    # ========================================================
    # USERNAME
    # ========================================================

    username = forms.CharField(
        label="Username",
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter username",
                "autocomplete": "username",
            }
        ),
    )

    # ========================================================
    # PASSWORD
    # ========================================================

    password = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter password",
                "autocomplete": "new-password",
            }
        ),
    )

    # ========================================================
    # CONFIRM PASSWORD
    # ========================================================

    confirm_password = forms.CharField(
        label="Confirm Password",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm password",
                "autocomplete": "new-password",
            }
        ),
    )

    # ========================================================
    # DATE OF BIRTH
    # ========================================================

    date_of_birth = forms.DateField(
        label="Date of Birth",
        required=True,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
    )

    # ========================================================
    # CLASS
    # ========================================================

    class_room = forms.ModelChoiceField(
        label="Class",
        queryset=ClassRoom.objects
        .filter(
            status="Active"
        )
        .order_by(
            "name"
        ),
        required=True,
        empty_label="Select class",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    # ========================================================
    # GENDER
    # ========================================================

    gender = forms.ChoiceField(
        label="Gender",
        choices=Student.GENDER_CHOICES,
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    # ========================================================
    # PHONE
    # ========================================================

    phone = forms.CharField(
        label="Phone",
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter phone number",
            }
        ),
    )

    # ========================================================
    # ADDRESS
    # ========================================================

    address = forms.CharField(
        label="Address",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Enter student address",
                "rows": 4,
            }
        ),
    )

    # ========================================================
    # META
    # ========================================================

    class Meta:

        model = Student

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "gender",
            "date_of_birth",
            "class_room",
            "address",
        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter first name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter last name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "student@example.com",
                }
            ),

        }

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        # ----------------------------------------------------
        # UPDATE MODE
        # ----------------------------------------------------

        if self.instance and self.instance.pk:

            # -----------------------------------------------
            # CONNECTED DJANGO USER
            # -----------------------------------------------

            user = getattr(
                self.instance,
                "user",
                None,
            )

            if user:

                self.fields[
                    "username"
                ].initial = user.username

            # -----------------------------------------------
            # PASSWORD OPTIONAL DURING UPDATE
            # -----------------------------------------------

            self.fields[
                "password"
            ].required = False

            self.fields[
                "confirm_password"
            ].required = False

            self.fields[
                "password"
            ].widget.attrs[
                "placeholder"
            ] = (
                "Leave blank to keep current password"
            )

            self.fields[
                "confirm_password"
            ].widget.attrs[
                "placeholder"
            ] = (
                "Repeat new password"
            )

    # ========================================================
    # CLEAN USERNAME
    # ========================================================

    def clean_username(self):

        """
        Validate username uniqueness.

        During update, the current user's username
        is allowed to remain unchanged.
        """

        username = (
            self.cleaned_data.get(
                "username"
            )
        )

        if not username:

            raise forms.ValidationError(
                "Username is required."
            )

        queryset = (
            User.objects
            .filter(
                username__iexact=username
            )
        )

        # ----------------------------------------------------
        # UPDATE MODE
        # ----------------------------------------------------

        if (
            self.instance
            and self.instance.pk
        ):

            current_user = getattr(
                self.instance,
                "user",
                None,
            )

            if current_user:

                queryset = (
                    queryset.exclude(
                        pk=current_user.pk
                    )
                )

        # ----------------------------------------------------
        # DUPLICATE
        # ----------------------------------------------------

        if queryset.exists():

            raise forms.ValidationError(
                "This username is already in use."
            )

        return username.strip()

    # ========================================================
    # CLEAN EMAIL
    # ========================================================

    def clean_email(self):

        """
        Validate email uniqueness against:

            Student.email
            User.email
        """

        email = self.cleaned_data.get(
            "email"
        )

        if not email:

            raise forms.ValidationError(
                "Email is required."
            )

        email = email.strip()

        # ----------------------------------------------------
        # STUDENT EMAIL
        # ----------------------------------------------------

        student_queryset = (
            Student.objects
            .filter(
                email__iexact=email
            )
        )

        # ----------------------------------------------------
        # UPDATE MODE
        # ----------------------------------------------------

        if (
            self.instance
            and self.instance.pk
        ):

            student_queryset = (
                student_queryset.exclude(
                    pk=self.instance.pk
                )
            )

        # ----------------------------------------------------
        # DUPLICATE STUDENT EMAIL
        # ----------------------------------------------------

        if student_queryset.exists():

            raise forms.ValidationError(
                "This email is already used by another student."
            )

        # ----------------------------------------------------
        # USER EMAIL
        # ----------------------------------------------------

        user_queryset = (
            User.objects
            .filter(
                email__iexact=email
            )
        )

        # ----------------------------------------------------
        # UPDATE MODE
        # ----------------------------------------------------

        if (
            self.instance
            and self.instance.pk
        ):

            current_user = getattr(
                self.instance,
                "user",
                None,
            )

            if current_user:

                user_queryset = (
                    user_queryset.exclude(
                        pk=current_user.pk
                    )
                )

        # ----------------------------------------------------
        # DUPLICATE USER EMAIL
        # ----------------------------------------------------

        if user_queryset.exists():

            raise forms.ValidationError(
                "This email is already connected to another account."
            )

        return email

    # ========================================================
    # CLEAN PASSWORD
    # ========================================================

    def clean(self):

        """
        Validate password and confirmation.
        """

        cleaned_data = super().clean()

        password = (
            cleaned_data.get(
                "password"
            )
        )

        confirm_password = (
            cleaned_data.get(
                "confirm_password"
            )
        )

        # ----------------------------------------------------
        # CREATE / UPDATE
        # ----------------------------------------------------

        is_update = bool(
            self.instance
            and self.instance.pk
        )

        # ----------------------------------------------------
        # CREATE MODE
        # ----------------------------------------------------

        if not is_update:

            if not password:

                self.add_error(
                    "password",
                    "Password is required when creating a student account.",
                )

            if not confirm_password:

                self.add_error(
                    "confirm_password",
                    "Please confirm the password.",
                )

        # ----------------------------------------------------
        # PASSWORD MATCH
        # ----------------------------------------------------

        if password or confirm_password:

            if password != confirm_password:

                self.add_error(
                    "confirm_password",
                    "Passwords do not match.",
                )

        return cleaned_data


# ============================================================
# CLASS ROOM FORM
# ============================================================

class ClassRoomForm(forms.ModelForm):
    """
    Form used to create and update school classes.

    Fields:

        name
        description
        status
    """

    # ========================================================
    # CLASS NAME
    # ========================================================

    name = forms.CharField(
        label="Class Name",
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Example: Grade 7A",
            }
        ),
    )

    # ========================================================
    # DESCRIPTION
    # ========================================================

    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Enter class description",
                "rows": 4,
            }
        ),
    )

    # ========================================================
    # STATUS
    # ========================================================

    status = forms.ChoiceField(
        label="Status",
        choices=ClassRoom.STATUS_CHOICES,
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    # ========================================================
    # META
    # ========================================================

    class Meta:

        model = ClassRoom

        fields = [
            "name",
            "description",
            "status",
        ]

    # ========================================================
    # CLEAN NAME
    # ========================================================

    def clean_name(self):

        """
        Validate that class name is unique.

        Existing class name is allowed during update.
        """

        name = self.cleaned_data.get(
            "name"
        )

        if not name:

            raise forms.ValidationError(
                "Class name is required."
            )

        # ----------------------------------------------------
        # NORMALIZE SPACES
        # ----------------------------------------------------

        name = " ".join(
            name.strip().split()
        )

        # ----------------------------------------------------
        # CASE-INSENSITIVE DUPLICATE
        # ----------------------------------------------------

        queryset = (
            ClassRoom.objects
            .filter(
                name__iexact=name
            )
        )

        # ----------------------------------------------------
        # UPDATE MODE
        # ----------------------------------------------------

        if (
            self.instance
            and self.instance.pk
        ):

            queryset = (
                queryset.exclude(
                    pk=self.instance.pk
                )
            )

        # ----------------------------------------------------
        # DUPLICATE
        # ----------------------------------------------------

        if queryset.exists():

            raise forms.ValidationError(
                "This class already exists."
            )

        return name


# ============================================================
# CLASS SUBJECT / CURRICULUM FORM
# ============================================================

from subjects.models import Subject

from .models import ClassSubject


# ============================================================
# CLASS SUBJECT FORM
# ============================================================

class ClassSubjectForm(forms.ModelForm):

    class Meta:

        model = ClassSubject

        fields = [
            "class_room",
            "subject",
            "status",
        ]

        widgets = {

            "class_room": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "subject": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

        }

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        # ----------------------------------------------------
        # ACTIVE CLASSES
        # ----------------------------------------------------

        self.fields[
            "class_room"
        ].queryset = (
            ClassRoom.objects
            .filter(
                status="Active"
            )
            .order_by(
                "name"
            )
        )

        # ----------------------------------------------------
        # ACTIVE SUBJECTS
        # ----------------------------------------------------

        self.fields[
            "subject"
        ].queryset = (
            Subject.objects
            .filter(
                status="Active"
            )
            .order_by(
                "name"
            )
        )

