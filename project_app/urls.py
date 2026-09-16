
from django.urls import path
from . import views


urlpatterns = [
    
    path(
    'project/abc/',
    views.test_error,
    name='test_error'
),

    # ============================================================
    # DASHBOARD
    # ============================================================

    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    # ============================================================
    # PROJECTS
    # ============================================================

    path(
        'projects/',
        views.projects,
        name='projects'
    ),

    # ============================================================
    # PROJECT DETAIL
    # ============================================================

    path(
        'project/<str:pk>/',
        views.project,
        name='project'
    ),

    # ============================================================
    # CREATE PROJECT
    # ============================================================

    path(
        'create-project/',
        views.createProject,
        name='create-project'
    ),

    # ============================================================
    # UPDATE PROJECT
    # ============================================================

    path(
        'update-project/<str:pk>/',
        views.updateProject,
        name='update-project'
    ),

    # ============================================================
    # DELETE PROJECT
    # ============================================================

    path(
        'delete-project/<str:pk>/',
        views.deleteProject,
        name='delete-project'
    ),

]

