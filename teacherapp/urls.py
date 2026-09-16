# ============================================================

# TEACHER MANAGEMENT URLS

# ============================================================

from django.urls import path

from . import views

app_name = "teacherapp"

urlpatterns = [


# ========================================================
# TEACHER DASHBOARD
# ========================================================

path(
    "",
    views.teacher_dashboard,
    name="teacher-dashboard",
),


# ========================================================
# TEACHER MANAGEMENT
# ========================================================

path(
    "teachers/",
    views.teacher_list,
    name="teacher-list",
),

path(
    "teachers/add/",
    views.teacher_create,
    name="teacher-create",
),

path(
    "teachers/<int:pk>/",
    views.teacher_detail,
    name="teacher-detail",
),

path(
    "teachers/<int:pk>/edit/",
    views.teacher_edit,
    name="teacher-edit",
),

path(
    "teachers/<int:pk>/deactivate/",
    views.teacher_deactivate,
    name="teacher-deactivate",
),

path(
    "teachers/<int:pk>/reactivate/",
    views.teacher_reactivate,
    name="teacher-reactivate",
),

path(
    "teachers/<int:pk>/delete/",
    views.teacher_delete,
    name="teacher-delete",
),


# ========================================================
# TEACHER ASSIGNMENTS
# ========================================================

path(
    "assignments/",
    views.assignment_list,
    name="assignment-list",
),

path(
    "assignments/add/",
    views.assignment_create,
    name="assignment-create",
),

path(
    "assignments/<int:pk>/delete/",
    views.assignment_delete,
    name="assignment-delete",
),

path(
    "assignments/<int:pk>/toggle-status/",
    views.assignment_toggle_status,
    name="assignment-toggle-status",
),


# ========================================================
# AJAX / CLASS SUBJECTS
# ========================================================

path(
    "class-subjects/",
    views.class_subjects,
    name="class-subjects",
),


# ========================================================
# TEACHER GRADES
# ========================================================

path(
    "grades/",
    views.teacher_grades,
    name="teacher-grades",
),

path(
    "grades/<int:assignment_id>/",
    views.teacher_grades,
    name="teacher-grades-assignment",
),


# ========================================================
# TEACHER ATTENDANCE
# ========================================================

path(
    "attendance/",
    views.teacher_attendance,
    name="teacher-attendance",
),

path(
    "attendance/<int:assignment_id>/",
    views.teacher_attendance,
    name="teacher-attendance-assignment",
),


]
