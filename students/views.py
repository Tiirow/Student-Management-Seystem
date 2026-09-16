# ============================================================
# STUDENTS VIEWS
# ============================================================
#
# Dynamic Student Management System
#
# MAIN ENTRY URL:
#     /students/
#
# INITIAL ACCESS:
#     Unauthenticated user
#         -> Login Form
#
# AFTER LOGIN:
#
#     Administrator
#         -> Management Dashboard
#
#     Manager
#         -> Management Dashboard
#
#     Teacher
#         -> Teacher Dashboard (/teacher/)
#
#     Student
#         -> Private Student Dashboard
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

from django.contrib.auth.models import User

from django.apps import apps

from django.db import transaction

from django.db.models import Count, Q

from django.utils import timezone

from .models import (
    Student,
    ClassRoom,
    ClassSubject,
)

from .forms import (
    StudentForm,
    ClassRoomForm,
)

from subjects.models import Subject

from enrollment.models import Enrollment

from users.models import Profile

from grades.models import (
    Grade,
    Semester,
)

from teacherapp.models import TeacherAssignment


# ============================================================
# LOGIN REQUIRED REDIRECT
# ============================================================

def login_required_redirect(request):
    """
    Redirect unauthenticated users to the login page.

    This helper is used by protected pages.

    Example:
        /students/list/
        /students/create/
        /students/classes/
    """

    if not request.user.is_authenticated:

        return redirect(
            f"/users/login/?next={request.get_full_path()}"
        )

    return None


# ============================================================
# NORMALIZE ROLE
# ============================================================

def get_user_role(user):
    """
    Return the authenticated user's normalized role.

    Returns lowercase values:

        administrator
        manager
        teacher
        student
        ""
    """

    if not user or not user.is_authenticated:

        return ""

    # --------------------------------------------------------
    # DJANGO SUPERUSER = ADMINISTRATOR
    # --------------------------------------------------------

    if user.is_superuser:

        return "administrator"

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    try:

        profile = user.profile

    except Profile.DoesNotExist:

        return ""

    # --------------------------------------------------------
    # ROLE
    # --------------------------------------------------------

    return str(
        profile.role or ""
    ).strip().lower()


# ============================================================
# MANAGEMENT USER CHECK
# ============================================================

def is_management_user(user):
    """
    Administrator and Manager can access
    general management pages.
    """

    role = get_user_role(user)

    return role in [
        "administrator",
        "manager",
    ]


# ============================================================
# CLASS VIEWER CHECK
# ============================================================

def is_class_viewer(user):
    """
    Users allowed to view classes:

        Administrator
        Manager
        Teacher
    """

    role = get_user_role(user)

    return role in [
        "administrator",
        "manager",
        "teacher",
    ]


# ============================================================
# TEACHER CHECK
# ============================================================

def is_teacher(user):
    """
    Check whether user is a Teacher.
    """

    return get_user_role(user) == "teacher"


# ============================================================
# ADMINISTRATOR CHECK
# ============================================================

def is_administrator(user):
    """
    Check whether user is an Administrator.
    """

    return get_user_role(user) == "administrator"


# ============================================================
# ACCESS DENIED
# ============================================================

def access_denied(request):
    """
    Display the standard Access Denied page.
    """

    return render(
        request,
        "users/access_denied.html",
    )


# ============================================================
# MANAGEMENT ACCESS REQUIRED
# ============================================================

def management_required(request):
    """
    Allow only:

        Administrator
        Manager
    """

    login_redirect = login_required_redirect(
        request
    )

    if login_redirect:

        return login_redirect

    if is_management_user(
        request.user
    ):

        return None

    return access_denied(
        request
    )


# ============================================================
# CLASS VIEW ACCESS REQUIRED
# ============================================================

def class_view_required(request):
    """
    Allow:

        Administrator
        Manager
        Teacher
    """

    login_redirect = login_required_redirect(
        request
    )

    if login_redirect:

        return login_redirect

    if is_class_viewer(
        request.user
    ):

        return None

    return access_denied(
        request
    )


# ============================================================
# STUDENT LIST VIEW ACCESS REQUIRED
# ============================================================

def student_list_view_required(request):
    """
    Allow:

        Administrator
        Manager
        Teacher

    Student cannot access the management student list.
    """

    login_redirect = login_required_redirect(
        request
    )

    if login_redirect:

        return login_redirect

    role = get_user_role(
        request.user
    )

    if role in [
        "administrator",
        "manager",
        "teacher",
    ]:

        return None

    return access_denied(
        request
    )


# ============================================================
# AUTOMATIC STUDENT ID GENERATOR
# ============================================================

def generate_next_student_id():
    """
    Generate the next unique Student ID.

    Example:

        STU001
        STU002
        STU003
    """

    students = (
        Student.objects
        .filter(
            student_id__startswith="STU"
        )
        .values_list(
            "student_id",
            flat=True,
        )
    )

    highest_number = 0

    for student_id in students:

        if not student_id:

            continue

        value = str(
            student_id
        ).strip().upper()

        if not value.startswith("STU"):

            continue

        number_part = value[3:]

        if not number_part.isdigit():

            continue

        number = int(
            number_part
        )

        if number > highest_number:

            highest_number = number

    next_number = highest_number + 1

    return f"STU{next_number:03d}"


# ============================================================
# STUDENT USERNAME VALIDATION / GENERATOR
# ============================================================

def generate_student_username(student_id=None):
    """
    Generate a unique fallback username.

    IMPORTANT:
    This username is ONLY a fallback.

    Administrator should normally enter the student's
    real username through the Add Student form.

    Student ID is NOT used as the login username.
    """

    number = None

    if student_id:

        value = str(
            student_id
        ).strip().upper()

        if value.startswith("STU"):

            number_part = value[3:]

            if number_part.isdigit():

                number = int(
                    number_part
                )

    if number is None:

        existing_usernames = (
            User.objects
            .filter(
                username__istartswith="student"
            )
            .values_list(
                "username",
                flat=True,
            )
        )

        highest_number = 0

        for username in existing_usernames:

            value = str(
                username
            ).strip().lower()

            if not value.startswith("student"):

                continue

            number_part = value[7:]

            if not number_part.isdigit():

                continue

            current_number = int(
                number_part
            )

            if current_number > highest_number:

                highest_number = current_number

        number = highest_number + 1

    username = f"student{number:03d}"

    while User.objects.filter(
        username__iexact=username
    ).exists():

        number += 1

        username = f"student{number:03d}"

    return username

# ============================================================
# PREVIEW AUTOMATIC STUDENT ID
# ============================================================

def get_student_credential_preview():

    student_id = (
        generate_next_student_id()
    )

    return {
        "student_id": student_id,
    }

# ============================================================
# GET LOGGED-IN STUDENT
# ============================================================

def get_logged_in_student(request):
    """
    Return the Student record linked to the
    authenticated Student account.

    This function is intentionally Student-only.
    """

    login_redirect = login_required_redirect(
        request
    )

    if login_redirect:

        return None, login_redirect

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    try:

        profile = request.user.profile

    except Profile.DoesNotExist:

        messages.error(
            request,
            (
                "Your account does not have a profile. "
                "Please contact the Administrator."
            ),
        )

        return None, access_denied(
            request
        )

    # --------------------------------------------------------
    # ROLE
    # --------------------------------------------------------

    role = str(
        profile.role or ""
    ).strip().lower()

    if role != "student":

        return None, access_denied(
            request
        )

    # --------------------------------------------------------
    # PRIMARY CONNECTION
    # --------------------------------------------------------

    student = (
        Student.objects
        .select_related(
            "user",
            "class_room",
        )
        .filter(
            user=request.user
        )
        .first()
    )

    if student:

        return student, None

    # --------------------------------------------------------
    # COMPATIBILITY FALLBACK
    # --------------------------------------------------------

    username = str(
        request.user.username or ""
    ).strip()

    if username:

        student = (
            Student.objects
            .select_related(
                "user",
                "class_room",
            )
            .filter(
                student_id__iexact=username
            )
            .first()
        )

        if student:

            if student.user_id is None:

                student.user = request.user

                student.save(
                    update_fields=[
                        "user"
                    ]
                )

            return student, None

    # --------------------------------------------------------
    # NO RECORD
    # --------------------------------------------------------

    messages.error(
        request,
        (
            "Your account is marked as Student, but no "
            "student record is connected to this account. "
            "Please contact the Administrator."
        ),
    )

    return None, access_denied(
        request
    )


# ============================================================
# MAIN SYSTEM ENTRY
# ============================================================

def studentHome(request):
    """
    Main system entry point.

    URL:
        http://127.0.0.1:8000/students/

    Behavior:

        Not logged in
            -> Login Form

        Administrator
            -> Main Management System

        Manager
            -> Main Management System

        Teacher
            -> Main System Page

        Student
            -> Private Student Dashboard

    Separate Teacher Dashboard:
        http://127.0.0.1:8000/teacher/
    """

    # --------------------------------------------------------
    # NOT LOGGED IN
    # --------------------------------------------------------

    if not request.user.is_authenticated:

        return render(
            request,
            "users/login.html",
            {
                "next": "/students/",
            },
        )

    # --------------------------------------------------------
    # GET ROLE
    # --------------------------------------------------------

    role = get_user_role(
        request.user
    )

    # --------------------------------------------------------
    # ADMINISTRATOR
    # --------------------------------------------------------

    if role == "administrator":

        return managementDashboard(
            request
        )

    # --------------------------------------------------------
    # MANAGER
    # --------------------------------------------------------

    if role == "manager":

        return managementDashboard(
            request
        )

    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    if role == "teacher":

        return render(
            request,
            "students/dashboard.html",
            {
                "current_role": "Teacher",

                "active_page": "dashboard",

                "students": (
                    Student.objects
                    .select_related(
                        "class_room",
                        "user",
                    )
                    .all()
                    .order_by("-id")
                ),

                "total_students": (
                    Student.objects.count()
                ),

                "recent_students": (
                    Student.objects
                    .select_related(
                        "class_room",
                        "user",
                    )
                    .all()
                    .order_by("-id")[:5]
                ),

                "classes": (
                    ClassRoom.objects
                    .annotate(
                        student_count=Count(
                            "students",
                            distinct=True,
                        ),
                        subject_count=Count(
                            "class_subjects",
                            filter=Q(
                                class_subjects__status="Active",
                                class_subjects__subject__status="Active",
                            ),
                            distinct=True,
                        ),
                    )
                    .order_by("name")
                ),

                "total_classes": (
                    ClassRoom.objects.count()
                ),

                "active_classes": (
                    ClassRoom.objects
                    .filter(
                        status="Active"
                    )
                    .count()
                ),

                "total_subjects": (
                    Subject.objects
                    .filter(
                        status="Active"
                    )
                    .count()
                ),
            },
        )

    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    if role == "student":

        return studentPortalDashboard(
            request
        )

    # --------------------------------------------------------
    # INVALID ROLE
    # --------------------------------------------------------

    messages.error(
        request,
        (
            "Your account does not have a valid system role. "
            "Please contact the Administrator."
        ),
    )

    return render(
        request,
        "users/login.html",
        {
            "next": "/students/",
        },
    )


# ============================================================
# MANAGEMENT DASHBOARD
# ============================================================

def managementDashboard(request):

    access = management_required(
        request
    )

    if access:

        return access

    # --------------------------------------------------------
    # STUDENTS
    # --------------------------------------------------------

    students = (
        Student.objects
        .select_related(
            "class_room",
            "user",
        )
        .all()
    )

    total_students = students.count()

    recent_students = (
        students
        .order_by(
            "-id"
        )[:5]
    )

    # --------------------------------------------------------
    # CLASSES
    # --------------------------------------------------------

    classes = (
        ClassRoom.objects
        .annotate(
            student_count=Count(
                "students",
                distinct=True,
            ),
            subject_count=Count(
                "class_subjects",
                filter=Q(
                    class_subjects__status="Active",
                    class_subjects__subject__status="Active",
                ),
                distinct=True,
            ),
        )
        .order_by(
            "name"
        )
    )

    total_classes = (
        ClassRoom.objects.count()
    )

    active_classes = (
        ClassRoom.objects
        .filter(
            status="Active"
        )
        .count()
    )

    # --------------------------------------------------------
    # SUBJECTS
    # --------------------------------------------------------

    total_subjects = (
        Subject.objects
        .filter(
            status="Active"
        )
        .count()
    )

    # --------------------------------------------------------
    # TEACHERS
    # --------------------------------------------------------

    total_teachers = (
        Profile.objects
        .filter(
            role__iexact="Teacher"
        )
        .count()
    )

    # --------------------------------------------------------
    # CURRENT ROLE
    # --------------------------------------------------------

    if request.user.is_superuser:

        current_role = "Administrator"

    else:

        try:

            current_role = (
                request.user.profile.role
            )

        except Profile.DoesNotExist:

            current_role = "User"

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        "current_role": current_role,

        "students": students,

        "total_students": total_students,

        "recent_students": recent_students,

        "total_teachers": total_teachers,

        "total_subjects": total_subjects,

        "classes": classes,

        "total_classes": total_classes,

        "active_classes": active_classes,
    }

    return render(
        request,
        "students/dashboard.html",
        context,
    )


# ============================================================
# PRIVATE STUDENT DASHBOARD
# ============================================================

def privateStudentDashboard(
    request,
    student=None,
):

    return studentPortalDashboard(
        request
    )


# ============================================================
# DASHBOARD COMPATIBILITY
# ============================================================

def dashboard(request):

    access = management_required(
        request
    )

    if access:

        return access

    return managementDashboard(
        request
    )


# ============================================================
# STUDENT DASHBOARD COMPATIBILITY
# ============================================================

def studentDashboard(request):

    return studentPortalDashboard(
        request
    )


# ============================================================
# STUDENT LIST
# ============================================================

def studentList(request):

    access = student_list_view_required(
        request
    )

    if access:

        return access

    students = (
        Student.objects
        .select_related(
            "class_room",
            "user",
        )
        .all()
        .order_by(
            "-id"
        )
    )

    if request.user.is_superuser:

        current_role = "Administrator"

    else:

        try:

            current_role = (
                request.user.profile.role
            )

        except Profile.DoesNotExist:

            current_role = "User"

    context = {

        "students": students,

        "current_role": current_role,

        "total_students": students.count(),

        "active_page": "students",
    }

    return render(
        request,
        "students/student_list.html",
        context,
    )


# ============================================================
# STUDENT DETAIL
# ============================================================

def studentDetail(
    request,
    pk,
):

    access = student_list_view_required(
        request
    )

    if access:

        return access

    student = get_object_or_404(
        Student.objects.select_related(
            "class_room",
            "user",
        ),
        pk=pk,
    )

    # --------------------------------------------------------
    # ENROLLMENTS
    # --------------------------------------------------------

    enrollments = (
        Enrollment.objects
        .filter(
            student=student,
            status="Active",
        )
        .select_related(
            "subject",
        )
        .order_by(
            "subject__name"
        )
    )

    # --------------------------------------------------------
    # GRADES
    # --------------------------------------------------------

    grades_queryset = (
        Grade.objects
        .filter(
            student=student,
        )
        .select_related(
            "subject",
            "semester",
        )
        .order_by(
            "-semester__id",
            "subject__name",
        )
    )

    grade_rows = []

    total_score = 0

    score_count = 0

    passed = 0

    re_exam = 0

    failed = 0

    for grade in grades_queryset:

        info = calculate_grade_info(
            grade.score
        )

        score = None

        if grade.score is not None:

            try:

                score = float(
                    grade.score
                )

                total_score += score

                score_count += 1

            except (
                TypeError,
                ValueError,
            ):

                pass

        if info["result"] == "PASS":

            passed += 1

        elif info["result"] == "RE-EXAM":

            re_exam += 1

        elif info["result"] == "FAIL":

            failed += 1

        grade_rows.append(
            {
                "grade": grade,
                "score": score,
                "letter": info["letter"],
                "result": info["result"],
            }
        )

    # --------------------------------------------------------
    # AVERAGE
    # --------------------------------------------------------

    average = None

    if score_count > 0:

        average = round(
            total_score / score_count,
            2,
        )

    # --------------------------------------------------------
    # OVERALL RESULT
    # --------------------------------------------------------

    overall_info = calculate_grade_info(
        average
    )

    overall_grade = overall_info["letter"]

    overall_result = overall_info["result"]

    # --------------------------------------------------------
    # ATTENDANCE
    # --------------------------------------------------------

    attendance = get_student_attendance_data(
        student
    )

    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    user = student.user

    account_username = ""

    account_status = "Not Connected"

    if user:

        account_username = user.username

        account_status = (
            "Active"
            if user.is_active
            else "Inactive"
        )

    # --------------------------------------------------------
    # CLASS
    # --------------------------------------------------------

    class_room = student.class_room

    # --------------------------------------------------------
    # CURRENT ROLE
    # --------------------------------------------------------

    if request.user.is_superuser:

        current_role = "Administrator"

    else:

        try:

            current_role = (
                request.user.profile.role
            )

        except Profile.DoesNotExist:

            current_role = "User"

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        "student": student,

        "user": user,

        "account_username": account_username,

        "account_status": account_status,

        "class_room": class_room,

        "enrollments": enrollments,

        "enrollment_count": enrollments.count(),

        "grades": grade_rows,

        "grade_count": len(grade_rows),

        "average": average,

        "overall_grade": overall_grade,

        "overall_result": overall_result,

        "passed": passed,

        "re_exam": re_exam,

        "failed": failed,

        "attendance_records": attendance["records"],

        "attendance_total": attendance["total"],

        "attendance_present": attendance["present"],

        "attendance_absent": attendance["absent"],

        "attendance_late": attendance["late"],

        "attendance_excused": attendance["excused"],

        "attendance_percentage": attendance["percentage"],

        "current_role": current_role,

        "active_page": "students",
    }

    return render(
        request,
        "students/student_detail.html",
        context,
    )


# ============================================================
# CLASS MANAGEMENT
# ============================================================

def classList(request):
    """
    Display Class Management.

    Administrator / Manager:
        See all classes.

    Teacher:
        See ONLY classes that are actively assigned
        to the logged-in Teacher.

    Student:
        Cannot access Class Management.
    """

    # --------------------------------------------------------
    # ACCESS CHECK
    # --------------------------------------------------------

    access = class_view_required(
        request
    )

    if access:

        return access

    # --------------------------------------------------------
    # CURRENT ROLE
    # --------------------------------------------------------

    if request.user.is_superuser:

        current_role = "Administrator"

    else:

        try:

            current_role = (
                request.user.profile.role
            )

        except Profile.DoesNotExist:

            current_role = "User"

    # --------------------------------------------------------
    # BASE CLASS QUERYSET
    # --------------------------------------------------------

    classes = (
        ClassRoom.objects
        .annotate(
            student_count=Count(
                "students",
                distinct=True,
            ),

            subject_count=Count(
                "class_subjects",
                filter=Q(
                    class_subjects__status="Active",
                    class_subjects__subject__status="Active",
                ),
                distinct=True,
            ),
        )
    )

    # --------------------------------------------------------
    # TEACHER CLASS RESTRICTION
    # --------------------------------------------------------
    #
    # Teacher sees ONLY classes where:
    #
    #     teacher = current user
    #     status  = Active
    #
    # --------------------------------------------------------

    if current_role == "Teacher":

        assigned_class_ids = (
            TeacherAssignment.objects
            .filter(
                teacher=request.user,
                status="Active",
            )
            .values_list(
                "class_room_id",
                flat=True,
            )
            .distinct()
        )

        classes = classes.filter(
            id__in=assigned_class_ids
        )

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    classes = classes.order_by(
        "name"
    )

    # --------------------------------------------------------
    # TOTAL CLASSES
    # --------------------------------------------------------

    total_classes = (
        classes.count()
    )

    # --------------------------------------------------------
    # ACTIVE CLASSES
    # --------------------------------------------------------

    active_classes = (
        classes
        .filter(
            status="Active"
        )
        .count()
    )

    # --------------------------------------------------------
    # STUDENT COUNT
    #
    # Count only students belonging to the classes
    # visible to the current user.
    # --------------------------------------------------------

    total_students = (
        Student.objects
        .filter(
            class_room__in=classes
        )
        .count()
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        "classes": classes,

        "total_classes": total_classes,

        "active_classes": active_classes,

        "total_students": total_students,

        "current_role": current_role,

    }

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render(
        request,
        "students/class_management.html",
        context,
    )


# ============================================================
# CLASS DETAIL
# ============================================================

def classDetail(
    request,
    pk,
):
    """
    Display one class and its students.

    Administrator / Manager:
        Can open any class.

    Teacher:
        Can open ONLY a class actively assigned to them.

    Teacher cannot use a direct URL to bypass
    Class Management restrictions.
    """

    # --------------------------------------------------------
    # BASIC ACCESS
    # --------------------------------------------------------

    access = class_view_required(
        request
    )

    if access:

        return access

    # --------------------------------------------------------
    # CURRENT ROLE
    # --------------------------------------------------------

    if request.user.is_superuser:

        current_role = "Administrator"

    else:

        try:

            current_role = (
                request.user.profile.role
            )

        except Profile.DoesNotExist:

            current_role = "User"

    # --------------------------------------------------------
    # GET CLASS
    # --------------------------------------------------------

    classroom = get_object_or_404(
        ClassRoom,
        pk=pk,
    )

    # --------------------------------------------------------
    # TEACHER AUTHORIZATION
    # --------------------------------------------------------
    #
    # This is the IMPORTANT backend restriction.
    #
    # Even if Teacher manually opens:
    #
    #     /students/classes/99/
    #
    # they can only continue when class 99 is actively
    # assigned to them.
    #
    # --------------------------------------------------------

    if current_role == "Teacher":

        has_assignment = (
            TeacherAssignment.objects
            .filter(
                teacher=request.user,
                class_room=classroom,
                status="Active",
            )
            .exists()
        )

        if not has_assignment:

            return access_denied(
                request
            )

    # --------------------------------------------------------
    # STUDENTS
    # --------------------------------------------------------

    students = (
        Student.objects
        .filter(
            class_room=classroom,
        )
        .select_related(
            "user",
        )
        .order_by(
            "first_name",
            "last_name",
        )
    )

    student_count = students.count()

    # --------------------------------------------------------
    # OFFICIAL CLASS SUBJECTS
    # --------------------------------------------------------

    class_subjects = (
        ClassSubject.objects
        .filter(
            class_room=classroom,
            status="Active",
            subject__status="Active",
        )
        .select_related(
            "subject",
        )
        .order_by(
            "subject__name",
        )
    )

    subject_count = class_subjects.count()

    # --------------------------------------------------------
    # ASSIGNED SUBJECT IDS
    # --------------------------------------------------------

    assigned_subject_ids = list(
        class_subjects
        .values_list(
            "subject_id",
            flat=True,
        )
    )

    # --------------------------------------------------------
    # AVAILABLE SUBJECTS
    #
    # Only Administrator / Manager may receive subjects
    # that can be added to the class curriculum.
    #
    # Teacher can VIEW the class but cannot manage curriculum.
    # --------------------------------------------------------

    available_subjects = (
        Subject.objects.none()
    )

    if current_role in [
        "Administrator",
        "Manager",
    ]:

        available_subjects = (
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

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        "classroom": classroom,

        "students": students,

        "student_count": student_count,

        "class_subjects": class_subjects,

        "subject_count": subject_count,

        "assigned_subject_ids": assigned_subject_ids,

        "available_subjects": available_subjects,

        "current_role": current_role,

    }

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render(
        request,
        "students/class_detail.html",
        context,
    )


# ============================================================
# CLASS CURRICULUM / ASSIGN SUBJECT
# ============================================================

@transaction.atomic
def classCurriculum(
    request,
    pk,
):
    """
    Add a subject to a class curriculum.

    Administrator / Manager:
        Allowed.

    Teacher:
        Not allowed.

    Student:
        Not allowed.
    """

    access = class_view_required(
        request
    )

    if access:

        return access

    classroom = get_object_or_404(
        ClassRoom,
        pk=pk,
    )

    # --------------------------------------------------------
    # POST ONLY
    # --------------------------------------------------------

    if request.method != "POST":

        return redirect(
            "class-view",
            pk=classroom.pk,
        )

    # --------------------------------------------------------
    # WRITE ACCESS
    # --------------------------------------------------------

    role = get_user_role(
        request.user
    )

    if role not in [
        "administrator",
        "manager",
    ]:

        messages.error(
            request,
            (
                "You do not have permission to assign "
                "subjects to this class."
            ),
        )

        return redirect(
            "class-view",
            pk=classroom.pk,
        )

    # --------------------------------------------------------
    # SUBJECT
    # --------------------------------------------------------

    subject_id = (
        request.POST.get(
            "subject_id"
        )
        or ""
    ).strip()

    if not subject_id:

        messages.error(
            request,
            "Please select a subject.",
        )

        return redirect(
            "class-view",
            pk=classroom.pk,
        )

    subject = get_object_or_404(
        Subject,
        pk=subject_id,
        status="Active",
    )

    # --------------------------------------------------------
    # EXISTING CLASS SUBJECT
    # --------------------------------------------------------

    class_subject = (
        ClassSubject.objects
        .filter(
            class_room=classroom,
            subject=subject,
        )
        .first()
    )

    if class_subject:

        if class_subject.status == "Active":

            messages.warning(
                request,
                (
                    f"{subject.name} is already assigned "
                    f"to {classroom.name}."
                ),
            )

            return redirect(
                "class-view",
                pk=classroom.pk,
            )

        class_subject.status = "Active"

        class_subject.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        messages.success(
            request,
            (
                f"{subject.name} was successfully "
                f"assigned to {classroom.name}."
            ),
        )

        return redirect(
            "class-view",
            pk=classroom.pk,
        )

    # --------------------------------------------------------
    # CREATE CLASS SUBJECT
    # --------------------------------------------------------

    ClassSubject.objects.create(
        class_room=classroom,
        subject=subject,
        status="Active",
    )

    messages.success(
        request,
        (
            f"{subject.name} was successfully "
            f"assigned to {classroom.name}."
        ),
    )

    return redirect(
        "class-view",
        pk=classroom.pk,
    )


# ============================================================
# REMOVE SUBJECT FROM CLASS
# ============================================================

@transaction.atomic
def removeClassSubject(
    request,
    pk,
):

    access = management_required(
        request
    )

    if access:

        return access

    class_subject = get_object_or_404(
        ClassSubject.objects.select_related(
            "class_room",
            "subject",
        ),
        id=pk,
    )

    classroom_id = (
        class_subject.class_room.id
    )

    subject_name = (
        class_subject.subject.name
    )

    if request.method != "POST":

        return redirect(
            "class-view",
            pk=classroom_id,
        )

    class_subject.delete()

    messages.success(
        request,
        (
            f"{subject_name} was removed from "
            f"the class curriculum."
        ),
    )

    return redirect(
        "class-view",
        pk=classroom_id,
    )


# ============================================================
# CREATE CLASS
# ============================================================

@transaction.atomic
def createClass(request):

    access = management_required(
        request
    )

    if access:

        return access

    if request.method == "POST":

        form = ClassRoomForm(
            request.POST
        )

        if form.is_valid():

            classroom = form.save()

            messages.success(
                request,
                (
                    f"{classroom.name} was created "
                    f"successfully."
                ),
            )

            return redirect(
                "class-list"
            )

    else:

        form = ClassRoomForm()

    return render(
        request,
        "students/class_form.html",
        {
            "form": form,
            "classroom": None,
            "page_title": "Add New Class",
            "submit_text": "Save Class",
        },
    )


# ============================================================
# UPDATE CLASS
# ============================================================

@transaction.atomic
def updateClass(
    request,
    pk,
):

    access = management_required(
        request
    )

    if access:

        return access

    classroom = get_object_or_404(
        ClassRoom,
        pk=pk,
    )

    if request.method == "POST":

        form = ClassRoomForm(
            request.POST,
            instance=classroom,
        )

        if form.is_valid():

            classroom = form.save()

            messages.success(
                request,
                (
                    f"{classroom.name} was updated "
                    f"successfully."
                ),
            )

            return redirect(
                "class-list"
            )

    else:

        form = ClassRoomForm(
            instance=classroom
        )

    return render(
        request,
        "students/class_form.html",
        {
            "form": form,
            "classroom": classroom,
            "page_title": "Edit Class",
            "submit_text": "Update Class",
        },
    )



# ============================================================
# DELETE CLASS
# ============================================================

@transaction.atomic
def deleteClass(
    request,
    pk,
):
    """
    Delete a class safely.

    IMPORTANT:
        A class cannot be deleted while students
        are still assigned to it.

    If students exist:
        Show a professional error message and
        return to the class page.

    If no students exist:
        Delete the class normally.
    """

    # --------------------------------------------------------
    # ACCESS CHECK
    # --------------------------------------------------------

    access = management_required(
        request
    )

    if access:
        return access

    # --------------------------------------------------------
    # GET CLASS
    # --------------------------------------------------------

    classroom = get_object_or_404(
        ClassRoom,
        pk=pk,
    )

    # --------------------------------------------------------
    # COUNT STUDENTS
    # --------------------------------------------------------

    student_count = (
        Student.objects
        .filter(
            class_room_id=classroom.id
        )
        .count()
    )

    # --------------------------------------------------------
    # COUNT ACTIVE SUBJECTS
    # --------------------------------------------------------

    subject_count = (
        ClassSubject.objects
        .filter(
            class_room_id=classroom.id,
            status="Active",
        )
        .count()
    )

    # ========================================================
    # POST = DELETE REQUEST
    # ========================================================

    if request.method == "POST":

        # ----------------------------------------------------
        # CHECK STUDENTS AGAIN
        # ----------------------------------------------------
        # We check again immediately before deletion
        # to prevent deleting a class that now contains
        # students.

        student_count = (
            Student.objects
            .filter(
                class_room_id=classroom.id
            )
            .count()
        )

        # ----------------------------------------------------
        # STUDENTS EXIST
        # ----------------------------------------------------

        if student_count > 0:

            messages.error(
                request,
                (
                    f"Cannot Delete Class. "
                    f"This class currently has "
                    f"{student_count} student"
                    f"{'s' if student_count != 1 else ''}. "
                    f"Please transfer or remove all students "
                    f"from this class before deleting it."
                ),
            )

            return redirect(
                "class-view",
                pk=classroom.id,
            )

        # ----------------------------------------------------
        # DELETE CLASS
        # ----------------------------------------------------

        class_name = classroom.name

        classroom.delete()

        # ----------------------------------------------------
        # SUCCESS MESSAGE
        # ----------------------------------------------------

        messages.success(
            request,
            (
                f"{class_name} was deleted "
                f"successfully."
            ),
        )

        return redirect(
            "class-list"
        )

    # ========================================================
    # DELETE CONFIRMATION PAGE
    # ========================================================

    return render(
        request,
        "students/class_confirm_delete.html",
        {
            "classroom": classroom,
            "student_count": student_count,
            "subject_count": subject_count,
        },
    )


# ============================================================
# CREATE STUDENT
# ============================================================

@transaction.atomic
def createStudent(request):

    access = management_required(
        request
    )

    if access:

        return access

    # ========================================================
    # GET
    # ========================================================

    if request.method != "POST":

        form = StudentForm()

        credential_preview = (
            get_student_credential_preview()
        )

        return render(
            request,
            "students/student_form.html",
            {
                "form": form,

                "student": None,

                "page_title": "Add New Student",

                "submit_text": "Create Student",

                # ------------------------------------------------
                # AUTOMATIC STUDENT ID
                # ------------------------------------------------

                "generated_student_id": (
                    credential_preview["student_id"]
                ),

                "student_id_preview": (
                    credential_preview["student_id"]
                ),

                # ------------------------------------------------
                # USERNAME
                # ------------------------------------------------
                #
                # Username is now entered by Administrator.
                #
                # It is NOT generated from Student ID.
                #
                "generated_username": "",

                "username_preview": "",
            },
        )

    # ========================================================
    # POST
    # ========================================================

    form = StudentForm(
        request.POST
    )

    # ========================================================
    # USERNAME
    # ========================================================
    #
    # IMPORTANT:
    #
    # Student login will use:
    #
    #     Username + Password
    #
    # NOT:
    #
    #     Student ID + Password
    #
    # ========================================================

    username = (
        request.POST.get(
            "username",
            "",
        )
        or ""
    ).strip()

    # ========================================================
    # BASIC USERNAME VALIDATION
    # ========================================================

    if not username:

        form.add_error(
            None,
            (
                "Username is required. "
                "The student will use this username "
                "to log in to the system."
            ),
        )

    elif User.objects.filter(
        username__iexact=username
    ).exists():

        form.add_error(
            None,
            (
                "This username is already in use. "
                "Please choose another username."
            ),
        )

    # ========================================================
    # FORM VALIDATION
    # ========================================================

    if not form.is_valid():

        credential_preview = (
            get_student_credential_preview()
        )

        return render(
            request,
            "students/student_form.html",
            {
                "form": form,

                "student": None,

                "page_title": "Add New Student",

                "submit_text": "Create Student",

                "generated_student_id": (
                    credential_preview["student_id"]
                ),

                "student_id_preview": (
                    credential_preview["student_id"]
                ),

                # Keep the username the Administrator
                # already typed in the form.
                "generated_username": username,

                "username_preview": username,
            },
        )

    # ========================================================
    # CLEAN DATA
    # ========================================================

    email = form.cleaned_data.get(
        "email"
    )

    first_name = form.cleaned_data.get(
        "first_name"
    )

    last_name = form.cleaned_data.get(
        "last_name"
    )

    password = form.cleaned_data.get(
        "password"
    )

    # ========================================================
    # PASSWORD VALIDATION
    # ========================================================

    if not password:

        form.add_error(
            None,
            (
                "Password is required. "
                "The student will use this password "
                "together with the username to log in."
            ),
        )

        credential_preview = (
            get_student_credential_preview()
        )

        return render(
            request,
            "students/student_form.html",
            {
                "form": form,

                "student": None,

                "page_title": "Add New Student",

                "submit_text": "Create Student",

                "generated_student_id": (
                    credential_preview["student_id"]
                ),

                "student_id_preview": (
                    credential_preview["student_id"]
                ),

                "generated_username": username,

                "username_preview": username,
            },
        )

    # ========================================================
    # EMAIL CHECK
    # ========================================================

    if email and User.objects.filter(
        email__iexact=email
    ).exists():

        form.add_error(
            "email",
            (
                "This email is already connected "
                "to another account."
            ),
        )

        credential_preview = (
            get_student_credential_preview()
        )

        return render(
            request,
            "students/student_form.html",
            {
                "form": form,

                "student": None,

                "page_title": "Add New Student",

                "submit_text": "Create Student",

                "generated_student_id": (
                    credential_preview["student_id"]
                ),

                "student_id_preview": (
                    credential_preview["student_id"]
                ),

                "generated_username": username,

                "username_preview": username,
            },
        )

    # ========================================================
    # STUDENT INSTANCE
    # ========================================================

    student = form.save(
        commit=False
    )

    # ========================================================
    # GENERATE STUDENT ID
    # ========================================================
    #
    # Student ID remains an academic/system identifier.
    #
    # Example:
    #
    #     STU001
    #     STU002
    #     STU003
    #
    # It is NOT the student's login username.
    #
    # ========================================================

    generated_student_id = (
        generate_next_student_id()
    )

    # ========================================================
    # SAFETY: STUDENT ID
    # ========================================================

    while Student.objects.filter(
        student_id__iexact=generated_student_id
    ).exists():

        generated_student_id = (
            generate_next_student_id()
        )

    # ========================================================
    # SAFETY: USERNAME
    # ========================================================

    if User.objects.filter(
        username__iexact=username
    ).exists():

        form.add_error(
            None,
            (
                "This username has just been used "
                "by another account. Please choose "
                "another username."
            ),
        )

        credential_preview = (
            get_student_credential_preview()
        )

        return render(
            request,
            "students/student_form.html",
            {
                "form": form,

                "student": None,

                "page_title": "Add New Student",

                "submit_text": "Create Student",

                "generated_student_id": (
                    credential_preview["student_id"]
                ),

                "student_id_preview": (
                    credential_preview["student_id"]
                ),

                "generated_username": username,

                "username_preview": username,
            },
        )

    # ========================================================
    # CREATE DJANGO USER
    # ========================================================
    #
    # This is the actual login account.
    #
    # Login:
    #
    #     username
    #     password
    #
    # Django automatically hashes the password.
    #
    # ========================================================

    user = User.objects.create_user(
        username=username,

        email=email or "",

        first_name=first_name or "",

        last_name=last_name or "",

        password=password,
    )

    # ========================================================
    # PROFILE
    # ========================================================

    profile, created = Profile.objects.get_or_create(
        user=user
    )

    profile.role = "Student"

    # --------------------------------------------------------
    # Student created by Administrator
    # --------------------------------------------------------
    #
    # The Student account can login normally.
    #
    # --------------------------------------------------------

    profile.is_approved = True

    profile.save()

    # ========================================================
    # CONNECT STUDENT TO USER
    # ========================================================

    student.student_id = (
        generated_student_id
    )

    student.user = user

    # Password should NEVER be stored in the Student table.
    #
    # Django User stores a secure hashed password.
    #
    student.temporary_password = ""

    student.save()

    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    messages.success(
        request,
        (
            f"Student "
            f"{student.first_name} "
            f"{student.last_name} "
            f"was created successfully. "
            f"Student ID: "
            f"{student.student_id} | "
            f"Username: "
            f"{user.username}"
        ),
    )

    # ========================================================
    # RETURN TO STUDENT LIST
    # ========================================================

    return redirect(
        "student-list"
    )
# ============================================================
# UPDATE STUDENT
# ============================================================

@transaction.atomic
def updateStudent(
    request,
    pk,
):

    access = management_required(
        request
    )

    if access:

        return access

    student = get_object_or_404(
        Student.objects.select_related(
            "user",
        ),
        pk=pk,
    )

    if request.method == "POST":

        form = StudentForm(
            request.POST,
            instance=student,
        )

        if form.is_valid():

            student = form.save(
                commit=False
            )

            user = student.user

            if user:

                user.first_name = (
                    student.first_name
                )

                user.last_name = (
                    student.last_name
                )

                user.email = (
                    student.email
                )

                password = form.cleaned_data.get(
                    "password"
                )

                if password:

                    user.set_password(
                        password
                    )

                user.save()

            student.temporary_password = ""

            student.save()

            messages.success(
                request,
                "Student updated successfully.",
            )

            return redirect(
                "student-detail",
                pk=student.id,
            )

    else:

        form = StudentForm(
            instance=student
        )

    current_username = ""

    if student.user:

        current_username = (
            student.user.username
        )

    context = {

        "form": form,

        "student": student,

        "page_title": "Edit Student",

        "submit_text": "Update Student",

        "generated_student_id": (
            student.student_id
        ),

        "student_id_preview": (
            student.student_id
        ),

        "generated_username": (
            current_username
        ),

        "username_preview": (
            current_username
        ),
    }

    return render(
        request,
        "students/student_form.html",
        context,
    )


# ============================================================
# DELETE STUDENT
# ============================================================

@transaction.atomic
def deleteStudent(
    request,
    pk,
):

    access = management_required(
        request
    )

    if access:

        return access

    student = get_object_or_404(
        Student.objects.select_related(
            "user"
        ),
        pk=pk,
    )

    if request.method == "POST":

        student_name = (
            f"{student.first_name} "
            f"{student.last_name}"
        )

        user = student.user

        student.delete()

        if user:

            user.delete()

        messages.success(
            request,
            (
                f"{student_name} was deleted "
                f"successfully."
            ),
        )

        return redirect(
            "student-list"
        )

    return render(
        request,
        "students/student_confirm_delete.html",
        {
            "student": student,
        },
    )


# ============================================================
# STUDENT ENROLLMENT
# ============================================================

def enrollment(request):

    access = management_required(
        request
    )

    if access:

        return access

    selected_class_id = (
        request.POST.get(
            "class_id"
        )
        or request.GET.get(
            "class_id"
        )
    )

    selected_student_id = (
        request.POST.get(
            "student_id"
        )
        or request.GET.get(
            "student_id"
        )
    )

    # --------------------------------------------------------
    # CLASSES
    # --------------------------------------------------------

    classes = (
        ClassRoom.objects
        .filter(
            status="Active"
        )
        .order_by(
            "name"
        )
    )

    # --------------------------------------------------------
    # STUDENTS
    # --------------------------------------------------------

    students = Student.objects.none()

    if selected_class_id:

        students = (
            Student.objects
            .filter(
                class_room_id=selected_class_id
            )
            .select_related(
                "class_room"
            )
            .order_by(
                "first_name",
                "last_name",
            )
        )

    # --------------------------------------------------------
    # SUBJECTS
    # --------------------------------------------------------

    subjects = Subject.objects.none()

    if selected_class_id:

        subjects = (
            Subject.objects
            .filter(
                status="Active",
                class_assignments__class_room_id=(
                    selected_class_id
                ),
                class_assignments__status="Active",
            )
            .distinct()
            .order_by(
                "name"
            )
        )

    # ========================================================
    # SAVE ENROLLMENT
    # ========================================================

    if request.method == "POST":

        class_id = request.POST.get(
            "class_id"
        )

        student_id = request.POST.get(
            "student_id"
        )

        subject_ids = request.POST.getlist(
            "subjects"
        )

        if not class_id:

            messages.error(
                request,
                "Please choose a class.",
            )

            return redirect(
                "student-enrollment"
            )

        if not student_id:

            messages.error(
                request,
                "Please choose a student.",
            )

            return redirect(
                f"/students/enrollment/?class_id={class_id}"
            )

        if not subject_ids:

            messages.error(
                request,
                "Please select at least one subject.",
            )

            return redirect(
                f"/students/enrollment/"
                f"?class_id={class_id}"
                f"&student_id={student_id}"
            )

        student = (
            Student.objects
            .filter(
                id=student_id,
                class_room_id=class_id,
            )
            .first()
        )

        if not student:

            messages.error(
                request,
                (
                    "The selected student does not belong "
                    "to the selected class."
                ),
            )

            return redirect(
                "student-enrollment"
            )

        selected_subjects = (
            Subject.objects
            .filter(
                id__in=subject_ids,
                status="Active",
                class_assignments__class_room_id=class_id,
                class_assignments__status="Active",
            )
            .distinct()
        )

        if not selected_subjects.exists():

            messages.error(
                request,
                (
                    "No valid subjects from this class "
                    "curriculum were selected."
                ),
            )

            return redirect(
                f"/students/enrollment/"
                f"?class_id={class_id}"
                f"&student_id={student_id}"
            )

        for subject in selected_subjects:

            enrollment_obj, created = (
                Enrollment.objects.get_or_create(
                    student=student,
                    subject=subject,
                    defaults={
                        "status": "Active",
                    },
                )
            )

            if (
                not created
                and enrollment_obj.status != "Active"
            ):

                enrollment_obj.status = "Active"

                enrollment_obj.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

        messages.success(
            request,
            "Student subjects assigned successfully.",
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # CURRENT ENROLLMENTS
    # ========================================================

    current_enrollments = (
        Enrollment.objects.none()
    )

    if selected_student_id:

        current_enrollments = (
            Enrollment.objects
            .filter(
                student_id=selected_student_id
            )
            .select_related(
                "student",
                "subject",
            )
            .order_by(
                "subject__name"
            )
        )

    context = {

        "classes": classes,

        "students": students,

        "subjects": subjects,

        "selected_class_id": selected_class_id,

        "selected_student_id": selected_student_id,

        "current_enrollments": current_enrollments,
    }

    return render(
        request,
        "students/enrollment.html",
        context,
    )


# ============================================================
# GRADE CALCULATOR
# ============================================================

def calculate_grade_info(score):

    if score is None:

        return {
            "letter": None,
            "result": "PENDING",
        }

    try:

        score = float(score)

    except (
        TypeError,
        ValueError,
    ):

        return {
            "letter": None,
            "result": "PENDING",
        }

    if score >= 90:

        letter = "A+"

    elif score >= 85:

        letter = "A"

    elif score >= 80:

        letter = "B+"

    elif score >= 75:

        letter = "B"

    elif score >= 70:

        letter = "C+"

    elif score >= 60:

        letter = "C"

    elif score >= 50:

        letter = "D"

    else:

        letter = "F"

    if score >= 60:

        result = "PASS"

    elif score >= 50:

        result = "RE-EXAM"

    else:

        result = "FAIL"

    return {
        "letter": letter,
        "result": result,
    }


# ============================================================
# STUDENT ATTENDANCE HELPER
# ============================================================

def get_student_attendance_data(student):

    empty = {

        "records": [],

        "total": 0,

        "present": 0,

        "absent": 0,

        "late": 0,

        "excused": 0,

        "percentage": 0,

        "present_percentage": 0,

        "absent_percentage": 0,

        "late_percentage": 0,
    }

    try:

        Attendance = apps.get_model(
            "attendance",
            "Attendance",
        )

    except LookupError:

        return empty

    field_names = {
        field.name
        for field in Attendance._meta.get_fields()
        if hasattr(field, "name")
    }

    if "student" not in field_names:

        return empty

    # --------------------------------------------------------
    # DATE FIELD
    # --------------------------------------------------------

    date_field = None

    for candidate in [
        "date",
        "attendance_date",
        "day",
    ]:

        if candidate in field_names:

            date_field = candidate

            break

    # --------------------------------------------------------
    # STATUS FIELD
    # --------------------------------------------------------

    status_field = None

    for candidate in [
        "status",
        "attendance_status",
    ]:

        if candidate in field_names:

            status_field = candidate

            break

    # --------------------------------------------------------
    # SUBJECT FIELD
    # --------------------------------------------------------

    subject_field = None

    if "subject" in field_names:

        subject_field = "subject"

    # --------------------------------------------------------
    # QUERYSET
    # --------------------------------------------------------

    queryset = (
        Attendance.objects
        .filter(
            student=student
        )
    )

    if date_field:

        queryset = queryset.order_by(
            f"-{date_field}"
        )

    else:

        queryset = queryset.order_by(
            "-id"
        )

    # --------------------------------------------------------
    # COUNTERS
    # --------------------------------------------------------

    total = 0

    present = 0

    absent = 0

    late = 0

    excused = 0

    records = []

    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    for attendance in queryset:

        total += 1

        raw_status = ""

        if status_field:

            raw_status = getattr(
                attendance,
                status_field,
                "",
            )

        status_text = str(
            raw_status or ""
        ).strip()

        normalized = status_text.lower()

        if normalized in [
            "present",
            "p",
        ]:

            present += 1

            display_status = "Present"

        elif normalized in [
            "absent",
            "a",
        ]:

            absent += 1

            display_status = "Absent"

        elif normalized in [
            "late",
            "l",
        ]:

            late += 1

            display_status = "Late"

        elif normalized in [
            "excused",
            "e",
        ]:

            excused += 1

            display_status = "Excused"

        else:

            display_status = (
                status_text
                if status_text
                else "Recorded"
            )

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        record_date = None

        if date_field:

            record_date = getattr(
                attendance,
                date_field,
                None,
            )

        # ----------------------------------------------------
        # SUBJECT
        # ----------------------------------------------------

        subject_name = "General"

        if subject_field:

            subject_obj = getattr(
                attendance,
                subject_field,
                None,
            )

            if subject_obj:

                subject_name = str(
                    subject_obj
                )

        records.append(
            {
                "date": record_date,

                "subject_name": subject_name,

                "status": display_status,
            }
        )

    # --------------------------------------------------------
    # PERCENTAGES
    # --------------------------------------------------------

    percentage = 0

    present_percentage = 0

    absent_percentage = 0

    late_percentage = 0

    if total > 0:

        present_percentage = round(
            (present / total) * 100,
            1,
        )

        absent_percentage = round(
            (absent / total) * 100,
            1,
        )

        late_percentage = round(
            (late / total) * 100,
            1,
        )

        percentage = present_percentage

    return {

        "records": records,

        "total": total,

        "present": present,

        "absent": absent,

        "late": late,

        "excused": excused,

        "percentage": percentage,

        "present_percentage": present_percentage,

        "absent_percentage": absent_percentage,

        "late_percentage": late_percentage,
    }


# ============================================================
# STUDENT PORTAL DASHBOARD
# ============================================================

def studentPortalDashboard(request):

    student, error_response = (
        get_logged_in_student(
            request
        )
    )

    if error_response:

        return error_response

    class_room = student.class_room

    # --------------------------------------------------------
    # CLASS SUBJECTS
    # --------------------------------------------------------

    if class_room:

        class_subjects = (
            ClassSubject.objects
            .filter(
                class_room=class_room,
                status="Active",
                subject__status="Active",
            )
            .select_related(
                "subject",
            )
            .order_by(
                "subject__name"
            )
        )

    else:

        class_subjects = (
            ClassSubject.objects.none()
        )

    # --------------------------------------------------------
    # ENROLLMENTS
    # --------------------------------------------------------

    enrollments = (
        Enrollment.objects
        .filter(
            student=student,
            status="Active",
        )
        .select_related(
            "subject",
        )
        .order_by(
            "subject__name"
        )
    )

    # --------------------------------------------------------
    # GRADES
    # --------------------------------------------------------

    grades = (
        Grade.objects
        .filter(
            student=student,
        )
        .select_related(
            "subject",
            "semester",
        )
        .order_by(
            "-semester__id",
            "subject__name",
        )
    )

    grade_rows = []

    total_score = 0

    score_count = 0

    passed = 0

    re_exam = 0

    failed = 0

    for grade in grades:

        info = calculate_grade_info(
            grade.score
        )

        score = None

        if grade.score is not None:

            try:

                score = float(
                    grade.score
                )

                total_score += score

                score_count += 1

            except (
                TypeError,
                ValueError,
            ):

                pass

        if info["result"] == "PASS":

            passed += 1

        elif info["result"] == "RE-EXAM":

            re_exam += 1

        elif info["result"] == "FAIL":

            failed += 1

        grade_rows.append(
            {
                "grade": grade,

                "score": score,

                "letter": info["letter"],

                "result": info["result"],
            }
        )

    # --------------------------------------------------------
    # AVERAGE
    # --------------------------------------------------------

    average = None

    if score_count > 0:

        average = round(
            total_score / score_count,
            2,
        )

    # --------------------------------------------------------
    # OVERALL GRADE
    # --------------------------------------------------------

    overall_grade = None

    overall_result = None

    if average is not None:

        overall_info = calculate_grade_info(
            average
        )

        overall_grade = (
            overall_info["letter"]
        )

        overall_result = (
            overall_info["result"]
        )

    # --------------------------------------------------------
    # ATTENDANCE
    # --------------------------------------------------------

    attendance = get_student_attendance_data(
        student
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        "student": student,

        "class_room": class_room,

        "class_subjects": class_subjects,

        "enrollments": enrollments,

        "grades": grade_rows[:5],

        "subject_count": (
            class_subjects.count()
        ),

        "average": average,

        "overall_grade": overall_grade,

        "overall_result": overall_result,

        "passed": passed,

        "re_exam": re_exam,

        "failed": failed,

        "attendance_percentage": (
            attendance["percentage"]
        ),

        "attendance_present": (
            attendance["present"]
        ),

        "attendance_absent": (
            attendance["absent"]
        ),

        "attendance_late": (
            attendance["late"]
        ),

        "active_page": "dashboard",
    }

    return render(
        request,
        "students/student_dashboard.html",
        context,
    )


# ============================================================
# STUDENT MY CLASS
# ============================================================

def studentClass(request):

    student, error_response = (
        get_logged_in_student(
            request
        )
    )

    if error_response:

        return error_response

    class_room = student.class_room

    if class_room:

        class_subjects = (
            ClassSubject.objects
            .filter(
                class_room=class_room,
                status="Active",
                subject__status="Active",
            )
            .select_related(
                "subject"
            )
            .order_by(
                "subject__name"
            )
        )

        academic_year = getattr(
            class_room,
            "academic_year",
            timezone.now().year,
        )

    else:

        class_subjects = (
            ClassSubject.objects.none()
        )

        academic_year = timezone.now().year

    context = {

        "student": student,

        "class_room": class_room,

        "academic_year": academic_year,

        "class_subjects": class_subjects,

        "subject_count": (
            class_subjects.count()
        ),

        "active_page": "class",
    }

    return render(
        request,
        "students/student_class.html",
        context,
    )


# ============================================================
# STUDENT MY SUBJECTS
# ============================================================

def studentSubjects(request):

    student, error_response = (
        get_logged_in_student(
            request
        )
    )

    if error_response:

        return error_response

    class_room = student.class_room

    if class_room:

        class_subjects = (
            ClassSubject.objects
            .filter(
                class_room=class_room,
                status="Active",
                subject__status="Active",
            )
            .select_related(
                "subject"
            )
            .order_by(
                "subject__name"
            )
        )

    else:

        class_subjects = (
            ClassSubject.objects.none()
        )

    enrolled_subject_ids = set(
        Enrollment.objects
        .filter(
            student=student,
            status="Active",
        )
        .values_list(
            "subject_id",
            flat=True,
        )
    )

    subject_rows = []

    for class_subject in class_subjects:

        subject_rows.append(
            {
                "subject": class_subject.subject,

                "enrolled": (
                    class_subject.subject_id
                    in enrolled_subject_ids
                ),
            }
        )

    context = {

        "student": student,

        "class_room": class_room,

        "subject_rows": subject_rows,

        "subject_count": len(
            subject_rows
        ),

        "active_page": "subjects",
    }

    return render(
        request,
        "students/student_subjects.html",
        context,
    )


# ============================================================
# STUDENT MY GRADES
# ============================================================

def studentGrades(request):
    """
    Student-only Grades page.

    Teacher/Admin/Manager:
        Redirect to Grade Management.

    Student:
        View own grades only.
    """

    login_redirect = login_required_redirect(
        request
    )

    if login_redirect:

        return login_redirect

    role = get_user_role(
        request.user
    )

    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    if role == "teacher":

        return redirect(
            "/grades/"
        )

    # --------------------------------------------------------
    # ADMINISTRATOR
    # --------------------------------------------------------

    if role == "administrator":

        return redirect(
            "/grades/"
        )

    # --------------------------------------------------------
    # MANAGER
    # --------------------------------------------------------

    if role == "manager":

        return redirect(
            "/grades/"
        )

    # --------------------------------------------------------
    # ONLY STUDENT
    # --------------------------------------------------------

    if role != "student":

        return access_denied(
            request
        )

    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    student, error_response = (
        get_logged_in_student(
            request
        )
    )

    if error_response:

        return error_response

    # --------------------------------------------------------
    # SEMESTERS
    # --------------------------------------------------------

    semesters = (
        Semester.objects
        .filter(
            status="Active"
        )
        .order_by(
            "name"
        )
    )

    selected_semester_name = (
        request.GET.get(
            "semester",
            "",
        ).strip()
    )

    selected_semester = None

    if selected_semester_name:

        selected_semester = (
            semesters
            .filter(
                name=selected_semester_name
            )
            .first()
        )

    if (
        selected_semester is None
        and semesters.exists()
    ):

        selected_semester = (
            semesters.first()
        )

        selected_semester_name = (
            selected_semester.name
        )

    # --------------------------------------------------------
    # GRADES
    # --------------------------------------------------------

    grades = Grade.objects.none()

    if selected_semester:

        grades = (
            Grade.objects
            .filter(
                student=student,
                semester=selected_semester,
            )
            .select_related(
                "subject",
                "semester",
            )
            .order_by(
                "subject__name"
            )
        )

    # --------------------------------------------------------
    # ROWS
    # --------------------------------------------------------

    rows = []

    scores = []

    for grade in grades:

        info = calculate_grade_info(
            grade.score
        )

        score = None

        if grade.score is not None:

            try:

                score = float(
                    grade.score
                )

                scores.append(
                    score
                )

            except (
                TypeError,
                ValueError,
            ):

                pass

        rows.append(
            {
                "grade": grade,

                "score": score,

                "letter": info["letter"],

                "result": info["result"],
            }
        )

    # --------------------------------------------------------
    # AVERAGE
    # --------------------------------------------------------

    average = None

    if scores:

        average = round(
            sum(scores) / len(scores),
            2,
        )

    overall_info = calculate_grade_info(
        average
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        "student": student,

        "semesters": semesters,

        "selected_semester": (
            selected_semester_name
        ),

        "rows": rows,

        "average": average,

        "overall_grade": (
            overall_info["letter"]
        ),

        "overall_result": (
            overall_info["result"]
        ),

        "active_page": "grades",
    }

    return render(
        request,
        "students/student_grades.html",
        context,
    )


# ============================================================
# STUDENT MY RESULTS
# ============================================================

def studentResults(request):

    student, error_response = (
        get_logged_in_student(
            request
        )
    )

    if error_response:

        return error_response

    semesters = (
        Semester.objects
        .filter(
            status="Active"
        )
        .order_by(
            "name"
        )
    )

    selected_semester_name = (
        request.GET.get(
            "semester",
            "",
        ).strip()
    )

    selected_semester = None

    if selected_semester_name:

        selected_semester = (
            semesters
            .filter(
                name=selected_semester_name
            )
            .first()
        )

    if (
        selected_semester is None
        and semesters.exists()
    ):

        selected_semester = (
            semesters.first()
        )

        selected_semester_name = (
            selected_semester.name
        )

    grades = Grade.objects.none()

    if selected_semester:

        grades = (
            Grade.objects
            .filter(
                student=student,
                semester=selected_semester,
            )
            .select_related(
                "subject",
            )
            .order_by(
                "subject__name"
            )
        )

    rows = []

    scores = []

    passed = 0

    re_exam = 0

    failed = 0

    for grade in grades:

        info = calculate_grade_info(
            grade.score
        )

        score = None

        if grade.score is not None:

            try:

                score = float(
                    grade.score
                )

                scores.append(
                    score
                )

            except (
                TypeError,
                ValueError,
            ):

                pass

        if info["result"] == "PASS":

            passed += 1

        elif info["result"] == "RE-EXAM":

            re_exam += 1

        elif info["result"] == "FAIL":

            failed += 1

        rows.append(
            {
                "grade": grade,

                "score": score,

                "letter": info["letter"],

                "result": info["result"],
            }
        )

    average = None

    if scores:

        average = round(
            sum(scores) / len(scores),
            2,
        )

    overall_info = calculate_grade_info(
        average
    )

    context = {

        "student": student,

        "semesters": semesters,

        "selected_semester": (
            selected_semester_name
        ),

        "rows": rows,

        "average": average,

        "overall_grade": (
            overall_info["letter"]
        ),

        "overall_result": (
            overall_info["result"]
        ),

        "passed": passed,

        "re_exam": re_exam,

        "failed": failed,

        "active_page": "results",
    }

    return render(
        request,
        "students/student_results.html",
        context,
    )


# ============================================================
# STUDENT MY ATTENDANCE
# ============================================================

def studentAttendance(request):
    """
    Student-only Attendance page.

    Teacher/Admin/Manager:
        Redirect to Attendance Management.

    Student:
        View own attendance only.
    """

    login_redirect = login_required_redirect(
        request
    )

    if login_redirect:

        return login_redirect

    role = get_user_role(
        request.user
    )

    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    if role == "teacher":

        return redirect(
            "/attendance/"
        )

    # --------------------------------------------------------
    # ADMINISTRATOR
    # --------------------------------------------------------

    if role == "administrator":

        return redirect(
            "/attendance/"
        )

    # --------------------------------------------------------
    # MANAGER
    # --------------------------------------------------------

    if role == "manager":

        return redirect(
            "/attendance/"
        )

    # --------------------------------------------------------
    # ONLY STUDENT
    # --------------------------------------------------------

    if role != "student":

        return access_denied(
            request
        )

    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    student, error_response = (
        get_logged_in_student(
            request
        )
    )

    if error_response:

        return error_response

    attendance = get_student_attendance_data(
        student
    )

    context = {

        "student": student,

        "attendance_records": (
            attendance["records"]
        ),

        "attendance_total": (
            attendance["total"]
        ),

        "attendance_present": (
            attendance["present"]
        ),

        "attendance_absent": (
            attendance["absent"]
        ),

        "attendance_late": (
            attendance["late"]
        ),

        "attendance_excused": (
            attendance["excused"]
        ),

        "attendance_percentage": (
            attendance["percentage"]
        ),

        "present_percentage": (
            attendance["present_percentage"]
        ),

        "absent_percentage": (
            attendance["absent_percentage"]
        ),

        "late_percentage": (
            attendance["late_percentage"]
        ),

        "active_page": "attendance",
    }

    return render(
        request,
        "students/student_attendance.html",
        context,
    )


# ============================================================
# STUDENT MY PROFILE
# ============================================================

def studentProfile(request):

    student, error_response = (
        get_logged_in_student(
            request
        )
    )

    if error_response:

        return error_response

    user = student.user

    context = {

        "student": student,

        "user": user,

        "active_page": "profile",
    }

    return render(
        request,
        "students/student_profile.html",
        context,
    )

# ============================================================
# STUDENT CREDENTIALS
# ============================================================
#
# Compatibility route:
#
#     /students/credentials/
#
# IMPORTANT:
#
# Student login uses:
#
#     Username + Password
#
# Student ID is NOT the login username.
#
# Password is never displayed or stored as plaintext.
#
# This route is kept for compatibility with existing links.
# ============================================================

def studentCredentials(request):

    student, error_response = (
        get_logged_in_student(
            request
        )
    )

    if error_response:

        return error_response

    return redirect(
        "student-profile"
    )


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

studentCreate = createStudent

studentUpdate = updateStudent

studentDelete = deleteStudent



    