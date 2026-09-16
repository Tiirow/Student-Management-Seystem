# ============================================================
# IMPORTS
# ============================================================

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Project
from .forms import ProjectForm

from notifications.utils import notify_all_users

from system_logs.utils import create_audit_log


# ============================================================
# HELPER FUNCTION
# ============================================================
#
# Function-kan wuxuu hubinayaa permission-ka user-ka.
#
# Tusaale:
#
# has_permission(request.user, 'can_view')
# has_permission(request.user, 'can_add')
# has_permission(request.user, 'can_edit')
# has_permission(request.user, 'can_delete')
#
# ============================================================

def has_permission(user, permission):

    """
    Hubi permission-ka user-ka.
    """

    # --------------------------------------------------------
    # USER LOGIN MA YAHAY?
    # --------------------------------------------------------

    if not user.is_authenticated:
        return False

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    try:

        profile = user.profile

    except Exception:

        return False

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    return getattr(
        profile,
        permission,
        False
    )


# ============================================================
# ACCESS DENIED
# ============================================================
#
# Haddii user-ku uusan permission u lahayn shaqada uu
# isku dayayo, Access Denied page ayaa loo tusayaa.
#
# ============================================================

def access_denied(request):

    return render(
        request,
        'users/access_denied.html'
    )


# ============================================================
# DASHBOARD
# ============================================================
#
# Dashboard-ka wuxuu soo bandhigayaa:
#
# 📁 Total Projects
# 👥 Total Users
# 🟢 Active Users
# 👤 My Projects
# 🆕 Recently Added Projects
# 🔔 Notifications
#
# ============================================================

@login_required(login_url='login')
def dashboard(request):

    # --------------------------------------------------------
    # HUBI VIEW PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request.user,
        'can_view'
    ):

        return access_denied(request)

    # --------------------------------------------------------
    # TOTAL PROJECTS
    # --------------------------------------------------------

    total_projects = Project.objects.count()

    # --------------------------------------------------------
    # TOTAL USERS
    # --------------------------------------------------------

    total_users = User.objects.count()

    # --------------------------------------------------------
    # ACTIVE USERS
    # --------------------------------------------------------

    active_users = User.objects.filter(
        is_active=True
    ).count()

    # --------------------------------------------------------
    # MY PROJECTS
    # --------------------------------------------------------

    my_projects = Project.objects.filter(
        owner=request.user
    ).count()

    # --------------------------------------------------------
    # RECENTLY ADDED PROJECTS
    # --------------------------------------------------------

    recent_projects = Project.objects.select_related(
        'owner'
    ).order_by(
        '-created'
    )[:4]

    # --------------------------------------------------------
    # NOTIFICATIONS
    # --------------------------------------------------------
    #
    # Kaliya notifications-ka user-ka hadda login-ka ah.
    #
    # --------------------------------------------------------

    notifications = request.user.notifications.all()[:10]

    # --------------------------------------------------------
    # UNREAD NOTIFICATIONS
    # --------------------------------------------------------

    unread_notifications = request.user.notifications.filter(
        is_read=False
    ).count()

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        'total_projects': total_projects,

        'total_users': total_users,

        'active_users': active_users,

        'my_projects': my_projects,

        'recent_projects': recent_projects,

        'notifications': notifications,

        'unread_notifications': unread_notifications,

    }

    # --------------------------------------------------------
    # DASHBOARD TEMPLATE
    # --------------------------------------------------------

    return render(
        request,
        'projects/dashboard.html',
        context
    )


# ============================================================
# PROJECTS
# ============================================================
#
# URL:
#
# /projects/
#
# Permission:
#
# can_view = True
#
# ============================================================

@login_required(login_url='login')
def projects(request):

    # --------------------------------------------------------
    # HUBI VIEW PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request.user,
        'can_view'
    ):

        return access_denied(request)

    # --------------------------------------------------------
    # SOO QAADO PROJECTS
    # --------------------------------------------------------

    projects = Project.objects.select_related(
        'owner'
    ).all().order_by(
        '-created'
    )

    # --------------------------------------------------------
    # PERMISSIONS
    # --------------------------------------------------------

    can_add = has_permission(
        request.user,
        'can_add'
    )

    can_edit = has_permission(
        request.user,
        'can_edit'
    )

    can_delete = has_permission(
        request.user,
        'can_delete'
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        'projects': projects,

        'can_add': can_add,

        'can_edit': can_edit,

        'can_delete': can_delete,

    }

    # --------------------------------------------------------
    # PROJECTS PAGE
    # --------------------------------------------------------

    return render(
        request,
        'projects/projects.html',
        context
    )


# ============================================================
# CREATE PROJECT
# ============================================================
#
# Permission:
#
# can_add = True
#
# Audit:
#
# CREATE PROJECT
#
# Notification:
#
# Notify all active users except creator.
#
# ============================================================

@login_required(login_url='login')
def createProject(request):

    # --------------------------------------------------------
    # HUBI ADD PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request.user,
        'can_add'
    ):

        return access_denied(request)

    # --------------------------------------------------------
    # FORM
    # --------------------------------------------------------

    form = ProjectForm()

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == 'POST':

        form = ProjectForm(
            request.POST
        )

        # ----------------------------------------------------
        # FORM VALID
        # ----------------------------------------------------

        if form.is_valid():

            # ------------------------------------------------
            # PROJECT
            # ------------------------------------------------

            project = form.save(
                commit=False
            )

            # ------------------------------------------------
            # OWNER
            # ------------------------------------------------

            project.owner = request.user

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            project.save()

            # ------------------------------------------------
            # SAVE MANY TO MANY
            # ------------------------------------------------

            form.save_m2m()

            # =================================================
            # AUDIT TRAIL
            # =================================================
            #
            # Waxaan diiwaangelinaynaa:
            #
            # WHO:
            # request.user
            #
            # ACTION:
            # create
            #
            # TARGET:
            # Project
            #
            # DESCRIPTION:
            # Created project 'Project Name'
            #
            # =================================================

            create_audit_log(

                request=request,

                action='create',

                description=(
                    f"Created project "
                    f"'{project.title}'."
                ),

                target_type='Project',

                target_id=project.id,

            )

            # =================================================
            # NOTIFICATION
            # =================================================

            notify_all_users(

                message=(
                    f"🆕 New project "
                    f"'{project.title}' "
                    f"was created by "
                    f"{request.user.username}."
                ),

                notification_type='project_created',

                related_project=project,

                exclude_user=request.user

            )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            messages.success(
                request,
                "Project-ka si successfully ah ayaa loo sameeyay."
            )

            # ------------------------------------------------
            # PROJECTS
            # ------------------------------------------------

            return redirect(
                'projects'
            )

    # --------------------------------------------------------
    # CREATE PAGE
    # --------------------------------------------------------

    return render(
        request,
        'projects/project_form.html',
        {
            'form': form
        }
    )


# ============================================================
# PROJECT DETAIL
# ============================================================
#
# Permission:
#
# can_view = True
#
# ============================================================

@login_required(login_url='login')
def project(request, pk):

    # --------------------------------------------------------
    # HUBI VIEW PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request.user,
        'can_view'
    ):

        return access_denied(request)

    # --------------------------------------------------------
    # SOO QAADO PROJECT
    # --------------------------------------------------------

    projectObj = get_object_or_404(
        Project,
        id=pk
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        'projectObj': projectObj

    }

    # --------------------------------------------------------
    # DETAIL PAGE
    # --------------------------------------------------------

    return render(
        request,
        'projects/single-project.html',
        context
    )


# ============================================================
# UPDATE PROJECT
# ============================================================
#
# Permission:
#
# can_edit = True
#
# Audit:
#
# UPDATE PROJECT
#
# ============================================================

@login_required(login_url='login')
def updateProject(request, pk):

    # --------------------------------------------------------
    # HUBI EDIT PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request.user,
        'can_edit'
    ):

        return access_denied(request)

    # --------------------------------------------------------
    # SOO QAADO PROJECT
    # --------------------------------------------------------

    projectObj = get_object_or_404(
        Project,
        id=pk
    )

    # --------------------------------------------------------
    # FORM
    # --------------------------------------------------------

    form = ProjectForm(
        instance=projectObj
    )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == 'POST':

        form = ProjectForm(
            request.POST,
            instance=projectObj
        )

        # ----------------------------------------------------
        # FORM VALID
        # ----------------------------------------------------

        if form.is_valid():

            # ------------------------------------------------
            # SAVE PROJECT
            # ------------------------------------------------

            project = form.save(
                commit=False
            )

            # ------------------------------------------------
            # OWNER HA LA BADALIN
            # ------------------------------------------------
            #
            # User-ka edit-gareynaya ma beddelayo owner-ka.
            #
            # ------------------------------------------------

            project.owner = projectObj.owner

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            project.save()

            # ------------------------------------------------
            # SAVE MANY TO MANY
            # ------------------------------------------------

            form.save_m2m()

            # =================================================
            # AUDIT TRAIL
            # =================================================
            #
            # Waxaan diiwaangelinaynaa update-ka.
            #
            # =================================================

            create_audit_log(

                request=request,

                action='update',

                description=(
                    f"Updated project "
                    f"'{project.title}'."
                ),

                target_type='Project',

                target_id=project.id,

            )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            messages.success(
                request,
                "Project-ka si successfully ah ayaa loo update gareeyay."
            )

            # ------------------------------------------------
            # PROJECT DETAIL
            # ------------------------------------------------

            return redirect(
                'project',
                pk=projectObj.id
            )

    # --------------------------------------------------------
    # UPDATE PAGE
    # --------------------------------------------------------

    return render(
        request,
        'projects/project_form.html',
        {
            'form': form,
            'projectObj': projectObj
        }
    )


# ============================================================
# DELETE PROJECT
# ============================================================
#
# Permission:
#
# can_delete = True
#
# Audit:
#
# DELETE PROJECT
#
# ============================================================

@login_required(login_url='login')
def deleteProject(request, pk):

    # --------------------------------------------------------
    # HUBI DELETE PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request.user,
        'can_delete'
    ):

        return access_denied(request)

    # --------------------------------------------------------
    # SOO QAADO PROJECT
    # --------------------------------------------------------

    projectObj = get_object_or_404(
        Project,
        id=pk
    )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    if request.method == 'POST':

        # ----------------------------------------------------
        # SAVE INFORMATION BEFORE DELETE
        # ----------------------------------------------------
        #
        # Marka project la delete-gareeyo,
        # object-ka database-ka wuu baaba'ayaa.
        #
        # Sidaas darteed title iyo ID ayaan
        # hore u kaydinaynaa.
        #
        # ----------------------------------------------------

        project_id = projectObj.id

        project_title = projectObj.title

        # ----------------------------------------------------
        # AUDIT TRAIL
        # ----------------------------------------------------
        #
        # Audit-ka waa in la sameeyaa BEFORE delete.
        #
        # ----------------------------------------------------

        create_audit_log(

            request=request,

            action='delete',

            description=(
                f"Deleted project "
                f"'{project_title}'."
            ),

            target_type='Project',

            target_id=project_id,

        )

        # ----------------------------------------------------
        # DELETE PROJECT
        # ----------------------------------------------------

        projectObj.delete()

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        messages.success(
            request,
            "Project-ka si successfully ah ayaa loo delete gareeyay."
        )

        # ----------------------------------------------------
        # PROJECTS
        # ----------------------------------------------------

        return redirect(
            'projects'
        )

    # --------------------------------------------------------
    # DELETE CONFIRMATION PAGE
    # --------------------------------------------------------

    return render(
        request,
        'projects/delete.html',
        {
            'projectObj': projectObj
        }
    )
# ============================================================
# TEST ERROR
# ============================================================
#
# TEST ONLY
#
# View-kan wuxuu si ula kac ah u sameynayaa ValueError
# si loo tijaabiyo Error Logging Middleware.
#
# Tusaale:
#
# User: Mohamed
# Error Type: ValueError
# Message: Invalid project ID
# Method: GET
# Path: /dashboard/project/abc/
#
# ============================================================

@login_required(login_url='login')
def test_error(request):

    # --------------------------------------------------------
    # TEST ERROR
    # --------------------------------------------------------

    raise ValueError(
        "Invalid project ID"
    )
