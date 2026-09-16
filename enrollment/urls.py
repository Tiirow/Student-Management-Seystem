
# ============================================================
# ENROLLMENT URLS
# ============================================================
#
# Subject & Enrollment Management
#
# Main URL:
# /enrollment/
#
# ============================================================

from django.urls import path

from . import views


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # ========================================================
    # SUBJECT & ENROLLMENT MANAGEMENT
    # /enrollment/
    # ========================================================

    path(
        "",
        views.enrollment,
        name="student-enrollment"
    ),


    # ========================================================
    # CREATE SUBJECT
    # /enrollment/subjects/create/
    # ========================================================

    path(
        "subjects/create/",
        views.create_subject,
        name="subject-create"
    ),


    # ========================================================
    # UPDATE SUBJECT
    # /enrollment/subjects/<id>/update/
    # ========================================================

    path(
        "subjects/<int:pk>/update/",
        views.update_subject,
        name="subject-update"
    ),


    # ========================================================
    # DELETE SUBJECT
    # /enrollment/subjects/<id>/delete/
    # ========================================================

    path(
        "subjects/<int:pk>/delete/",
        views.delete_subject,
        name="subject-delete"
    ),


    # ========================================================
    # CREATE ENROLLMENT
    # /enrollment/create/
    # ========================================================

    path(
        "create/",
        views.create_enrollment,
        name="enrollment-create"
    ),


    # ========================================================
    # STUDENT ENROLLMENT DETAILS
    # AJAX / JSON
    #
    # /enrollment/student/5/details/
    #
    # Returns:
    # - Student name
    # - Student ID
    # - Class
    # - Already enrolled subjects
    # - Available subjects
    # - Total subjects
    # ========================================================

    path(
        "student/<int:pk>/details/",
        views.student_enrollment_details,
        name="student-enrollment-details"
    ),


    # ========================================================
    # ADD CLASS
    # /enrollment/classes/create/
    # ========================================================

    path(
        "classes/create/",
        views.create_class,
        name="class-create"
    ),


    # ========================================================
    # UPDATE ENROLLMENT STATUS
    # /enrollment/<id>/status/
    # ========================================================

    path(
        "<int:pk>/status/",
        views.update_enrollment_status,
        name="enrollment-status-update"
    ),


    # ========================================================
    # DELETE ENROLLMENT
    # REMOVE SUBJECT FROM STUDENT
    #
    # /enrollment/<id>/delete/
    # ========================================================

    path(
        "<int:pk>/delete/",
        views.delete_enrollment,
        name="enrollment-delete"
    ),
]

