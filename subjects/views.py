# ============================================================
# SUBJECTS VIEWS
# ============================================================
#
# Student Management System
#
# Handles:
#
#   - Subject List
#   - Subject Detail
#   - Create Subject
#   - Update Subject
#   - Delete Subject
#   - Assign Existing Subject to Class
#   - AJAX Available Subjects
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages

from django.db import transaction

from django.db.models import Count

from django.http import JsonResponse

from .models import Subject

from students.models import (
    ClassRoom,
    ClassSubject,
)

from enrollment.models import Enrollment

from .forms import SubjectForm


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required_redirect(request):
    """
    Redirect unauthenticated users to login.
    """

    if not request.user.is_authenticated:

        login_url = "/users/login/"

        return redirect(
            f"{login_url}?next={request.get_full_path()}"
        )

    return None


# ============================================================
# SUBJECT PERMISSION
# ============================================================

def subject_permission_required(request):
    """
    Allow only users who can manage subjects.

    Allowed:

        - Superuser
        - Users with can_manage_subjects
    """

    login_redirect = (
        login_required_redirect(request)
    )

    if login_redirect:
        return login_redirect

    # --------------------------------------------------------
    # SUPERUSER
    # --------------------------------------------------------

    if request.user.is_superuser:
        return None

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    try:

        profile = request.user.profile

    except Exception:

        return render(
            request,
            "users/access_denied.html",
        )

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not profile.can_manage_subjects:

        return render(
            request,
            "users/access_denied.html",
        )

    return None


# ============================================================
# GENERATE SUBJECT CODE
# ============================================================

def generate_subject_code(
    name,
    instance=None,
):
    """
    Generate a unique subject code automatically.

    Examples:

        Mathematics
            -> MAT-001

        English
            -> ENG-001

        Computer Science
            -> COM-001
    """

    clean_name = " ".join(
        (name or "").strip().split()
    )

    words = clean_name.split()

    # --------------------------------------------------------
    # PREFIX
    # --------------------------------------------------------

    if len(words) >= 2:

        prefix = "".join(
            word[0]
            for word in words[:3]
            if word
        ).upper()

    else:

        prefix = (
            clean_name[:3]
            .upper()
        )

    if not prefix:

        prefix = "SUB"

    prefix = (
        prefix
        .replace(" ", "")
        [:3]
        .upper()
    )

    while len(prefix) < 3:

        prefix += "X"

    # --------------------------------------------------------
    # EXISTING CODES
    # --------------------------------------------------------

    existing_codes = (
        Subject.objects
        .filter(
            code__istartswith=f"{prefix}-"
        )
        .values_list(
            "code",
            flat=True,
        )
    )

    used_numbers = set()

    for code in existing_codes:

        try:

            number = int(
                str(code).split("-")[-1]
            )

            used_numbers.add(
                number
            )

        except (
            ValueError,
            TypeError,
        ):

            continue

    # --------------------------------------------------------
    # NEXT NUMBER
    # --------------------------------------------------------

    next_number = 1

    while next_number in used_numbers:

        next_number += 1

    generated_code = (
        f"{prefix}-{next_number:03d}"
    )

    # --------------------------------------------------------
    # FINAL SAFETY CHECK
    # --------------------------------------------------------

    while (
        Subject.objects
        .filter(
            code__iexact=generated_code
        )
        .exclude(
            pk=(
                instance.pk
                if instance
                else None
            )
        )
        .exists()
    ):

        next_number += 1

        generated_code = (
            f"{prefix}-{next_number:03d}"
        )

    return generated_code


# ============================================================
# SUBJECT LIST
# ============================================================

def subjectList(request):

    access = (
        subject_permission_required(
            request
        )
    )

    if access:
        return access

    subjects = (
        Subject.objects
        .annotate(
            enrollment_count=Count(
                "enrollments",
                distinct=True,
            )
        )
        .order_by(
            "name"
        )
    )

    total_subjects = (
        Subject.objects.count()
    )

    active_subjects = (
        Subject.objects
        .filter(
            status="Active"
        )
        .count()
    )

    classes = (
        ClassRoom.objects
        .annotate(
            subject_count=Count(
                "class_subjects",
                distinct=True,
            )
        )
        .order_by(
            "name"
        )
    )

    total_classes = (
        ClassRoom.objects.count()
    )

    context = {

        "subjects": subjects,

        "total_subjects": total_subjects,

        "active_subjects": active_subjects,

        "classes": classes,

        "total_classes": total_classes,
    }

    return render(
        request,
        "subjects/subject_list.html",
        context,
    )


# ============================================================
# SUBJECT DETAIL
# ============================================================

def subjectDetail(
    request,
    pk,
):

    access = (
        subject_permission_required(
            request
        )
    )

    if access:
        return access

    subject = get_object_or_404(
        Subject,
        pk=pk,
    )

    enrollments = (
        Enrollment.objects
        .filter(
            subject=subject,
        )
        .select_related(
            "student",
            "student__class_room",
        )
        .order_by(
            "student__first_name",
            "student__last_name",
        )
    )

    student_count = (
        enrollments
        .values(
            "student"
        )
        .distinct()
        .count()
    )

    class_subjects = (
        ClassSubject.objects
        .filter(
            subject=subject,
        )
        .select_related(
            "class_room",
            "subject",
        )
        .order_by(
            "class_room__name",
        )
    )

    classes = (
        ClassRoom.objects
        .filter(
            class_subjects__subject=subject,
            class_subjects__status="Active",
        )
        .annotate(
            class_student_count=Count(
                "students",
                distinct=True,
            )
        )
        .distinct()
        .order_by(
            "name",
        )
    )

    class_count = classes.count()

    context = {

        "subject": subject,

        "enrollments": enrollments,

        "student_count": student_count,

        "class_subjects": class_subjects,

        "classes": classes,

        "class_count": class_count,
    }

    return render(
        request,
        "subjects/subject_detail.html",
        context,
    )


# ============================================================
# CREATE SUBJECT
# ============================================================

@transaction.atomic
def createSubject(request):

    access = (
        subject_permission_required(
            request
        )
    )

    if access:
        return access

    classes = (
        ClassRoom.objects
        .filter(
            status="Active"
        )
        .order_by(
            "name"
        )
    )

    if request.method == "POST":

        form = SubjectForm(
            request.POST
        )

        selected_class_id = (
            request.POST
            .get(
                "class_id",
                "",
            )
            .strip()
        )

        if form.is_valid():

            name = form.cleaned_data[
                "name"
            ]

            code = (
                generate_subject_code(
                    name
                )
            )

            subject = form.save(
                commit=False
            )

            subject.code = code

            subject.save()

            # ------------------------------------------------
            # OPTIONAL CLASS ASSIGNMENT
            # ------------------------------------------------

            if selected_class_id:

                classroom = get_object_or_404(
                    ClassRoom,
                    pk=selected_class_id,
                    status="Active",
                )

                (
                    ClassSubject.objects
                    .get_or_create(
                        class_room=classroom,
                        subject=subject,
                        defaults={
                            "status": "Active",
                        },
                    )
                )

                messages.success(
                    request,
                    (
                        f"{subject.name} was created "
                        f"with code {subject.code} "
                        f"and assigned to "
                        f"{classroom.name}."
                    ),
                )

            else:

                messages.success(
                    request,
                    (
                        f"{subject.name} was created "
                        f"successfully with code "
                        f"{subject.code}."
                    ),
                )

            return redirect(
                "subject-list"
            )

    else:

        form = SubjectForm()

        selected_class_id = ""

    context = {

        "form": form,

        "subject": None,

        "classes": classes,

        "selected_class_id": (
            selected_class_id
        ),

        "page_title": (
            "Add New Subject"
        ),

        "submit_text": (
            "Save Subject"
        ),
    }

    return render(
        request,
        "subjects/subject_form.html",
        context,
    )


# ============================================================
# UPDATE SUBJECT
# ============================================================

@transaction.atomic
def updateSubject(
    request,
    pk,
):

    access = (
        subject_permission_required(
            request
        )
    )

    if access:
        return access

    subject = get_object_or_404(
        Subject,
        pk=pk,
    )

    if request.method == "POST":

        form = SubjectForm(
            request.POST,
            instance=subject,
        )

        if form.is_valid():

            original_code = (
                subject.code
            )

            subject = form.save(
                commit=False
            )

            subject.code = (
                original_code
            )

            subject.save()

            messages.success(
                request,
                (
                    f"{subject.name} was updated "
                    f"successfully."
                ),
            )

            return redirect(
                "subject-list"
            )

    else:

        form = SubjectForm(
            instance=subject
        )

    context = {

        "form": form,

        "subject": subject,

        "page_title": "Edit Subject",

        "submit_text": (
            "Update Subject"
        ),
    }

    return render(
        request,
        "subjects/subject_form.html",
        context,
    )


# ============================================================
# DELETE SUBJECT
# ============================================================

@transaction.atomic
def deleteSubject(
    request,
    pk,
):

    access = (
        subject_permission_required(
            request
        )
    )

    if access:
        return access

    subject = get_object_or_404(
        Subject,
        pk=pk,
    )

    if request.method == "POST":

        subject_name = subject.name

        subject.delete()

        messages.success(
            request,
            (
                f"{subject_name} was deleted "
                f"successfully."
            ),
        )

        return redirect(
            "subject-list"
        )

    return render(
        request,
        "subjects/subject_confirm_delete.html",
        {
            "subject": subject,
        },
    )


# ============================================================
# AVAILABLE SUBJECTS HELPER
# ============================================================

def get_available_subjects_for_class(
    class_id
):
    """
    Return ACTIVE subjects that are NOT already
    actively assigned to the selected class.

    Inactive assignments are allowed to appear so
    they can be reactivated when assigned again.
    """

    if not class_id:

        return Subject.objects.none()

    assigned_subject_ids = (
        ClassSubject.objects
        .filter(
            class_room_id=class_id,
            status="Active",
        )
        .values_list(
            "subject_id",
            flat=True,
        )
    )

    return (
        Subject.objects
        .filter(
            status="Active",
        )
        .exclude(
            id__in=assigned_subject_ids,
        )
        .order_by(
            "name",
        )
    )


# ============================================================
# AJAX: AVAILABLE SUBJECTS FOR CLASS
# ============================================================

def availableSubjectsForClass(request):
    """
    AJAX endpoint for dynamic Subject loading.

    URL example:

        /subjects/assign-class/available-subjects/?class_id=3

    Returns:

        {
            "success": true,
            "subjects": [
                {
                    "id": 1,
                    "code": "MAT-001",
                    "name": "Mathematics"
                }
            ]
        }
    """

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if not request.user.is_authenticated:

        return JsonResponse(
            {
                "success": False,
                "error": "Authentication required.",
            },
            status=401,
        )

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if request.user.is_superuser:

        pass

    else:

        try:

            profile = request.user.profile

        except Exception:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Permission denied.",
                },
                status=403,
            )

        if not profile.can_manage_subjects:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Permission denied.",
                },
                status=403,
            )

    # --------------------------------------------------------
    # ONLY GET
    # --------------------------------------------------------

    if request.method != "GET":

        return JsonResponse(
            {
                "success": False,
                "error": "GET request required.",
            },
            status=405,
        )

    # --------------------------------------------------------
    # CLASS ID
    # --------------------------------------------------------

    class_id = (
        request.GET
        .get(
            "class_id",
            "",
        )
        .strip()
    )

    if not class_id:

        return JsonResponse(
            {
                "success": True,
                "subjects": [],
            }
        )

    # --------------------------------------------------------
    # ACTIVE CLASS
    # --------------------------------------------------------

    classroom = get_object_or_404(
        ClassRoom,
        pk=class_id,
        status="Active",
    )

    # --------------------------------------------------------
    # SUBJECTS
    # --------------------------------------------------------

    subjects = (
        get_available_subjects_for_class(
            classroom.id
        )
    )

    subject_data = []

    for subject in subjects:

        subject_data.append(
            {
                "id": subject.id,
                "code": subject.code,
                "name": subject.name,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "subjects": subject_data,
        }
    )


# ============================================================
# ASSIGN EXISTING SUBJECT TO CLASS
# ============================================================

@transaction.atomic
def assignSubjectToClass(request):
    """
    Assign an EXISTING subject to an existing class.

    GET:
        Displays assignment page.

    POST:
        Creates or reactivates ClassSubject.

    Important:
        Dynamic subject loading is handled separately by
        availableSubjectsForClass().
    """

    access = (
        subject_permission_required(
            request
        )
    )

    if access:
        return access

    # ========================================================
    # ACTIVE CLASSES
    # ========================================================

    classes = (
        ClassRoom.objects
        .filter(
            status="Active"
        )
        .order_by(
            "name"
        )
    )

    # ========================================================
    # GET SELECTED VALUES
    # ========================================================

    selected_class_id = (
        request.GET
        .get(
            "class_id",
            "",
        )
        .strip()
    )

    selected_subject_id = (
        request.GET
        .get(
            "subject_id",
            "",
        )
        .strip()
    )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        class_id = (
            request.POST
            .get(
                "class_id",
                "",
            )
            .strip()
        )

        subject_id = (
            request.POST
            .get(
                "subject_id",
                "",
            )
            .strip()
        )

        # ----------------------------------------------------
        # CLASS REQUIRED
        # ----------------------------------------------------

        if not class_id:

            messages.error(
                request,
                "Please select a class.",
            )

            return redirect(
                "subject-assign-class"
            )

        # ----------------------------------------------------
        # SUBJECT REQUIRED
        # ----------------------------------------------------

        if not subject_id:

            messages.error(
                request,
                "Please select a subject.",
            )

            return redirect(
                f"/subjects/assign-class/"
                f"?class_id={class_id}"
            )

        # ----------------------------------------------------
        # ACTIVE CLASS
        # ----------------------------------------------------

        classroom = get_object_or_404(
            ClassRoom,
            pk=class_id,
            status="Active",
        )

        # ----------------------------------------------------
        # ACTIVE SUBJECT
        # ----------------------------------------------------

        subject = get_object_or_404(
            Subject,
            pk=subject_id,
            status="Active",
        )

        # ----------------------------------------------------
        # EXISTING ASSIGNMENT
        # ----------------------------------------------------

        assignment = (
            ClassSubject.objects
            .filter(
                class_room=classroom,
                subject=subject,
            )
            .first()
        )

        # ====================================================
        # EXISTING RECORD
        # ====================================================

        if assignment:

            # ------------------------------------------------
            # REACTIVATE
            # ------------------------------------------------

            if assignment.status != "Active":

                assignment.status = "Active"

                assignment.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                messages.success(
                    request,
                    (
                        f"{subject.name} was reactivated "
                        f"for {classroom.name}."
                    ),
                )

            # ------------------------------------------------
            # ALREADY ACTIVE
            # ------------------------------------------------

            else:

                messages.info(
                    request,
                    (
                        f"{subject.name} is already "
                        f"assigned to {classroom.name}."
                    ),
                )

        # ====================================================
        # CREATE NEW
        # ====================================================

        else:

            ClassSubject.objects.create(
                class_room=classroom,
                subject=subject,
                status="Active",
            )

            messages.success(
                request,
                (
                    f"{subject.name} was assigned "
                    f"to {classroom.name}."
                ),
            )

        return redirect(
            "subject-assign-class"
        )

    # ========================================================
    # NORMAL PAGE LOAD
    # ========================================================

    selected_class = None

    available_subjects = (
        Subject.objects.none()
    )

    # --------------------------------------------------------
    # SELECTED CLASS
    # --------------------------------------------------------

    if selected_class_id:

        selected_class = (
            classes
            .filter(
                id=selected_class_id
            )
            .first()
        )

        if selected_class:

            available_subjects = (
                get_available_subjects_for_class(
                    selected_class.id
                )
            )

    # ========================================================
    # CURRENT ASSIGNMENTS
    # ========================================================

    current_assignments = (
        ClassSubject.objects
        .filter(
            status="Active",
        )
        .select_related(
            "class_room",
            "subject",
        )
        .order_by(
            "class_room__name",
            "subject__name",
        )
    )

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "classes": classes,

        "available_subjects": (
            available_subjects
        ),

        "selected_class": (
            selected_class
        ),

        "selected_class_id": (
            selected_class_id
        ),

        "selected_subject_id": (
            selected_subject_id
        ),

        "current_assignments": (
            current_assignments
        ),
    }

    return render(
        request,
        "subjects/assign_subject_to_class.html",
        context,
    )


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

subjectCreate = createSubject

subjectUpdate = updateSubject

subjectDelete = deleteSubject

subjectDetailView = subjectDetail
