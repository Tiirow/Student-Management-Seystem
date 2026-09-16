# ============================================================
# STUDENTS URLS
# ============================================================
#
# Dynamic Student Management System
#
# MAIN URL:
#     /students/
#
# RESPONSIBILITIES:
#
#     Student Management
#     Class Management
#     Enrollment
#     Student Portal
#
# TEACHER ROUTES ARE NOT HERE.
# Teacher functionality is handled by teacherapp.
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

from django.urls import path

from . import views


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # ========================================================
    # MAIN STUDENT URL
    # ========================================================
    #
    # /students/
    #
    # Routes users according to their role.
    #
    # Administrator / Manager
    #     -> Management Dashboard
    #
    # Teacher
    #     -> Teacher Dashboard
    #
    # Student
    #     -> Student Portal
    #
    # ========================================================

    path(
        "",
        views.studentHome,
        name="student-home",
    ),


    # ========================================================
    # STUDENT PORTAL
    # ========================================================

    # /students/my-dashboard/
    path(
        "my-dashboard/",
        views.studentDashboard,
        name="student-dashboard",
    ),


    # ========================================================
    # STUDENT MY CLASS
    # ========================================================

    # /students/class/
    path(
        "class/",
        views.studentClass,
        name="student-class",
    ),


    # ========================================================
    # STUDENT MY SUBJECTS
    # ========================================================

    # /students/subjects/
    path(
        "subjects/",
        views.studentSubjects,
        name="student-subjects",
    ),


    # ========================================================
    # STUDENT MY GRADES
    # ========================================================

    # /students/grades/
    path(
        "grades/",
        views.studentGrades,
        name="student-grades",
    ),


    # ========================================================
    # STUDENT MY RESULTS
    # ========================================================

    # /students/results/
    path(
        "results/",
        views.studentResults,
        name="student-results",
    ),


    # ========================================================
    # STUDENT MY ATTENDANCE
    # ========================================================

    # /students/attendance/
    path(
        "attendance/",
        views.studentAttendance,
        name="student-attendance",
    ),


    # ========================================================
    # STUDENT MY PROFILE
    # ========================================================

    # /students/profile/
    path(
        "profile/",
        views.studentProfile,
        name="student-profile",
    ),


    # ========================================================
    # STUDENT CREDENTIALS
    # ========================================================

    # Compatibility route for existing system links.
    #
    # /students/credentials/
    #
    # ========================================================

    path(
        "credentials/",
        views.studentCredentials,
        name="student-credentials",
    ),


    # ========================================================
    # STUDENT MANAGEMENT
    # ========================================================

    # ========================================================
    # STUDENT LIST
    # ========================================================

    # /students/list/
    path(
        "list/",
        views.studentList,
        name="student-list",
    ),


    # ========================================================
    # CREATE STUDENT
    # ========================================================

    # /students/create/
    path(
        "create/",
        views.createStudent,
        name="student-create",
    ),


    # ========================================================
    # CLASS MANAGEMENT
    # ========================================================

    # Administrator / Manager:
    #     View + Add + Edit + Delete
    #
    # Teacher:
    #     Teacher functionality is handled by teacherapp.
    #
    # Student:
    #     No management access.
    #
    # ========================================================


    # ========================================================
    # CLASS LIST
    # ========================================================

    # /students/classes/
    path(
        "classes/",
        views.classList,
        name="class-list",
    ),


    # ========================================================
    # CREATE CLASS
    # ========================================================

    # /students/classes/create/
    path(
        "classes/create/",
        views.createClass,
        name="class-create",
    ),


    # ========================================================
    # CLASS DETAIL
    # ========================================================

    # /students/classes/<pk>/
    path(
        "classes/<int:pk>/",
        views.classDetail,
        name="class-view",
    ),


    # ========================================================
    # CLASS CURRICULUM
    # ========================================================

    # /students/classes/<pk>/curriculum/
    path(
        "classes/<int:pk>/curriculum/",
        views.classCurriculum,
        name="class-curriculum",
    ),


    # ========================================================
    # REMOVE SUBJECT FROM CLASS
    # ========================================================

    # /students/classes/subjects/<pk>/remove/
    path(
        "classes/subjects/<int:pk>/remove/",
        views.removeClassSubject,
        name="class-subject-remove",
    ),


    # ========================================================
    # UPDATE CLASS
    # ========================================================

    # /students/classes/<pk>/edit/
    path(
        "classes/<int:pk>/edit/",
        views.updateClass,
        name="class-update",
    ),


    # ========================================================
    # DELETE CLASS
    # ========================================================

    # /students/classes/<pk>/delete/
    path(
        "classes/<int:pk>/delete/",
        views.deleteClass,
        name="class-delete",
    ),


    # ========================================================
    # STUDENT DETAIL
    # ========================================================

    # IMPORTANT:
    # This comes after all fixed routes above.
    #
    # /students/<pk>/
    #
    # ========================================================

    path(
        "<int:pk>/",
        views.studentDetail,
        name="student-detail",
    ),


    # ========================================================
    # UPDATE STUDENT
    # ========================================================

    # /students/<pk>/edit/
    path(
        "<int:pk>/edit/",
        views.updateStudent,
        name="student-update",
    ),


    # ========================================================
    # DELETE STUDENT
    # ========================================================

    # /students/<pk>/delete/
    path(
        "<int:pk>/delete/",
        views.deleteStudent,
        name="student-delete",
    ),


    # ========================================================
    # ENROLLMENT
    # ========================================================

    # /students/enrollment/
    #
    # Flow:
    #
    #     Select Class
    #          ↓
    #     Select Student
    #          ↓
    #     Class Curriculum
    #          ↓
    #     Enrollment
    #
    # ========================================================

    path(
        "enrollment/",
        views.enrollment,
        name="student-enrollment",
    ),
]

