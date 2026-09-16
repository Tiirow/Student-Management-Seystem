
# ============================================================
# GRADES URLS
# ============================================================

from django.urls import path

from . import views


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # --------------------------------------------------------
    # GRADE LIST
    # --------------------------------------------------------
    #
    # /grades/
    #
    path(
        "",
        views.grade_list,
        name="grade-list"
    ),


    # --------------------------------------------------------
    # SAVE GRADES
    # --------------------------------------------------------
    #
    # /grades/save/
    #
    path(
        "save/",
        views.save_grades,
        name="grade-save"
    ),


    # --------------------------------------------------------
    # ADD SEMESTER
    # --------------------------------------------------------
    #
    # /grades/semester/add/
    #
    path(
        "semester/add/",
        views.add_semester,
        name="semester-add"
    ),


    # --------------------------------------------------------
    # UPDATE GRADE
    # --------------------------------------------------------
    #
    # /grades/<grade_id>/update/
    #
    path(
        "<int:grade_id>/update/",
        views.update_grade,
        name="grade-update"
    ),


    # --------------------------------------------------------
    # DELETE GRADE
    # --------------------------------------------------------
    #
    # /grades/<grade_id>/delete/
    #
    path(
        "<int:grade_id>/delete/",
        views.delete_grade,
        name="grade-delete"
    ),
]

