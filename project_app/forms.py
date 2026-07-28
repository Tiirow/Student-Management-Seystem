# ==========================================================
# ModelForm ayaan kasoo qaadaneynaa Django
# ModelForm wuxuu noo oggolaanayaa inaan form ka sameyno Model
# annagoo aan HTML field kasta gacanta ugu qorin.
# ==========================================================
from django.forms import ModelForm


# ==========================================================
# Project model-ka ayaan soo dejineynaa
# Form-kan wuxuu la shaqeyn doonaa Project model-ka.
# ==========================================================
from .models import Project


# ==========================================================
# ProjectForm
# Waa form-ka loo isticmaalo:
#
# - Create Project
# - Update Project
#
# Maadaama uu ka dhaxlay ModelForm,
# Django ayaa si automatic ah u sameynaya fields-ka.
# ==========================================================
class ProjectForm(ModelForm):

    # ======================================================
    # Meta
    #
    # Meta waxay u sheegaysaa Django:
    #
    # 1. Model kee ayaan isticmaaleynaa?
    # 2. Fields kee ayaan rabnaa?
    # ======================================================
    class Meta:

        # Form-kan wuxuu ku saleysan yahay Project model
        model = Project

        # owner-ka lama tusayo user-ka
        # Sababtoo ah owner waxaa si automatic ah loogu dhigaa:
        #
        # project.owner = request.user
        #
        # gudaha createProject()
        exclude = ['owner']