
# ============================================================
# ENROLLMENT VIEWS
# ============================================================
#
# Subject & Enrollment Management
#
# This module handles:
# 1. Subject Management
# 2. Enrollment Management
# 3. Choose Class
# 4. Add Class
# 5. Choose Student
# 6. Student Enrollment Details
# 7. Choose Multiple Subjects
# 8. Save Enrollment
# 9. Enrollment Records
# 10. Change Enrollment Status
# 11. Delete Enrollment
#
# Permission System:
# - Superuser = Full Access
# - Administrator = Based on profile permissions
# - Teacher = Based on profile permissions
# - Student = Based on profile permissions
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

from django.contrib.auth.decorators import login_required

from django.db import IntegrityError, transaction

from django.http import JsonResponse

from django.views.decorators.http import require_POST

from students.models import Student, ClassRoom

from subjects.models import Subject

from .models import Enrollment


# ============================================================
# LOGIN HELPER
# ============================================================

def login_required_redirect(request):
    """
    Check whether the current user is logged in.

    If the user is not authenticated:
        Redirect to the login page.

    The current URL is stored inside ?next=
    so the user can return after login.
    """

    if not request.user.is_authenticated:

        login_url = "/users/login/"

        return redirect(
            f"{login_url}?next={request.get_full_path()}"
        )

    return None


# ============================================================
# PERMISSION HELPERS
# ============================================================

def has_permission(request, permission):
    """
    Check whether the current user has a specific permission.

    Superuser:
        Full Access.

    Profile users:
        Access depends on their Profile permissions.

    Example:
        has_permission(request, "can_manage_subjects")
    """

    # --------------------------------------------------------
    # USER MUST BE AUTHENTICATED
    # --------------------------------------------------------

    if not request.user.is_authenticated:
        return False

    # --------------------------------------------------------
    # SUPERUSER = FULL ACCESS
    # --------------------------------------------------------

    if request.user.is_superuser:
        return True

    # --------------------------------------------------------
    # GET PROFILE
    # --------------------------------------------------------

    try:
        profile = request.user.profile

    except Exception:
        return False

    # --------------------------------------------------------
    # CHECK PERMISSION
    # --------------------------------------------------------

    return getattr(
        profile,
        permission,
        False
    )


# ============================================================
# PERMISSION DENIED HELPER
# ============================================================

def permission_denied(
    request,
    message="You do not have permission to perform this action."
):
    """
    Display a permission error and return to Enrollment page.
    """

    messages.error(
        request,
        message
    )

    return redirect(
        "student-enrollment"
    )


# ============================================================
# MAIN ENROLLMENT MANAGEMENT
# ============================================================

def enrollment(request):
    """
    Main Subject & Enrollment Management page.

    URL:
        /enrollment/

    Handles:
        - Subjects
        - Classes
        - Students
        - Enrollment records
        - Student enrollment management
    """

    # --------------------------------------------------------
    # LOGIN CHECK
    # --------------------------------------------------------

    login_redirect = login_required_redirect(request)

    if login_redirect:
        return login_redirect

    # --------------------------------------------------------
    # VIEW PERMISSION
    # --------------------------------------------------------
    #
    # User can access this page if they can:
    #
    # - View students
    # - Manage subjects
    # - Manage enrollment
    #
    # Superuser automatically passes these checks.
    #

    if not (
        has_permission(request, "can_view_students")
        or has_permission(request, "can_manage_subjects")
        or has_permission(request, "can_manage_enrollment")
    ):

        return permission_denied(
            request,
            "You do not have permission to access Enrollment Management."
        )

    # ========================================================
    # CLASSES
    # ========================================================

    classes = ClassRoom.objects.filter(
        status="Active"
    ).order_by(
        "name"
    )

    # ========================================================
    # STUDENTS
    # ========================================================

    students = Student.objects.select_related(
        "class_room"
    ).order_by(
        "first_name",
        "last_name"
    )

    # ========================================================
    # ACTIVE SUBJECTS
    # ========================================================

    subjects = Subject.objects.filter(
        status="Active"
    ).order_by(
        "name"
    )

    # ========================================================
    # ALL SUBJECTS
    # ========================================================

    all_subjects = Subject.objects.all().order_by(
        "name"
    )

    # ========================================================
    # ENROLLMENTS
    # ========================================================

    enrollments = Enrollment.objects.select_related(
        "student",
        "student__class_room",
        "subject",
    ).order_by(
        "-enrolled_at"
    )

    # ========================================================
    # STATISTICS
    # ========================================================

    total_classes = ClassRoom.objects.count()

    active_classes = ClassRoom.objects.filter(
        status="Active"
    ).count()

    total_students = Student.objects.count()

    total_subjects = Subject.objects.count()

    active_subjects = Subject.objects.filter(
        status="Active"
    ).count()

    total_enrollments = Enrollment.objects.count()

    active_enrollments = Enrollment.objects.filter(
        status="Active"
    ).count()

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "classes": classes,

        "students": students,

        "subjects": subjects,

        "all_subjects": all_subjects,

        "enrollments": enrollments,

        "total_classes": total_classes,

        "active_classes": active_classes,

        "total_students": total_students,

        "total_subjects": total_subjects,

        "active_subjects": active_subjects,

        "total_enrollments": total_enrollments,

        "active_enrollments": active_enrollments,

    }

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "enrollment/enrollment_list.html",
        context
    )


# ============================================================
# CREATE CLASS
# ============================================================

@login_required
@require_POST
def create_class(request):
    """
    Create a new ClassRoom.

    Permission:
        can_manage_enrollment

    POST fields:
        name
        description
        status
    """

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request,
        "can_manage_enrollment"
    ):

        return permission_denied(
            request,
            "You do not have permission to manage classes."
        )

    # ========================================================
    # GET FORM DATA
    # ========================================================

    name = request.POST.get(
        "name",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    status = request.POST.get(
        "status",
        "Active"
    ).strip()

    # ========================================================
    # VALIDATION
    # ========================================================

    if not name:

        messages.error(
            request,
            "Class name is required."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # VALIDATE STATUS
    # ========================================================

    if status not in {
        "Active",
        "Inactive",
    }:

        status = "Active"

    # ========================================================
    # DUPLICATE CLASS CHECK
    # ========================================================

    if ClassRoom.objects.filter(
        name__iexact=name
    ).exists():

        messages.error(
            request,
            f"Class '{name}' already exists."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # CREATE CLASS
    # ========================================================

    ClassRoom.objects.create(
        name=name,
        description=description,
        status=status,
    )

    # ========================================================
    # SUCCESS
    # ========================================================

    messages.success(
        request,
        f"Class '{name}' was added successfully."
    )

    return redirect(
        "student-enrollment"
    )


# ============================================================
# CREATE SUBJECT
# ============================================================

@login_required
@require_POST
def create_subject(request):
    """
    Create a new subject.

    Permission:
        can_manage_subjects

    Required fields:
        code
        name
        description
        credit_hours
        status
    """

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request,
        "can_manage_subjects"
    ):

        return permission_denied(
            request,
            "You do not have permission to manage subjects."
        )

    # ========================================================
    # GET FORM DATA
    # ========================================================

    code = request.POST.get(
        "code",
        ""
    ).strip()

    name = request.POST.get(
        "name",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    credit_hours = request.POST.get(
        "credit_hours",
        "3"
    ).strip()

    status = request.POST.get(
        "status",
        "Active"
    ).strip()

    # ========================================================
    # VALIDATION
    # ========================================================

    if not code:

        messages.error(
            request,
            "Subject code is required."
        )

        return redirect(
            "student-enrollment"
        )

    if not name:

        messages.error(
            request,
            "Subject name is required."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # CREDIT HOURS
    # ========================================================

    try:

        credit_hours = int(
            credit_hours
        )

        if credit_hours < 1:
            raise ValueError

    except (
        ValueError,
        TypeError,
    ):

        messages.error(
            request,
            "Credit hours must be a valid positive number."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # STATUS
    # ========================================================

    if status not in {
        "Active",
        "Inactive",
    }:

        status = "Active"

    # ========================================================
    # DUPLICATE CODE
    # ========================================================

    if Subject.objects.filter(
        code__iexact=code
    ).exists():

        messages.error(
            request,
            f"Subject code '{code}' already exists."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # CREATE
    # ========================================================

    Subject.objects.create(
        code=code,
        name=name,
        description=description,
        credit_hours=credit_hours,
        status=status,
    )

    # ========================================================
    # SUCCESS
    # ========================================================

    messages.success(
        request,
        f"{name} was added successfully."
    )

    return redirect(
        "student-enrollment"
    )


# ============================================================
# UPDATE SUBJECT
# ============================================================

@login_required
@require_POST
def update_subject(request, pk):
    """
    Update an existing subject.

    Permission:
        can_manage_subjects
    """

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request,
        "can_manage_subjects"
    ):

        return permission_denied(
            request,
            "You do not have permission to edit subjects."
        )

    # ========================================================
    # GET SUBJECT
    # ========================================================

    subject = get_object_or_404(
        Subject,
        pk=pk
    )

    # ========================================================
    # GET DATA
    # ========================================================

    code = request.POST.get(
        "code",
        ""
    ).strip()

    name = request.POST.get(
        "name",
        ""
    ).strip()

    description = request.POST.get(
        "description",
        ""
    ).strip()

    credit_hours = request.POST.get(
        "credit_hours",
        "3"
    ).strip()

    status = request.POST.get(
        "status",
        "Active"
    ).strip()

    # ========================================================
    # VALIDATION
    # ========================================================

    if not code or not name:

        messages.error(
            request,
            "Subject code and name are required."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # CREDIT HOURS
    # ========================================================

    try:

        credit_hours = int(
            credit_hours
        )

        if credit_hours < 1:
            raise ValueError

    except (
        ValueError,
        TypeError,
    ):

        messages.error(
            request,
            "Credit hours must be a valid positive number."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # STATUS
    # ========================================================

    if status not in {
        "Active",
        "Inactive",
    }:

        status = "Active"

    # ========================================================
    # DUPLICATE CODE
    # ========================================================

    duplicate = Subject.objects.filter(
        code__iexact=code
    ).exclude(
        pk=subject.pk
    ).exists()

    if duplicate:

        messages.error(
            request,
            f"Subject code '{code}' already exists."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # UPDATE
    # ========================================================

    subject.code = code

    subject.name = name

    subject.description = description

    subject.credit_hours = credit_hours

    subject.status = status

    subject.save()

    # ========================================================
    # SUCCESS
    # ========================================================

    messages.success(
        request,
        f"{subject.name} was updated successfully."
    )

    return redirect(
        "student-enrollment"
    )


# ============================================================
# DELETE SUBJECT
# ============================================================

@login_required
@require_POST
def delete_subject(request, pk):
    """
    Delete an existing subject.

    Permission:
        can_manage_subjects

    Enrollment.subject uses CASCADE,
    therefore related enrollments will also be removed.
    """

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request,
        "can_manage_subjects"
    ):

        return permission_denied(
            request,
            "You do not have permission to delete subjects."
        )

    # ========================================================
    # GET SUBJECT
    # ========================================================

    subject = get_object_or_404(
        Subject,
        pk=pk
    )

    # ========================================================
    # GET NAME
    # ========================================================

    subject_name = subject.name

    # ========================================================
    # DELETE
    # ========================================================

    subject.delete()

    # ========================================================
    # SUCCESS
    # ========================================================

    messages.success(
        request,
        f"{subject_name} was deleted successfully."
    )

    return redirect(
        "student-enrollment"
    )


# ============================================================
# STUDENT ENROLLMENT DETAILS - AJAX
# ============================================================

@login_required
def student_enrollment_details(request, pk):
    """
    Return complete enrollment information for one student.

    Permission:
        can_view_students
        OR
        can_manage_enrollment

    URL:
        /enrollment/student/<id>/details/

    Returns JSON containing:
        Student name
        Student ID
        Class
        Already enrolled subjects
        Available subjects
        Total subjects
    """

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not (
        has_permission(
            request,
            "can_view_students"
        )
        or has_permission(
            request,
            "can_manage_enrollment"
        )
    ):

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "You do not have permission "
                    "to view enrollment details."
                ),
            },
            status=403
        )

    # ========================================================
    # GET STUDENT
    # ========================================================

    student = get_object_or_404(
        Student.objects.select_related(
            "class_room"
        ),
        pk=pk
    )

    # ========================================================
    # GET CURRENT ENROLLMENTS
    # ========================================================

    student_enrollments = Enrollment.objects.filter(
        student=student
    ).select_related(
        "subject"
    ).order_by(
        "subject__name"
    )

    # ========================================================
    # ACTIVE ENROLLMENTS
    # ========================================================

    active_enrollments = student_enrollments.filter(
        status="Active"
    )

    # ========================================================
    # ENROLLED SUBJECT IDS
    # ========================================================

    enrolled_subject_ids = list(
        active_enrollments.values_list(
            "subject_id",
            flat=True
        )
    )

    # ========================================================
    # ALREADY ENROLLED SUBJECTS
    # ========================================================

    enrolled_subjects = []

    for enrollment_obj in student_enrollments:

        enrolled_subjects.append(
            {
                "id": enrollment_obj.subject.id,

                "code": enrollment_obj.subject.code,

                "name": enrollment_obj.subject.name,

                "credit_hours": (
                    enrollment_obj.subject.credit_hours
                ),

                "status": enrollment_obj.status,

                "enrolled_at": (
                    enrollment_obj.enrolled_at.strftime(
                        "%Y-%m-%d"
                    )
                    if enrollment_obj.enrolled_at
                    else ""
                ),
            }
        )

    # ========================================================
    # AVAILABLE SUBJECTS
    # ========================================================

    available_subjects_queryset = Subject.objects.filter(
        status="Active"
    ).exclude(
        id__in=enrolled_subject_ids
    ).order_by(
        "name"
    )

    available_subjects = []

    for subject in available_subjects_queryset:

        available_subjects.append(
            {
                "id": subject.id,

                "code": subject.code,

                "name": subject.name,

                "credit_hours": subject.credit_hours,
            }
        )

    # ========================================================
    # CLASS INFORMATION
    # ========================================================

    if student.class_room:

        class_name = student.class_room.name

        class_id = student.class_room.id

    else:

        class_name = "No Class Assigned"

        class_id = None

    # ========================================================
    # RESPONSE
    # ========================================================

    return JsonResponse(
        {
            "success": True,

            "student": {

                "id": student.id,

                "student_id": student.student_id,

                "first_name": student.first_name,

                "last_name": student.last_name,

                "full_name": (
                    f"{student.first_name} "
                    f"{student.last_name}"
                ),

                "email": student.email,

                "class_id": class_id,

                "class_name": class_name,
            },

            "enrolled_subjects": enrolled_subjects,

            "available_subjects": available_subjects,

            "total_subjects": len(
                enrolled_subjects
            ),

            "active_subjects": len(
                [
                    item
                    for item in enrolled_subjects
                    if item["status"] == "Active"
                ]
            ),

            "available_subject_count": len(
                available_subjects
            ),
        }
    )


# ============================================================
# CREATE ENROLLMENT
# ============================================================

@login_required
@require_POST
def create_enrollment(request):
    """
    Create enrollments for one student.

    Permission:
        can_manage_enrollment

    Workflow:
        1. Choose Class
        2. Choose Student
        3. Choose multiple Subjects
        4. Save Enrollment

    POST fields:
        class_room
        student
        subjects[]
    """

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request,
        "can_manage_enrollment"
    ):

        return permission_denied(
            request,
            "You do not have permission to create enrollments."
        )

    # ========================================================
    # GET CLASS
    # ========================================================

    class_room_id = request.POST.get(
        "class_room"
    )

    # ========================================================
    # GET STUDENT
    # ========================================================

    student_id = request.POST.get(
        "student"
    )

    # ========================================================
    # GET MULTIPLE SUBJECTS
    # ========================================================

    subject_ids = request.POST.getlist(
        "subjects"
    )

    # ========================================================
    # VALIDATE CLASS
    # ========================================================

    if not class_room_id:

        messages.error(
            request,
            "Please choose a class."
        )

        return redirect(
            "student-enrollment"
        )

    class_room = get_object_or_404(
        ClassRoom,
        pk=class_room_id,
        status="Active"
    )

    # ========================================================
    # VALIDATE STUDENT
    # ========================================================

    if not student_id:

        messages.error(
            request,
            "Please choose a student."
        )

        return redirect(
            "student-enrollment"
        )

    student = get_object_or_404(
        Student,
        pk=student_id
    )

    # ========================================================
    # MAKE SURE STUDENT BELONGS TO CLASS
    # ========================================================

    if student.class_room_id != class_room.id:

        messages.error(
            request,
            "The selected student does not belong to "
            "the selected class."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # VALIDATE SUBJECTS
    # ========================================================

    if not subject_ids:

        messages.error(
            request,
            "Please choose at least one subject."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # GET ACTIVE SUBJECTS
    # ========================================================

    selected_subjects = Subject.objects.filter(
        id__in=subject_ids,
        status="Active"
    )

    if not selected_subjects.exists():

        messages.error(
            request,
            "No valid active subjects were selected."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # CREATE ENROLLMENTS
    # ========================================================

    created_count = 0

    duplicate_count = 0

    reactivated_count = 0

    # ========================================================
    # TRANSACTION
    # ========================================================

    with transaction.atomic():

        for subject in selected_subjects:

            try:

                enrollment_obj, created = (
                    Enrollment.objects.get_or_create(
                        student=student,
                        subject=subject,
                        defaults={
                            "status": "Active"
                        }
                    )
                )

                # ------------------------------------------------
                # NEW ENROLLMENT
                # ------------------------------------------------

                if created:

                    created_count += 1

                # ------------------------------------------------
                # EXISTING ENROLLMENT
                # ------------------------------------------------

                else:

                    # --------------------------------------------
                    # DROPPED → REACTIVATE
                    # --------------------------------------------

                    if enrollment_obj.status == "Dropped":

                        enrollment_obj.status = "Active"

                        enrollment_obj.save(
                            update_fields=[
                                "status",
                                "updated_at",
                            ]
                        )

                        reactivated_count += 1

                    # --------------------------------------------
                    # ALREADY ACTIVE / COMPLETED
                    # --------------------------------------------

                    else:

                        duplicate_count += 1

            except IntegrityError:

                duplicate_count += 1

    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    if created_count > 0:

        messages.success(
            request,
            f"{created_count} subject(s) enrolled successfully "
            f"for {student.first_name} {student.last_name}."
        )

    # ========================================================
    # REACTIVATED MESSAGE
    # ========================================================

    if reactivated_count > 0:

        messages.info(
            request,
            f"{reactivated_count} previously dropped subject(s) "
            f"were reactivated for "
            f"{student.first_name} {student.last_name}."
        )

    # ========================================================
    # DUPLICATES
    # ========================================================

    if duplicate_count > 0:

        messages.warning(
            request,
            f"{duplicate_count} subject(s) were already enrolled "
            f"for this student."
        )

    # ========================================================
    # NOTHING CHANGED
    # ========================================================

    if (
        created_count == 0
        and reactivated_count == 0
        and duplicate_count == 0
    ):

        messages.warning(
            request,
            "No enrollment changes were made."
        )

    # ========================================================
    # REDIRECT
    # ========================================================

    return redirect(
        "student-enrollment"
    )


# ============================================================
# UPDATE ENROLLMENT STATUS
# ============================================================

@login_required
@require_POST
def update_enrollment_status(request, pk):
    """
    Change enrollment status.

    Permission:
        can_manage_enrollment

    Available statuses:
        Active
        Dropped
        Completed
    """

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request,
        "can_manage_enrollment"
    ):

        return permission_denied(
            request,
            "You do not have permission to change enrollment status."
        )

    # ========================================================
    # GET ENROLLMENT
    # ========================================================

    enrollment_obj = get_object_or_404(
        Enrollment,
        pk=pk
    )

    # ========================================================
    # GET STATUS
    # ========================================================

    new_status = request.POST.get(
        "status",
        ""
    ).strip()

    valid_statuses = {
        "Active",
        "Dropped",
        "Completed",
    }

    # ========================================================
    # VALIDATE STATUS
    # ========================================================

    if new_status not in valid_statuses:

        messages.error(
            request,
            "Invalid enrollment status."
        )

        return redirect(
            "student-enrollment"
        )

    # ========================================================
    # UPDATE
    # ========================================================

    enrollment_obj.status = new_status

    enrollment_obj.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    # ========================================================
    # SUCCESS
    # ========================================================

    messages.success(
        request,
        "Enrollment status updated successfully."
    )

    return redirect(
        "student-enrollment"
    )


# ============================================================
# DELETE ENROLLMENT
# ============================================================

@login_required
@require_POST
def delete_enrollment(request, pk):
    """
    Delete an enrollment record.

    Permission:
        can_manage_enrollment

    This removes the subject from the student's
    enrollment records.
    """

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not has_permission(
        request,
        "can_manage_enrollment"
    ):

        return permission_denied(
            request,
            "You do not have permission to delete enrollments."
        )

    # ========================================================
    # GET ENROLLMENT
    # ========================================================

    enrollment_obj = get_object_or_404(
        Enrollment,
        pk=pk
    )

    # ========================================================
    # GET STUDENT NAME
    # ========================================================

    student_name = (
        f"{enrollment_obj.student.first_name} "
        f"{enrollment_obj.student.last_name}"
    )

    # ========================================================
    # GET SUBJECT NAME
    # ========================================================

    subject_name = enrollment_obj.subject.name

    # ========================================================
    # DELETE
    # ========================================================

    enrollment_obj.delete()

    # ========================================================
    # SUCCESS
    # ========================================================

    messages.success(
        request,
        f"{subject_name} enrollment for "
        f"{student_name} was removed successfully."
    )

    return redirect(
        "student-enrollment"
    )


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

subjectCreate = create_subject

subjectUpdate = update_subject

subjectDelete = delete_subject

enrollmentCreate = create_enrollment

enrollmentStatusUpdate = update_enrollment_status

enrollmentDelete = delete_enrollment

studentEnrollmentDetails = student_enrollment_details

classCreate = create_class

