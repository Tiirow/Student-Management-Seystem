# ============================================================
# GRADES VIEWS
# ============================================================

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from students.models import Student, ClassRoom
from subjects.models import Subject
from users.models import Profile
from teacherapp.models import TeacherAssignment

from .models import Grade, Semester


# ============================================================
# ROLE
# ============================================================

def get_current_role(user):
    """
    Return the logged-in user's role.
    Superuser is treated as Administrator.
    """

    if user.is_superuser:
        return "Administrator"

    try:
        return user.profile.role
    except Profile.DoesNotExist:
        return None


def is_administrator(user):
    return get_current_role(user) == "Administrator"


def is_manager(user):
    return get_current_role(user) == "Manager"


def is_teacher(user):
    return get_current_role(user) == "Teacher"


def can_manage_grades(user):
    return get_current_role(user) in [
        "Administrator",
        "Manager",
        "Teacher",
    ]


# ============================================================
# GRADE CALCULATION
# ============================================================

def calculate_letter_grade(score):

    score = Decimal(str(score))

    if score >= Decimal("90"):
        return "A+"

    elif score >= Decimal("85"):
        return "A"

    elif score >= Decimal("80"):
        return "B+"

    elif score >= Decimal("75"):
        return "B"

    elif score >= Decimal("70"):
        return "C+"

    elif score >= Decimal("60"):
        return "C"

    elif score >= Decimal("50"):
        return "D"

    return "F"


def calculate_result(score):

    score = Decimal(str(score))

    if score >= Decimal("60"):
        return "PASS"

    elif score >= Decimal("50"):
        return "RE-EXAM"

    return "FAIL"


# ============================================================
# TEACHER ASSIGNED CLASSES
# ============================================================

def get_teacher_classes(user):

    assigned_class_ids = (
        TeacherAssignment.objects
        .filter(
            teacher=user,
            status="Active",
        )
        .values_list(
            "class_room_id",
            flat=True,
        )
        .distinct()
    )

    return (
        ClassRoom.objects
        .filter(
            id__in=assigned_class_ids,
            status="Active",
        )
        .order_by(
            "name"
        )
    )


# ============================================================
# TEACHER ASSIGNED SUBJECTS
# ============================================================

def get_teacher_subjects(user, classroom):

    subject_ids = (
        TeacherAssignment.objects
        .filter(
            teacher=user,
            class_room=classroom,
            status="Active",
        )
        .values_list(
            "subject_id",
            flat=True,
        )
        .distinct()
    )

    return (
        Subject.objects
        .filter(
            id__in=subject_ids,
            status="Active",
        )
        .order_by(
            "name"
        )
    )


# ============================================================
# TEACHER CLASS ACCESS
# ============================================================

def teacher_can_access_class(
    user,
    classroom,
):

    if not classroom:
        return False

    return (
        TeacherAssignment.objects
        .filter(
            teacher=user,
            class_room=classroom,
            status="Active",
        )
        .exists()
    )


# ============================================================
# TEACHER STUDENT ACCESS
# ============================================================

def teacher_can_access_student(
    user,
    student,
):

    if not student:
        return False

    if not student.class_room_id:
        return False

    return (
        TeacherAssignment.objects
        .filter(
            teacher=user,
            class_room_id=student.class_room_id,
            status="Active",
        )
        .exists()
    )


# ============================================================
# TEACHER SUBJECT ACCESS
# ============================================================

def teacher_can_access_subject(
    user,
    classroom,
    subject,
):

    if not classroom or not subject:
        return False

    return (
        TeacherAssignment.objects
        .filter(
            teacher=user,
            class_room=classroom,
            subject=subject,
            status="Active",
        )
        .exists()
    )


# ============================================================
# GRADE LIST
# ============================================================

@login_required
def grade_list(request):

    # ========================================================
    # PERMISSION
    # ========================================================

    if not can_manage_grades(request.user):

        messages.error(
            request,
            "You do not have permission to manage grades."
        )

        return redirect("student-home")


    # ========================================================
    # ROLE
    # ========================================================

    current_role = get_current_role(
        request.user
    )

    teacher = (
        current_role == "Teacher"
    )

    administrator = (
        current_role == "Administrator"
    )

    manager = (
        current_role == "Manager"
    )


    # ========================================================
    # CLASSES
    # ========================================================

    if teacher:

        classes = get_teacher_classes(
            request.user
        )

    else:

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
    # SELECTED CLASS
    # ========================================================

    selected_class_id = (
        request.GET.get(
            "class",
            ""
        )
        .strip()
    )

    selected_class = None


    if selected_class_id:

        selected_class = (
            classes
            .filter(
                id=selected_class_id
            )
            .first()
        )


    # ========================================================
    # ALL ALLOWED STUDENTS
    #
    # IMPORTANT:
    # For Teacher we load students from all assigned
    # classes once. JavaScript will filter them when
    # the teacher selects a class.
    # ========================================================

    if teacher:

        assigned_class_ids = list(
            classes.values_list(
                "id",
                flat=True,
            )
        )

        students = (
            Student.objects
            .filter(
                class_room_id__in=assigned_class_ids
            )
            .select_related(
                "class_room",
                "user",
            )
            .order_by(
                "class_room__name",
                "first_name",
                "last_name",
            )
        )

    else:

        students = (
            Student.objects
            .select_related(
                "class_room",
                "user",
            )
            .order_by(
                "class_room__name",
                "first_name",
                "last_name",
            )
        )


    # ========================================================
    # SELECTED STUDENT
    # ========================================================

    selected_student_id = (
        request.GET.get(
            "student",
            ""
        )
        .strip()
    )

    selected_student = None


    if selected_student_id:

        selected_student = (
            students
            .filter(
                id=selected_student_id
            )
            .first()
        )


    # ========================================================
    # TEACHER VALIDATION
    # ========================================================

    if (
        teacher
        and selected_student
        and not teacher_can_access_student(
            request.user,
            selected_student,
        )
    ):

        messages.error(
            request,
            "You are not authorized to manage this student."
        )

        selected_student = None
        selected_student_id = ""


    # ========================================================
    # CLASS / STUDENT CONSISTENCY
    # ========================================================

    if (
        selected_student
        and selected_class
        and selected_student.class_room_id
        != selected_class.id
    ):

        messages.error(
            request,
            "The selected student does not belong to the selected class."
        )

        selected_student = None
        selected_student_id = ""


    # ========================================================
    # IF STUDENT SELECTED BUT CLASS EMPTY
    # ========================================================

    if (
        selected_student
        and not selected_class
    ):

        selected_class = (
            classes
            .filter(
                id=selected_student.class_room_id
            )
            .first()
        )

        if selected_class:

            selected_class_id = str(
                selected_class.id
            )


    # ========================================================
    # SEMESTERS
    # ========================================================

    semesters = (
        Semester.objects
        .filter(
            status="Active"
        )
        .order_by(
            "name"
        )
    )


    # ========================================================
    # SELECTED SEMESTER
    # ========================================================

    selected_semester = None
    selected_semester_id = ""


    if teacher:

        # ----------------------------------------------------
        # Teacher does NOT select semester.
        # System uses active semester automatically.
        # ----------------------------------------------------

        selected_semester = (
            semesters.first()
        )

        if selected_semester:

            selected_semester_id = str(
                selected_semester.id
            )

    else:

        # ----------------------------------------------------
        # Administrator / Manager
        # ----------------------------------------------------

        requested_semester_id = (
            request.GET.get(
                "semester",
                ""
            )
            .strip()
        )


        if requested_semester_id:

            selected_semester = (
                semesters
                .filter(
                    id=requested_semester_id
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


        if selected_semester:

            selected_semester_id = str(
                selected_semester.id
            )


    # ========================================================
    # SUBJECTS
    # ========================================================

    subjects = Subject.objects.none()


    if selected_class:

        if teacher:

            subjects = get_teacher_subjects(
                request.user,
                selected_class,
            )

        else:

            subjects = (
                Subject.objects
                .filter(
                    status="Active"
                )
                .order_by(
                    "name"
                )
            )


    # ========================================================
    # EXISTING GRADES
    # ========================================================

    grade_rows = Grade.objects.none()


    if (
        selected_student
        and selected_semester
    ):

        grade_rows = (
            Grade.objects
            .filter(
                student=selected_student,
                semester=selected_semester,
            )
            .select_related(
                "student",
                "subject",
                "semester",
            )
            .order_by(
                "subject__name"
            )
        )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "current_role": current_role,

        "is_teacher": teacher,

        "is_administrator": administrator,

        "is_manager": manager,

        "classes": classes,

        "students": students,

        "subjects": subjects,

        "semesters": semesters,

        "selected_class": selected_class,

        "selected_class_id": (
            str(selected_class.id)
            if selected_class
            else ""
        ),

        "selected_student": selected_student,

        "selected_student_id": (
            str(selected_student.id)
            if selected_student
            else ""
        ),

        "selected_semester": selected_semester,

        "selected_semester_id": (
            selected_semester_id
        ),

        "grade_rows": grade_rows,
    }


    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "grades/grade_list.html",
        context,
    )


# ============================================================
# SAVE GRADES
# ============================================================

@login_required
@require_POST
def save_grades(request):

    # ========================================================
    # PERMISSION
    # ========================================================

    if not can_manage_grades(
        request.user
    ):

        messages.error(
            request,
            "You do not have permission to save grades."
        )

        return redirect(
            "student-home"
        )


    # ========================================================
    # ROLE
    # ========================================================

    current_role = get_current_role(
        request.user
    )

    teacher = (
        current_role == "Teacher"
    )


    # ========================================================
    # STUDENT
    # ========================================================

    student_id = (
        request.POST.get(
            "student_id",
            ""
        )
        .strip()
    )


    if not student_id:

        messages.error(
            request,
            "Please select a student."
        )

        return redirect(
            "grade-list"
        )


    student = get_object_or_404(
        Student.objects.select_related(
            "class_room"
        ),
        pk=student_id,
    )


    # ========================================================
    # TEACHER STUDENT ACCESS
    # ========================================================

    if teacher:

        if not teacher_can_access_student(
            request.user,
            student,
        ):

            messages.error(
                request,
                "You are not authorized to manage this student."
            )

            return redirect(
                "grade-list"
            )


    # ========================================================
    # CLASS
    # ========================================================

    class_id = (
        request.POST.get(
            "class_id",
            ""
        )
        .strip()
    )


    if class_id:

        classroom = (
            ClassRoom.objects
            .filter(
                pk=class_id
            )
            .first()
        )

    else:

        classroom = (
            student.class_room
        )


    # ========================================================
    # CLASS VALIDATION
    # ========================================================

    if not classroom:

        messages.error(
            request,
            "The selected student is not assigned to a class."
        )

        return redirect(
            "grade-list"
        )


    if (
        student.class_room_id
        != classroom.id
    ):

        messages.error(
            request,
            "The selected student does not belong to the selected class."
        )

        return redirect(
            f"/grades/?class={student.class_room_id}"
            f"&student={student.id}"
        )


    # ========================================================
    # TEACHER CLASS ACCESS
    # ========================================================

    if teacher:

        if not teacher_can_access_class(
            request.user,
            classroom,
        ):

            messages.error(
                request,
                "You are not assigned to this class."
            )

            return redirect(
                "grade-list"
            )


    # ========================================================
    # SEMESTER
    # ========================================================

    if teacher:

        semester = (
            Semester.objects
            .filter(
                status="Active"
            )
            .order_by(
                "name"
            )
            .first()
        )

    else:

        semester_id = (
            request.POST.get(
                "semester_id",
                ""
            )
            .strip()
        )

        semester = (
            Semester.objects
            .filter(
                pk=semester_id,
                status="Active",
            )
            .first()
        )


    # ========================================================
    # NO SEMESTER
    # ========================================================

    if not semester:

        messages.error(
            request,
            "No active semester is available."
        )

        return redirect(
            f"/grades/?class={classroom.id}"
            f"&student={student.id}"
        )


    # ========================================================
    # SUBJECT NAMES
    # ========================================================

    subject_names = (
        request.POST.getlist(
            "subject_name"
        )
    )


    # ========================================================
    # MARKS
    # ========================================================

    marks_list = (
        request.POST.getlist(
            "marks"
        )
    )


    # ========================================================
    # VALIDATE
    # ========================================================

    if not subject_names or not marks_list:

        messages.error(
            request,
            "Please add at least one subject and marks."
        )

        return redirect(
            f"/grades/?class={classroom.id}"
            f"&student={student.id}"
        )


    # ========================================================
    # COUNTERS
    # ========================================================

    saved_count = 0
    skipped_count = 0


    # ========================================================
    # SAVE
    # ========================================================

    try:

        with transaction.atomic():

            for subject_name, marks in zip(
                subject_names,
                marks_list,
            ):

                # ------------------------------------------------
                # CLEAN
                # ------------------------------------------------

                subject_name = (
                    subject_name
                    .strip()
                )

                marks = (
                    marks
                    .strip()
                )


                # ------------------------------------------------
                # SKIP EMPTY ROW
                # ------------------------------------------------

                if not subject_name and not marks:
                    continue


                # ------------------------------------------------
                # REQUIRE BOTH
                # ------------------------------------------------

                if (
                    not subject_name
                    or not marks
                ):

                    skipped_count += 1
                    continue


                # ------------------------------------------------
                # MARKS
                # ------------------------------------------------

                try:

                    score = Decimal(
                        marks
                    )

                except (
                    InvalidOperation,
                    ValueError,
                    TypeError,
                ):

                    skipped_count += 1
                    continue


                # ------------------------------------------------
                # SCORE RANGE
                # ------------------------------------------------

                if (
                    score < Decimal("0")
                    or score > Decimal("100")
                ):

                    skipped_count += 1
                    continue


                # =================================================
                # FIND SUBJECT
                # =================================================

                subject = (
                    Subject.objects
                    .filter(
                        name__iexact=subject_name,
                        status="Active",
                    )
                    .first()
                )


                # ------------------------------------------------
                # SUBJECT MUST EXIST
                # ------------------------------------------------

                if not subject:

                    skipped_count += 1
                    continue


                # =================================================
                # TEACHER SUBJECT ACCESS
                # =================================================

                if teacher:

                    if not teacher_can_access_subject(
                        request.user,
                        classroom,
                        subject,
                    ):

                        skipped_count += 1
                        continue


                # =================================================
                # SAVE / UPDATE
                # =================================================

                Grade.objects.update_or_create(

                    student=student,

                    subject=subject,

                    semester=semester,

                    defaults={
                        "score": score,
                    },
                )


                saved_count += 1


    except Exception as error:

        messages.error(
            request,
            f"An error occurred while saving grades: {error}"
        )

        return redirect(
            f"/grades/?class={classroom.id}"
            f"&student={student.id}"
        )


    # ========================================================
    # SUCCESS
    # ========================================================

    if saved_count > 0:

        messages.success(
            request,
            f"{saved_count} subject grade(s) saved successfully."
        )


    # ========================================================
    # WARNING
    # ========================================================

    if skipped_count > 0:

        messages.warning(
            request,
            f"{skipped_count} row(s) were skipped. "
            f"Check the subject name and marks."
        )


    # ========================================================
    # NOTHING SAVED
    # ========================================================

    if saved_count == 0:

        messages.error(
            request,
            "No grades were saved."
        )


    # ========================================================
    # REDIRECT
    # ========================================================

    return redirect(
        f"/grades/?class={classroom.id}"
        f"&student={student.id}"
    )


# ============================================================
# ADD SEMESTER
# ============================================================

@login_required
@require_POST
def add_semester(request):

    # --------------------------------------------------------
    # ADMINISTRATOR ONLY
    # --------------------------------------------------------

    if not is_administrator(
        request.user
    ):

        messages.error(
            request,
            "Only the Administrator can add a semester."
        )

        return redirect(
            "grade-list"
        )


    semester_name = (
        request.POST.get(
            "semester_name",
            ""
        )
        .strip()
    )


    if not semester_name:

        messages.error(
            request,
            "Semester name is required."
        )

        return redirect(
            "grade-list"
        )


    if (
        Semester.objects
        .filter(
            name__iexact=semester_name
        )
        .exists()
    ):

        messages.error(
            request,
            "This semester already exists."
        )

        return redirect(
            "grade-list"
        )


    Semester.objects.create(
        name=semester_name,
        status="Active",
    )


    messages.success(
        request,
        f"{semester_name} added successfully."
    )


    return redirect(
        "grade-list"
    )


# ============================================================
# UPDATE GRADE
# ============================================================

@login_required
@require_POST
def update_grade(
    request,
    grade_id,
):

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not can_manage_grades(
        request.user
    ):

        messages.error(
            request,
            "You do not have permission to update grades."
        )

        return redirect(
            "student-home"
        )


    grade = get_object_or_404(
        Grade.objects.select_related(
            "student",
            "student__class_room",
            "subject",
            "semester",
        ),
        pk=grade_id,
    )


    # --------------------------------------------------------
    # TEACHER ACCESS
    # --------------------------------------------------------

    if is_teacher(
        request.user
    ):

        if not teacher_can_access_student(
            request.user,
            grade.student,
        ):

            messages.error(
                request,
                "You are not authorized to update this grade."
            )

            return redirect(
                "grade-list"
            )


        if not teacher_can_access_subject(
            request.user,
            grade.student.class_room,
            grade.subject,
        ):

            messages.error(
                request,
                "You are not authorized to update this subject."
            )

            return redirect(
                "grade-list"
            )


    # --------------------------------------------------------
    # MARKS
    # --------------------------------------------------------

    marks = (
        request.POST.get(
            "marks",
            ""
        )
        .strip()
    )


    try:

        score = Decimal(
            marks
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        messages.error(
            request,
            "Marks must be a valid number."
        )

        return redirect(
            f"/grades/?class={grade.student.class_room_id}"
            f"&student={grade.student.id}"
        )


    # --------------------------------------------------------
    # RANGE
    # --------------------------------------------------------

    if (
        score < Decimal("0")
        or score > Decimal("100")
    ):

        messages.error(
            request,
            "Marks must be between 0 and 100."
        )

        return redirect(
            f"/grades/?class={grade.student.class_room_id}"
            f"&student={grade.student.id}"
        )


    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    grade.score = score

    grade.save(
        update_fields=[
            "score",
            "updated_at",
        ]
    )


    messages.success(
        request,
        "Grade updated successfully."
    )


    return redirect(
        f"/grades/?class={grade.student.class_room_id}"
        f"&student={grade.student.id}"
    )


# ============================================================
# DELETE GRADE
# ============================================================

@login_required
@require_POST
def delete_grade(
    request,
    grade_id,
):

    # --------------------------------------------------------
    # PERMISSION
    # --------------------------------------------------------

    if not can_manage_grades(
        request.user
    ):

        messages.error(
            request,
            "You do not have permission to delete grades."
        )

        return redirect(
            "student-home"
        )


    grade = get_object_or_404(
        Grade.objects.select_related(
            "student",
            "student__class_room",
            "subject",
            "semester",
        ),
        pk=grade_id,
    )


    # --------------------------------------------------------
    # TEACHER ACCESS
    # --------------------------------------------------------

    if is_teacher(
        request.user
    ):

        if not teacher_can_access_student(
            request.user,
            grade.student,
        ):

            messages.error(
                request,
                "You are not authorized to delete this grade."
            )

            return redirect(
                "grade-list"
            )


        if not teacher_can_access_subject(
            request.user,
            grade.student.class_room,
            grade.subject,
        ):

            messages.error(
                request,
                "You are not authorized to delete this subject grade."
            )

            return redirect(
                "grade-list"
            )


    student_id = grade.student_id

    class_id = (
        grade.student.class_room_id
    )

    grade.delete()


    messages.success(
        request,
        "Grade deleted successfully."
    )


    return redirect(
        f"/grades/?class={class_id}"
        f"&student={student_id}"
    )

