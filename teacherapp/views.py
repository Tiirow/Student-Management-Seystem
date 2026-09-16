# ============================================================
# TEACHER MANAGEMENT VIEWS
# ============================================================
#
# Student Management System
#
# Roles:
#
# Administrator
#   - Full teacher management
#   - Create/edit/delete teachers
#   - Activate/deactivate teachers
#   - Create/delete/toggle teacher assignments
#
# Manager
#   - View teachers
#   - View teacher assignments
#
# Teacher
#   - Access own teacher dashboard
#   - View ONLY own active assignments
#   - View ONLY assigned classes and subjects
#   - Grades / Attendance access is handled by
#     their respective apps using TeacherAssignment
#
# Student
#   - No access to Teacher Management
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from students.models import ClassRoom, ClassSubject
from subjects.models import Subject

from .forms import (
    TeacherAssignmentForm,
    TeacherEditForm,
    TeacherForm,
)

from .models import TeacherAssignment


# ============================================================
# ROLE HELPERS
# ============================================================

def get_profile(user):
    """
    Safely return the user's Profile.
    """

    try:
        return user.profile
    except Exception:
        return None


def get_user_role(user):
    """
    Return normalized user role.

    Returns:
        administrator
        manager
        teacher
        student
        ""
    """

    if not user or not user.is_authenticated:
        return ""

    # Django superuser is always treated as Administrator.
    if user.is_superuser:
        return "administrator"

    profile = get_profile(user)

    if not profile:
        return ""

    return str(
        profile.role or ""
    ).strip().lower()


def is_administrator(user):
    """
    Check Administrator role.
    """

    return get_user_role(user) == "administrator"


def is_manager(user):
    """
    Check Manager role.
    """

    return get_user_role(user) == "manager"


def is_teacher(user):
    """
    Check Teacher role.
    """

    return get_user_role(user) == "teacher"


def can_view_teacher_management(user):
    """
    Administrator and Manager can view Teacher Management.

    Teacher is intentionally excluded from management pages.
    """

    return (
        is_administrator(user)
        or is_manager(user)
    )


def can_access_teacher_dashboard(user):
    """
    Administrator, Manager and Teacher can access
    the teacher dashboard page.
    """

    return (
        is_administrator(user)
        or is_manager(user)
        or is_teacher(user)
    )


# ============================================================
# TEACHER MANAGEMENT DASHBOARD
# ============================================================

@login_required
def teacher_dashboard(request):
    """
    Teacher Dashboard.

    Administrator:
        Sees all teachers and all assignments.

    Manager:
        Sees all teachers and all assignments.

    Teacher:
        Sees ONLY their own active assignments.
        Other teachers' classes and subjects are hidden.
    """

    # ========================================================
    # ACCESS CHECK
    # ========================================================

    if not can_access_teacher_dashboard(request.user):
        messages.error(
            request,
            "You do not have permission to access Teacher Management.",
        )

        return redirect("student-home")

    # ========================================================
    # DEFAULT VALUES
    # ========================================================

    teachers = User.objects.none()
    my_assignments = TeacherAssignment.objects.none()

    # Teacher-specific class list.
    my_classes = ClassRoom.objects.none()

    # Teacher-specific subject list.
    my_subjects = Subject.objects.none()

    total_teachers = 0
    active_teachers = 0
    inactive_teachers = 0

    total_assignments = 0
    active_assignments = 0

    # ========================================================
    # ADMINISTRATOR / MANAGER
    # ========================================================

    if (
        is_administrator(request.user)
        or is_manager(request.user)
    ):

        teachers = (
            User.objects
            .filter(
                profile__role="Teacher"
            )
            .select_related(
                "profile"
            )
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        total_teachers = teachers.count()

        active_teachers = (
            teachers
            .filter(
                is_active=True
            )
            .count()
        )

        inactive_teachers = (
            teachers
            .filter(
                is_active=False
            )
            .count()
        )

        total_assignments = (
            TeacherAssignment.objects.count()
        )

        active_assignments = (
            TeacherAssignment.objects
            .filter(
                status="Active"
            )
            .count()
        )

    # ========================================================
    # TEACHER
    # ========================================================

    elif is_teacher(request.user):

        # ----------------------------------------------------
        # ONLY THIS TEACHER'S ACTIVE ASSIGNMENTS
        # ----------------------------------------------------

        my_assignments = (
            TeacherAssignment.objects
            .filter(
                teacher=request.user,
                status="Active",
            )
            .select_related(
                "teacher",
                "class_room",
                "subject",
            )
            .order_by(
                "class_room__name",
                "subject__name",
            )
        )

        # ----------------------------------------------------
        # COUNTS
        # ----------------------------------------------------

        total_assignments = my_assignments.count()
        active_assignments = my_assignments.count()

        # ----------------------------------------------------
        # ONLY ASSIGNED CLASSES
        #
        # IMPORTANT:
        # This queryset can NEVER contain classes
        # belonging only to another teacher.
        # ----------------------------------------------------

        my_class_ids = (
            my_assignments
            .values_list(
                "class_room_id",
                flat=True,
            )
            .distinct()
        )

        my_classes = (
            ClassRoom.objects
            .filter(
                id__in=my_class_ids
            )
            .order_by(
                "name"
            )
        )

        # ----------------------------------------------------
        # ONLY ASSIGNED SUBJECTS
        # ----------------------------------------------------

        my_subject_ids = (
            my_assignments
            .values_list(
                "subject_id",
                flat=True,
            )
            .distinct()
        )

        my_subjects = (
            Subject.objects
            .filter(
                id__in=my_subject_ids,
                status="Active",
            )
            .order_by(
                "name"
            )
        )

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {
        # ----------------------------------------------------
        # ADMIN / MANAGER DATA
        # ----------------------------------------------------

        "teachers": teachers,

        "total_teachers": total_teachers,

        "active_teachers": active_teachers,

        "inactive_teachers": inactive_teachers,

        # ----------------------------------------------------
        # ASSIGNMENT DATA
        # ----------------------------------------------------

        "total_assignments": total_assignments,

        "active_assignments": active_assignments,

        # ----------------------------------------------------
        # TEACHER DATA
        # ----------------------------------------------------

        "my_assignments": my_assignments,

        "my_classes": my_classes,

        "my_subjects": my_subjects,

        # ----------------------------------------------------
        # ROLE FLAGS
        # ----------------------------------------------------

        "is_administrator": is_administrator(
            request.user
        ),

        "is_manager": is_manager(
            request.user
        ),

        "is_teacher": is_teacher(
            request.user
        ),
    }

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "teacherapp/teacher_dashboard.html",
        context,
    )


# ============================================================
# TEACHER LIST
# ============================================================

@login_required
def teacher_list(request):
    """
    List all teachers.

    Administrator:
        Allowed.

    Manager:
        Allowed.

    Teacher:
        Not allowed.
    """

    # ========================================================
    # ACCESS
    # ========================================================

    if not can_view_teacher_management(request.user):

        messages.error(
            request,
            "Access denied.",
        )

        return redirect(
            "student-home"
        )

    # ========================================================
    # SEARCH
    # ========================================================

    search = (
        request.GET
        .get(
            "search",
            "",
        )
        .strip()
    )

    # ========================================================
    # TEACHERS
    # ========================================================

    teachers = (
        User.objects
        .filter(
            profile__role="Teacher"
        )
        .select_related(
            "profile"
        )
        .annotate(
            assignment_count=Count(
                "teacher_assignments",
                distinct=True,
            )
        )
    )

    # ========================================================
    # APPLY SEARCH
    # ========================================================

    if search:

        teachers = teachers.filter(
            Q(
                first_name__icontains=search
            )
            |
            Q(
                last_name__icontains=search
            )
            |
            Q(
                username__icontains=search
            )
            |
            Q(
                email__icontains=search
            )
        )

    # ========================================================
    # ORDER
    # ========================================================

    teachers = teachers.order_by(
        "first_name",
        "last_name",
        "username",
    )

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {
        "teachers": teachers,

        "search": search,

        "is_administrator": is_administrator(
            request.user
        ),

        "is_manager": is_manager(
            request.user
        ),
    }

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "teacherapp/teacher_list.html",
        context,
    )


# ============================================================
# ADD TEACHER
# ============================================================

@login_required
def teacher_create(request):
    """
    Create a Teacher.

    Administrator only.
    """

    # ========================================================
    # PERMISSION
    # ========================================================

    if not is_administrator(request.user):

        messages.error(
            request,
            "Only an Administrator can create teachers.",
        )

        return redirect(
            "teacherapp:teacher-list"
        )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        form = TeacherForm(
            request.POST
        )

        if form.is_valid():

            user = User.objects.create_user(
                username=form.cleaned_data[
                    "username"
                ],

                email=form.cleaned_data[
                    "email"
                ],

                password=form.cleaned_data[
                    "password"
                ],

                first_name=form.cleaned_data[
                    "first_name"
                ],

                last_name=form.cleaned_data[
                    "last_name"
                ],
            )

            # =================================================
            # CREATE / UPDATE PROFILE
            # =================================================

            try:

                profile = user.profile

                profile.role = "Teacher"

                profile.save()

            except Exception:

                from users.models import Profile

                Profile.objects.create(
                    user=user,
                    role="Teacher",
                )

            # =================================================
            # SUCCESS
            # =================================================

            messages.success(
                request,
                (
                    f"Teacher "
                    f"{user.get_full_name() or user.username} "
                    f"was created successfully."
                ),
            )

            return redirect(
                "teacherapp:teacher-detail",
                pk=user.pk,
            )

    # ========================================================
    # GET
    # ========================================================

    else:

        form = TeacherForm()

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "teacherapp/teacher_form.html",
        {
            "form": form,

            "page_title": "Add Teacher",

            "is_create": True,

            "is_administrator": is_administrator(
                request.user
            ),
        },
    )


# ============================================================
# TEACHER DETAIL
# ============================================================

@login_required
def teacher_detail(request, pk):
    """
    Display teacher information and assignments.

    Administrator:
        Allowed.

    Manager:
        Allowed.

    Teacher:
        Not allowed to view management detail pages.
    """

    # ========================================================
    # ACCESS
    # ========================================================

    if not can_view_teacher_management(request.user):

        messages.error(
            request,
            "Access denied.",
        )

        return redirect(
            "student-home"
        )

    # ========================================================
    # GET TEACHER
    # ========================================================

    teacher = get_object_or_404(
        User.objects.select_related(
            "profile"
        ),
        pk=pk,
        profile__role="Teacher",
    )

    # ========================================================
    # ASSIGNMENTS
    # ========================================================

    assignments = (
        TeacherAssignment.objects
        .filter(
            teacher=teacher
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
        "teacher": teacher,

        "assignments": assignments,

        "is_administrator": is_administrator(
            request.user
        ),

        "is_manager": is_manager(
            request.user
        ),
    }

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "teacherapp/teacher_detail.html",
        context,
    )


# ============================================================
# EDIT TEACHER
# ============================================================

@login_required
def teacher_edit(request, pk):
    """
    Edit teacher.

    Administrator only.
    """

    # ========================================================
    # PERMISSION
    # ========================================================

    if not is_administrator(request.user):

        messages.error(
            request,
            "Only an Administrator can edit teachers.",
        )

        return redirect(
            "teacherapp:teacher-detail",
            pk=pk,
        )

    # ========================================================
    # GET TEACHER
    # ========================================================

    teacher = get_object_or_404(
        User.objects.select_related(
            "profile"
        ),
        pk=pk,
        profile__role="Teacher",
    )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        form = TeacherEditForm(
            request.POST,
            user=teacher,
        )

        if form.is_valid():

            teacher.first_name = (
                form.cleaned_data[
                    "first_name"
                ]
            )

            teacher.last_name = (
                form.cleaned_data[
                    "last_name"
                ]
            )

            teacher.email = (
                form.cleaned_data[
                    "email"
                ]
            )

            teacher.save()

            messages.success(
                request,
                "Teacher information updated successfully.",
            )

            return redirect(
                "teacherapp:teacher-detail",
                pk=teacher.pk,
            )

    # ========================================================
    # GET FORM
    # ========================================================

    else:

        form = TeacherEditForm(
            initial={
                "first_name": teacher.first_name,

                "last_name": teacher.last_name,

                "email": teacher.email,
            },

            user=teacher,
        )

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "teacherapp/teacher_form.html",
        {
            "form": form,

            "teacher": teacher,

            "page_title": "Edit Teacher",

            "is_create": False,

            "is_administrator": is_administrator(
                request.user
            ),
        },
    )


# ============================================================
# DEACTIVATE TEACHER
# ============================================================

@login_required
def teacher_deactivate(request, pk):
    """
    Deactivate a Teacher.

    Administrator only.

    Also deactivates all teacher assignments.
    """

    # ========================================================
    # PERMISSION
    # ========================================================

    if not is_administrator(request.user):

        messages.error(
            request,
            "Only an Administrator can deactivate teachers.",
        )

        return redirect(
            "teacherapp:teacher-detail",
            pk=pk,
        )

    # ========================================================
    # GET TEACHER
    # ========================================================

    teacher = get_object_or_404(
        User,
        pk=pk,
        profile__role="Teacher",
    )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        teacher.is_active = False

        teacher.save(
            update_fields=[
                "is_active"
            ]
        )

        # Deactivate assignments.
        TeacherAssignment.objects.filter(
            teacher=teacher
        ).update(
            status="Inactive"
        )

        messages.success(
            request,
            "Teacher has been deactivated.",
        )

    # ========================================================
    # REDIRECT
    # ========================================================

    return redirect(
        "teacherapp:teacher-detail",
        pk=teacher.pk,
    )


# ============================================================
# REACTIVATE TEACHER
# ============================================================

@login_required
def teacher_reactivate(request, pk):
    """
    Reactivate a Teacher.

    Administrator only.

    Also reactivates previous assignments.
    """

    # ========================================================
    # PERMISSION
    # ========================================================

    if not is_administrator(request.user):

        messages.error(
            request,
            "Only an Administrator can reactivate teachers.",
        )

        return redirect(
            "teacherapp:teacher-detail",
            pk=pk,
        )

    # ========================================================
    # GET TEACHER
    # ========================================================

    teacher = get_object_or_404(
        User,
        pk=pk,
        profile__role="Teacher",
    )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        teacher.is_active = True

        teacher.save(
            update_fields=[
                "is_active"
            ]
        )

        TeacherAssignment.objects.filter(
            teacher=teacher
        ).update(
            status="Active"
        )

        messages.success(
            request,
            "Teacher has been reactivated.",
        )

    # ========================================================
    # REDIRECT
    # ========================================================

    return redirect(
        "teacherapp:teacher-detail",
        pk=teacher.pk,
    )


# ============================================================
# DELETE TEACHER
# ============================================================

@login_required
def teacher_delete(request, pk):
    """
    Delete a Teacher.

    Administrator only.
    """

    # ========================================================
    # PERMISSION
    # ========================================================

    if not is_administrator(request.user):

        messages.error(
            request,
            "Only an Administrator can delete teachers.",
        )

        return redirect(
            "teacherapp:teacher-detail",
            pk=pk,
        )

    # ========================================================
    # GET TEACHER
    # ========================================================

    teacher = get_object_or_404(
        User,
        pk=pk,
        profile__role="Teacher",
    )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        teacher_name = (
            teacher.get_full_name()
            or teacher.username
        )

        teacher.delete()

        messages.success(
            request,
            f"Teacher {teacher_name} was deleted.",
        )

        return redirect(
            "teacherapp:teacher-list"
        )

    # ========================================================
    # GET CONFIRMATION PAGE
    # ========================================================

    return render(
        request,
        "teacherapp/teacher_delete.html",
        {
            "teacher": teacher,

            "is_administrator": is_administrator(
                request.user
            ),
        },
    )


# ============================================================
# TEACHER ASSIGNMENT LIST
# ============================================================

@login_required
def assignment_list(request):
    """
    List Teacher Assignments.

    Administrator:
        Allowed.

    Manager:
        Allowed.

    Teacher:
        Not allowed to access management assignment list.
    """

    # ========================================================
    # ACCESS
    # ========================================================

    if not can_view_teacher_management(request.user):

        messages.error(
            request,
            "Access denied.",
        )

        return redirect(
            "student-home"
        )

    # ========================================================
    # SEARCH
    # ========================================================

    search = (
        request.GET
        .get(
            "search",
            "",
        )
        .strip()
    )

    # ========================================================
    # QUERYSET
    # ========================================================

    assignments = (
        TeacherAssignment.objects
        .select_related(
            "teacher",
            "class_room",
            "subject",
        )
        .order_by(
            "teacher__first_name",
            "teacher__last_name",
            "class_room__name",
            "subject__name",
        )
    )

    # ========================================================
    # SEARCH FILTER
    # ========================================================

    if search:

        assignments = assignments.filter(
            Q(
                teacher__first_name__icontains=search
            )
            |
            Q(
                teacher__last_name__icontains=search
            )
            |
            Q(
                teacher__username__icontains=search
            )
            |
            Q(
                class_room__name__icontains=search
            )
            |
            Q(
                subject__name__icontains=search
            )
            |
            Q(
                subject__code__icontains=search
            )
        )

    # ========================================================
    # COUNTS
    # ========================================================

    active_count = (
        assignments
        .filter(
            status="Active"
        )
        .count()
    )

    inactive_count = (
        assignments
        .filter(
            status="Inactive"
        )
        .count()
    )

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {
        "assignments": assignments,

        "search": search,

        "active_count": active_count,

        "inactive_count": inactive_count,

        "is_administrator": is_administrator(
            request.user
        ),

        "is_manager": is_manager(
            request.user
        ),
    }

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "teacherapp/teacher_assignments.html",
        context,
    )


# ============================================================
# CREATE ASSIGNMENT
# ============================================================

@login_required
def assignment_create(request):
    """
    Create a Teacher Assignment.

    Administrator only.
    """

    # ========================================================
    # PERMISSION
    # ========================================================

    if not is_administrator(request.user):

        messages.error(
            request,
            "Only an Administrator can create teacher assignments.",
        )

        return redirect(
            "teacherapp:assignment-list"
        )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        form = TeacherAssignmentForm(
            request.POST
        )

        if form.is_valid():

            assignment = form.save(
                commit=False
            )

            assignment.status = "Active"

            assignment.save()

            # =================================================
            # SUCCESS
            # =================================================

            teacher_name = (
                assignment.teacher.get_full_name()
                or assignment.teacher.username
            )

            messages.success(
                request,
                (
                    f"{teacher_name} was assigned to "
                    f"{assignment.class_room.name} - "
                    f"{assignment.subject.name}."
                ),
            )

            return redirect(
                "teacherapp:assignment-list"
            )

    # ========================================================
    # GET
    # ========================================================

    else:

        form = TeacherAssignmentForm()

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "teacherapp/teacher_assignment_form.html",
        {
            "form": form,

            "page_title": "Assign Teacher",

            "is_administrator": is_administrator(
                request.user
            ),
        },
    )


# ============================================================
# DELETE ASSIGNMENT
# ============================================================

@login_required
def assignment_delete(request, pk):
    """
    Delete Teacher Assignment.

    Administrator only.
    """

    # ========================================================
    # PERMISSION
    # ========================================================

    if not is_administrator(request.user):

        messages.error(
            request,
            "Only an Administrator can delete assignments.",
        )

        return redirect(
            "teacherapp:assignment-list"
        )

    # ========================================================
    # GET ASSIGNMENT
    # ========================================================

    assignment = get_object_or_404(
        TeacherAssignment.objects.select_related(
            "teacher",
            "class_room",
            "subject",
        ),
        pk=pk,
    )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        assignment.delete()

        messages.success(
            request,
            "Teacher assignment was removed successfully.",
        )

    # ========================================================
    # REDIRECT
    # ========================================================

    return redirect(
        "teacherapp:assignment-list"
    )


# ============================================================
# ASSIGNMENT STATUS TOGGLE
# ============================================================

@login_required
def assignment_toggle_status(request, pk):
    """
    Activate / deactivate Teacher Assignment.

    Administrator only.
    """

    # ========================================================
    # PERMISSION
    # ========================================================

    if not is_administrator(request.user):

        messages.error(
            request,
            "Only an Administrator can change assignment status.",
        )

        return redirect(
            "teacherapp:assignment-list"
        )

    # ========================================================
    # GET ASSIGNMENT
    # ========================================================

    assignment = get_object_or_404(
        TeacherAssignment,
        pk=pk,
    )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        if assignment.status == "Active":

            assignment.status = "Inactive"

        else:

            assignment.status = "Active"

        assignment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "Assignment status updated.",
        )

    # ========================================================
    # REDIRECT
    # ========================================================

    return redirect(
        "teacherapp:assignment-list"
    )


# ============================================================
# SUBJECTS FOR SELECTED CLASS
# ============================================================

@login_required
def class_subjects(request):
    """
    Return subjects available for a selected class.

    This endpoint is intended for the Teacher Assignment
    form / AJAX workflow.

    Administrator:
        Allowed.

    Manager:
        Allowed.

    Teacher:
        Not allowed to use management assignment selector.
    """

    # ========================================================
    # ACCESS
    # ========================================================

    if not can_view_teacher_management(request.user):

        return redirect(
            "student-home"
        )

    # ========================================================
    # CLASS ID
    # ========================================================

    class_id = request.GET.get(
        "class_id"
    )

    # ========================================================
    # NO CLASS SELECTED
    # ========================================================

    if not class_id:

        return render(
            request,
            "teacherapp/subject_options.html",
            {
                "subjects": [],
            },
        )

    # ========================================================
    # SELECT CLASS
    # ========================================================

    classroom = (
        ClassRoom.objects
        .filter(
            id=class_id
        )
        .first()
    )

    if not classroom:

        return render(
            request,
            "teacherapp/subject_options.html",
            {
                "subjects": [],
            },
        )

    # ========================================================
    # CLASS SUBJECT RELATION
    # ========================================================

    subject_ids = (
        ClassSubject.objects
        .filter(
            class_room=classroom,
        )
        .values_list(
            "subject_id",
            flat=True,
        )
        .distinct()
    )

    # ========================================================
    # ACTIVE SUBJECTS
    # ========================================================

    subjects = (
        Subject.objects
        .filter(
            id__in=subject_ids,
            status="Active",
        )
        .distinct()
        .order_by(
            "name"
        )
    )

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "teacherapp/subject_options.html",
        {
            "subjects": subjects,
        },
    )


# ============================================================
# TEACHER GRADES
# ============================================================

@login_required
def teacher_grades(request, assignment_id=None):
    """
    Teacher Grade Management.

    Teacher:
        Can access grades only for their own active assignment.

    Administrator:
        Can access the existing Grade Management page.

    Manager:
        Not allowed.
    """

    role = get_user_role(
        request.user
    )

    # ========================================================
    # ADMINISTRATOR
    # ========================================================

    if role == "administrator":

        from grades.views import grade_list

        return grade_list(
            request
        )

    # ========================================================
    # TEACHER ONLY
    # ========================================================

    if role != "teacher":

        messages.error(
            request,
            "You do not have permission to manage grades.",
        )

        return redirect(
            "student-home"
        )

    # ========================================================
    # ASSIGNMENT SELECTED
    # ========================================================

    if assignment_id is not None:

        assignment = get_object_or_404(
            TeacherAssignment,
            pk=assignment_id,
            teacher=request.user,
            status="Active",
        )

        from grades.views import grade_list

        query_data = request.GET.copy()

        query_data["class"] = str(
            assignment.class_room_id
        )

        request.GET = query_data

        return grade_list(
            request
        )

    # ========================================================
    # ACTIVE ASSIGNMENTS
    # ========================================================

    assignments = (
        TeacherAssignment.objects
        .filter(
            teacher=request.user,
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
    # NO ACTIVE ASSIGNMENTS
    # ========================================================

    if not assignments.exists():

        messages.warning(
            request,
            "You do not have any active class or subject assignments.",
        )

        return redirect(
            "/grades/"
        )

    # ========================================================
    # EXISTING GRADE MANAGEMENT
    # ========================================================

    from grades.views import grade_list

    return grade_list(
        request
    )


# ============================================================
# TEACHER ATTENDANCE
# ============================================================

@login_required
def teacher_attendance(request, assignment_id=None):
    """
    Teacher Attendance Management.

    Teacher:
        Can access attendance only for their own
        active TeacherAssignment.

    Administrator:
        Can access existing Attendance Management.

    Manager:
        Not allowed.
    """

    role = get_user_role(
        request.user
    )

    # ========================================================
    # ADMINISTRATOR
    # ========================================================

    if role == "administrator":

        from attendance.views import attendanceHome

        return attendanceHome(
            request
        )

    # ========================================================
    # TEACHER ONLY
    # ========================================================

    if role != "teacher":

        messages.error(
            request,
            "You do not have permission to manage attendance.",
        )

        return redirect(
            "student-home"
        )

    # ========================================================
    # ASSIGNMENT SELECTED
    # ========================================================

    if assignment_id is not None:

        assignment = get_object_or_404(
            TeacherAssignment,
            pk=assignment_id,
            teacher=request.user,
            status="Active",
        )

        from attendance.views import attendanceHome

        query_data = request.GET.copy()

        query_data["class_id"] = str(
            assignment.class_room_id
        )

        query_data["subject_id"] = str(
            assignment.subject_id
        )

        # Keep selected date if supplied.
        if not query_data.get("date"):

            from django.utils import timezone

            query_data["date"] = (
                timezone
                .localdate()
                .isoformat()
            )

        request.GET = query_data

        return attendanceHome(
            request
        )

    # ========================================================
    # ACTIVE ASSIGNMENTS
    # ========================================================

    assignments = (
        TeacherAssignment.objects
        .filter(
            teacher=request.user,
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
    # NO ACTIVE ASSIGNMENTS
    # ========================================================

    if not assignments.exists():

        messages.warning(
            request,
            "You do not have any active class or subject assignments.",
        )

        return redirect(
            "/attendance/"
        )

    # ========================================================
    # EXISTING ATTENDANCE MANAGEMENT
    # ========================================================

    from attendance.views import attendanceHome

    return attendanceHome(
        request
    )


# ============================================================
# END OF TEACHER MANAGEMENT VIEWS
# ============================================================
