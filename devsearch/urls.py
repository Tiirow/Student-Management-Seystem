# ============================================================
# MAIN PROJECT URLS
# ============================================================
#
# DevSearch / Student Management System
#
# Main application URL configuration.
#
# Includes:
#
#   - Admin
#   - Dashboard / Projects
#   - Conversations
#   - Notifications
#   - System Logs
#   - Users
#   - Students
#   - Subjects
#   - Enrollment
#   - Grades
#   - Attendance
#   - Teacher Management
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

from django.contrib import admin

from django.urls import (
    path,
    include,
)

# Import the working enrollment view
from students import views as student_views


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # ========================================================
    # ADMIN
    # ========================================================

    path(
        "admin/",
        admin.site.urls,
    ),


    # ========================================================
    # MAIN DASHBOARD + PROJECTS
    # ========================================================

    path(
        "dashboard/",
        include("project_app.urls"),
    ),


    # ========================================================
    # CONVERSATIONS
    # ========================================================

    path(
        "conversations/",
        include("conversations.urls"),
    ),


    # ========================================================
    # NOTIFICATIONS
    # ========================================================

    path(
        "notifications/",
        include("notifications.urls"),
    ),


    # ========================================================
    # SYSTEM LOGS
    # ========================================================

    path(
        "dashboard/logs/",
        include("system_logs.urls"),
    ),


    # ========================================================
    # USERS
    # ========================================================

    path(
        "users/",
        include("users.urls"),
    ),


    # ========================================================
    # STUDENTS
    # ========================================================

    path(
        "students/",
        include("students.urls"),
    ),


    # ========================================================
    # SUBJECTS
    # ========================================================

    path(
        "subjects/",
        include("subjects.urls"),
    ),


    # ========================================================
    # ENROLLMENT MANAGEMENT
    # ========================================================
    #
    # OFFICIAL SYSTEM URL:
    #
    #     /enrollment/
    #
    # This uses the SAME working enrollment view from:
    #
    #     students/views.py
    #
    # Therefore:
    #
    #     /enrollment/
    #
    # and:
    #
    #     /students/enrollment/
    #
    # can use the same functionality.
    #
    # ========================================================

    path(
        "enrollment/",
        student_views.enrollment,
        name="student-enrollment",
    ),


    # ========================================================
    # GRADES / RESULTS
    # ========================================================
    #
    # Manager / Administrator:
    #
    #     /grades/
    #     /grades/create/
    #     /grades/<id>/
    #     /grades/<id>/edit/
    #     /grades/<id>/delete/
    #
    # Student Portal:
    #
    #     /students/grades/
    #     /students/results/
    #
    # Student sees ONLY his/her own academic results.
    #
    # ========================================================

    path(
        "grades/",
        include("grades.urls"),
    ),


    # ========================================================
    # ATTENDANCE
    # ========================================================
    #
    # Main Attendance Management:
    #
    #     /attendance/
    #
    # Administrator / Manager / Teacher:
    #
    #     View + Manage Attendance
    #
    # Student:
    #
    #     /attendance/my/
    #
    #     View ONLY own attendance.
    #
    # ========================================================

    path(
        "attendance/",
        include("attendance.urls"),
    ),


    # ========================================================
    # TEACHER MANAGEMENT
    # ========================================================
    #
    # Teacher application:
    #
    #     /teacher/
    #
    # Teacher dashboard and teacher-specific
    # academic management features.
    #
    # ========================================================

    path(
        "teacher/",
        include("teacherapp.urls"),
    ),
]
