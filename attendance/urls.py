
from django.urls import path

from . import views


urlpatterns = [

    # ============================================================
    # ATTENDANCE HOME
    # ============================================================

    path(
        "",
        views.attendanceHome,
        name="attendance-home",
    ),


    # ============================================================
    # SAVE ATTENDANCE
    # ============================================================

    path(
        "save/",
        views.saveAttendance,
        name="attendance-save",
    ),


    # ============================================================
    # ATTENDANCE LIST
    # ============================================================

    path(
        "list/",
        views.attendanceList,
        name="attendance-list",
    ),


    # ============================================================
    # EDIT ATTENDANCE
    # ============================================================

    path(
        "<int:pk>/edit/",
        views.editAttendance,
        name="attendance-edit",
    ),

]