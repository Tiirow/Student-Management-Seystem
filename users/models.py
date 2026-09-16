from django.db import models
from django.contrib.auth.models import User


# ============================================================
# PROFILE
# ============================================================
#
# Student Management System
#
# ROLE ARCHITECTURE:
#
# Administrator
#     ↓
# Full System Management
#
# Manager
#     ↓
# Operational / View Management
#
# Teacher
#     ↓
# Academic Management
#
# Student
#     ↓
# Self-Service
#
# ============================================================


class Profile(models.Model):

    # ========================================================
    # ROLE SYSTEM
    # ========================================================

    ROLE_CHOICES = (
        ("Administrator", "Administrator"),
        ("Manager", "Manager"),
        ("Teacher", "Teacher"),
        ("Student", "Student"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="Student",
    )

    # ========================================================
    # ACCESS APPROVAL
    # ========================================================
    #
    # False = User has registered but Administrator
    #         has not granted system access yet.
    #
    # True  = Administrator has approved the user.
    #
    # ========================================================

    is_approved = models.BooleanField(
        default=False,
    )

    # ========================================================
    # STUDENTS MODULE
    # ========================================================

    can_view_students = models.BooleanField(default=False)
    can_add_students = models.BooleanField(default=False)
    can_edit_students = models.BooleanField(default=False)
    can_delete_students = models.BooleanField(default=False)

    # ========================================================
    # TEACHERS MODULE
    # ========================================================

    can_view_teachers = models.BooleanField(default=False)
    can_manage_teachers = models.BooleanField(default=False)

    # ========================================================
    # SUBJECTS MODULE
    # ========================================================

    can_view_subjects = models.BooleanField(default=False)
    can_manage_subjects = models.BooleanField(default=False)

    # ========================================================
    # ENROLLMENT MODULE
    # ========================================================

    can_manage_enrollment = models.BooleanField(default=False)

    # ========================================================
    # ATTENDANCE MODULE
    # ========================================================

    can_view_attendance = models.BooleanField(default=False)
    can_manage_attendance = models.BooleanField(default=False)

    # ========================================================
    # GRADES MODULE
    # ========================================================

    can_view_grades = models.BooleanField(default=False)
    can_manage_grades = models.BooleanField(default=False)

    # ========================================================
    # USERS MODULE
    # ========================================================

    can_view_users = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)

    # ========================================================
    # REPORTS MODULE
    # ========================================================

    can_view_reports = models.BooleanField(default=False)

    # ========================================================
    # NOTIFICATIONS MODULE
    # ========================================================

    can_view_notifications = models.BooleanField(default=False)
    can_manage_notifications = models.BooleanField(default=False)

    # ========================================================
    # SETTINGS MODULE
    # ========================================================

    can_view_settings = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)

    # ========================================================
    # ACCESS LEVEL
    # ========================================================

    @property
    def access_level(self):

        if not self.is_approved:
            return "Pending Administrator Approval"

        access_levels = {
            "Administrator": "Full System Management",
            "Manager": "Operational Management",
            "Teacher": "Academic Management",
            "Student": "Self-Service",
        }

        return access_levels.get(
            self.role,
            "Restricted Access",
        )

    # ========================================================
    # ROLE DESCRIPTION
    # ========================================================

    @property
    def role_description(self):

        descriptions = {

            "Administrator": (
                "Full system management including users, teachers, "
                "teacher assignments, students, subjects, enrollment, "
                "attendance, grades, reports, notifications and settings."
            ),

            "Manager": (
                "Operational management access for viewing and monitoring "
                "students, teachers, subjects, enrollment, attendance, "
                "grades, reports and system information. Managers cannot "
                "create teachers, edit teacher accounts or manage teacher assignments."
            ),

            "Teacher": (
                "Academic management access limited to assigned classes "
                "and subjects, including students, attendance, grades and results."
            ),

            "Student": (
                "Self-service access to personal academic information, "
                "subjects, attendance, grades and notifications."
            ),
        }

        if not self.is_approved:
            return (
                "Your account is waiting for Administrator approval. "
                "You cannot access the system until access is granted."
            )

        return descriptions.get(
            self.role,
            "Restricted system access.",
        )

    # ========================================================
    # RESET PERMISSIONS
    # ========================================================

    def reset_permissions(self):

        self.can_view_students = False
        self.can_add_students = False
        self.can_edit_students = False
        self.can_delete_students = False

        self.can_view_teachers = False
        self.can_manage_teachers = False

        self.can_view_subjects = False
        self.can_manage_subjects = False

        self.can_manage_enrollment = False

        self.can_view_attendance = False
        self.can_manage_attendance = False

        self.can_view_grades = False
        self.can_manage_grades = False

        self.can_view_users = False
        self.can_manage_users = False

        self.can_view_reports = False

        self.can_view_notifications = False
        self.can_manage_notifications = False

        self.can_view_settings = False
        self.can_manage_settings = False

    # ========================================================
    # APPLY ROLE PERMISSIONS
    # ========================================================

    def apply_role_permissions(self):

        # ====================================================
        # RESET
        # ====================================================

        self.reset_permissions()

        # ====================================================
        # ADMINISTRATOR
        # ====================================================

        if self.role == "Administrator":

            # Students
            self.can_view_students = True
            self.can_add_students = True
            self.can_edit_students = True
            self.can_delete_students = True

            # Teachers
            self.can_view_teachers = True
            self.can_manage_teachers = True

            # Subjects
            self.can_view_subjects = True
            self.can_manage_subjects = True

            # Enrollment
            self.can_manage_enrollment = True

            # Attendance
            self.can_view_attendance = True
            self.can_manage_attendance = True

            # Grades
            self.can_view_grades = True
            self.can_manage_grades = True

            # Users
            self.can_view_users = True
            self.can_manage_users = True

            # Reports
            self.can_view_reports = True

            # Notifications
            self.can_view_notifications = True
            self.can_manage_notifications = True

            # Settings
            self.can_view_settings = True
            self.can_manage_settings = True

        # ====================================================
        # MANAGER
        # ====================================================

        elif self.role == "Manager":

            # Students
            self.can_view_students = True
            self.can_add_students = True
            self.can_edit_students = True
            self.can_delete_students = True

            # Teachers - VIEW ONLY
            self.can_view_teachers = True
            self.can_manage_teachers = False

            # Subjects - VIEW ONLY
            self.can_view_subjects = True
            self.can_manage_subjects = False

            # Enrollment
            self.can_manage_enrollment = True

            # Attendance - VIEW ONLY
            self.can_view_attendance = True
            self.can_manage_attendance = False

            # Grades - VIEW ONLY
            self.can_view_grades = True
            self.can_manage_grades = False

            # Users - VIEW ONLY
            self.can_view_users = True
            self.can_manage_users = False

            # Reports
            self.can_view_reports = True

            # Notifications - VIEW ONLY
            self.can_view_notifications = True
            self.can_manage_notifications = False

            # Settings - NO ACCESS
            self.can_view_settings = False
            self.can_manage_settings = False

        # ====================================================
        # TEACHER
        # ====================================================

        elif self.role == "Teacher":

            # Students
            self.can_view_students = True
            self.can_add_students = False
            self.can_edit_students = False
            self.can_delete_students = False

            # Teachers
            self.can_view_teachers = False
            self.can_manage_teachers = False

            # Subjects
            self.can_view_subjects = True
            self.can_manage_subjects = False

            # Enrollment
            self.can_manage_enrollment = False

            # Attendance
            self.can_view_attendance = True
            self.can_manage_attendance = True

            # Grades
            self.can_view_grades = True
            self.can_manage_grades = True

            # Users
            self.can_view_users = False
            self.can_manage_users = False

            # Reports
            self.can_view_reports = True

            # Notifications
            self.can_view_notifications = True
            self.can_manage_notifications = False

            # Settings
            self.can_view_settings = False
            self.can_manage_settings = False

        # ====================================================
        # STUDENT
        # ====================================================

        elif self.role == "Student":

            # Students
            self.can_view_students = False
            self.can_add_students = False
            self.can_edit_students = False
            self.can_delete_students = False

            # Teachers
            self.can_view_teachers = False
            self.can_manage_teachers = False

            # Subjects
            self.can_view_subjects = True
            self.can_manage_subjects = False

            # Enrollment
            self.can_manage_enrollment = False

            # Attendance
            self.can_view_attendance = True
            self.can_manage_attendance = False

            # Grades
            self.can_view_grades = True
            self.can_manage_grades = False

            # Users
            self.can_view_users = False
            self.can_manage_users = False

            # Reports
            self.can_view_reports = False

            # Notifications
            self.can_view_notifications = True
            self.can_manage_notifications = False

            # Settings
            self.can_view_settings = False
            self.can_manage_settings = False

    # ========================================================
    # SAVE
    # ========================================================

    def save(self, *args, **kwargs):

        self.apply_role_permissions()

        super().save(
            *args,
            **kwargs,
        )

    # ========================================================
    # STRING
    # ========================================================

    def __str__(self):

        return (
            f"{self.user.username} - {self.role}"
        )


# ============================================================
# LOGIN ATTEMPT
# ============================================================

class LoginAttempt(models.Model):

    username = models.CharField(
        max_length=150,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    created = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):

        return (
            f"{self.username} - "
            f"{self.created}"
        )

    class Meta:

        ordering = ["-created"]

        verbose_name = "Login Attempt"

        verbose_name_plural = "Login Attempts"