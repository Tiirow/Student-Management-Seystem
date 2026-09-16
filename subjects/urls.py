# ============================================================
# SUBJECT URLS
# ============================================================

from django.urls import path

from . import views


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # ========================================================
    # SUBJECT LIST
    # ========================================================
    #
    # /subjects/
    #
    path(
        "",
        views.subjectList,
        name="subject-list",
    ),


    # ========================================================
    # CREATE SUBJECT
    # ========================================================
    #
    # /subjects/create/
    #
    path(
        "create/",
        views.createSubject,
        name="subject-create",
    ),


    # ========================================================
    # ASSIGN SUBJECT TO CLASS
    # ========================================================
    #
    # /subjects/assign-to-class/
    #
    # Opens the professional Assign Subject to Class page.
    #
    path(
        "assign-to-class/",
        views.assignSubjectToClass,
        name="subject-assign-class",
    ),


    # ========================================================
    # AJAX AVAILABLE SUBJECTS
    # ========================================================
    #
    # /subjects/assign-to-class/available-subjects/
    #
    # Used by JavaScript when a class is selected.
    #
    # Example:
    #
    # /subjects/assign-to-class/available-subjects/
    #     ?class_id=3
    #
    # Returns:
    #
    # {
    #     "success": true,
    #     "subjects": [...]
    # }
    #
    path(
        "assign-to-class/available-subjects/",
        views.availableSubjectsForClass,
        name="available-subjects-for-class",
    ),


    # ========================================================
    # SUBJECT DETAIL
    # ========================================================
    #
    # /subjects/1/
    #
    path(
        "<int:pk>/",
        views.subjectDetail,
        name="subject-detail",
    ),


    # ========================================================
    # UPDATE SUBJECT
    # ========================================================
    #
    # /subjects/1/update/
    #
    path(
        "<int:pk>/update/",
        views.updateSubject,
        name="subject-update",
    ),


    # ========================================================
    # DELETE SUBJECT
    # ========================================================
    #
    # /subjects/1/delete/
    #
    path(
        "<int:pk>/delete/",
        views.deleteSubject,
        name="subject-delete",
    ),
]
