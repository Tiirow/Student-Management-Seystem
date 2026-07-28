# ==========================================================
# Import Functions and Classes
# ==========================================================

# render -> HTML page ayuu browser-ka u diraa
# redirect -> User-ka wuxuu u diraa URL kale
# get_object_or_404 -> Object ayuu soo helaa, haddii uusan jirinna 404 ayuu soo celiyaa
from django.shortcuts import render, redirect, get_object_or_404

# login_required -> User-ka waa inuu login yahay si view-kan u isticmaalo
from django.contrib.auth.decorators import login_required

# Project model-ka ayaan soo qaadaneynaa
from .models import Project

# Form-ka lagu sameynayo ama lagu edit gareynayo project
from .forms import ProjectForm


# ==========================================================
# READ ALL PROJECTS
# ==========================================================

def projects(request):

    # Database-ka kasoo qaad dhammaan projects-ka
    projects = Project.objects.all()

    # Context waa xogta aan u dirayno template-ka
    context = {
        'projects': projects
    }

    # Fur projects.html kadib context u dir
    return render(
        request,
        'projects/projects.html',
        context
    )


# ==========================================================
# READ SINGLE PROJECT
# ==========================================================

def project(request, pk):

    # Soo hel project-ka uu id-giisu yahay pk
    # Haddii uusan jirin -> 404
    projectObj = get_object_or_404(
        Project,
        id=pk
    )

    # Soo qaad tags-ka project-kan
    tags = projectObj.tags.all()

    # Context
    context = {
        'projectObj': projectObj,
        'tags': tags
    }

    # Fur single-project.html
    return render(
        request,
        'projects/single-project.html',
        context
    )


# ==========================================================
# CREATE PROJECT
# ==========================================================

# User waa inuu login yahay
@login_required(login_url='login')
def createProject(request):

    # Samee form madhan
    form = ProjectForm()

    # Marka user-ku submit gareeyo form-ka
    if request.method == 'POST':

        # Soo qaado xogta form-ka
        form = ProjectForm(request.POST)

        # Hubi inay sax tahay
        if form.is_valid():

            # Samee project object
            # Laakiin database-ka ha galin wali
            project = form.save(commit=False)

            # User-ka login-ka ah ayaa noqonaya owner-ka project-kan
            project.owner = request.user

            # Hadda database-ka geli
            project.save()

            # Keydi ManyToMany fields (tags)
            form.save_m2m()

            # Ku celi projects page
            return redirect('projects')

    # Context
    context = {
        'form': form
    }

    # Fur form page
    return render(
        request,
        'projects/project_form.html',
        context
    )


# ==========================================================
# UPDATE PROJECT
# ==========================================================

@login_required(login_url='login')
def updateProject(request, pk):

    # Soo hel project-ka
    # Waa inuu:
    # 1. id-ga sax yahay
    # 2. owner-ku yahay user-ka login-ka ah
    project = get_object_or_404(
        Project,
        id=pk,
        owner=request.user
    )

    # Form-ka ku buuxi xogta project-ka
    form = ProjectForm(
        instance=project
    )

    # Marka user-ku submit gareeyo
    if request.method == 'POST':

        # Cusboonaysii xogta
        form = ProjectForm(
            request.POST,
            instance=project
        )

        # Hubi validation
        if form.is_valid():

            # Save changes
            form.save()

            # Dib ugu noqo projects page
            return redirect('projects')

    # Context
    context = {
        'form': form
    }

    # Fur form-ka
    return render(
        request,
        'projects/project_form.html',
        context
    )


# ==========================================================
# DELETE PROJECT
# ==========================================================

@login_required(login_url='login')
def deleteProject(request, pk):

    # Soo hel project-ka
    # Waa inuu leeyahay user-kan
    project = get_object_or_404(
        Project,
        id=pk,
        owner=request.user
    )

    # Marka user-ku xaqiijiyo delete
    if request.method == 'POST':

        # Ka saar database-ka
        project.delete()

        # Dib ugu noqo projects page
        return redirect('projects')

    # Context
    context = {
        'object': project
    }

    # Fur delete confirmation page
    return render(
        request,
        'projects/delete_template.html',
        context
    )