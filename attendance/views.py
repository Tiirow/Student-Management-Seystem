# ============================================================
# ATTENDANCE VIEWS
# ============================================================

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages

from django.db import transaction

from django.db.models import Q

from django.utils import timezone

from .models import Attendance

from .forms import AttendanceForm

from students.models import (
    Student,
    ClassRoom,
)

from subjects.models import Subject

from users.models import Profile

from teacherapp.models import TeacherAssignment


# ============================================================
# LOGIN REQUIRED REDIRECT
# ============================================================

def login_required_redirect(request):
    """
    Redirect unauthenticated users to the login page.
    """

    if not request.user.is_authenticated:

        return redirect(
            f"/users/login/?next={request.get_full_path()}"
        )

    return None


# ============================================================
# ACCESS DENIED
# ============================================================

def access_denied(request):
    """
    Display the common Access Denied page.
    """

    return render(
        request,
        "users/access_denied.html",
    )


# ============================================================
# GET CURRENT ROLE
# ============================================================

def get_current_role(user):
    """
    Return the current user's system role.

    Superuser is treated as Administrator.
    """

    if user.is_superuser:
        return "Administrator"

    try:

        return user.profile.role

    except Profile.DoesNotExist:

        return "User"


# ============================================================
# MANAGEMENT ACCESS
# ============================================================

def management_required(request):
    """
    General management access.

    Allowed:
        - Administrator
        - Manager
    """

    login_redirect = login_required_redirect(
        request
    )

    if login_redirect:
        return login_redirect

    role = get_current_role(
        request.user
    )

    if role in [
        "Administrator",
        "Manager",
    ]:

        return None

    return access_denied(
        request
    )


# ============================================================
# ATTENDANCE MANAGEMENT ACCESS
# ============================================================

def attendance_management_required(request):
    """
    Attendance management access.

    Allowed:
        - Administrator
        - Manager
        - Teacher

    Student cannot manage attendance.
    """

    login_redirect = login_required_redirect(
        request
    )

    if login_redirect:
        return login_redirect

    role = get_current_role(
        request.user
    )

    if role in [
        "Administrator",
        "Manager",
        "Teacher",
    ]:

        return None

    return access_denied(
        request
    )


# ============================================================
# TEACHER CHECK
# ============================================================

def is_teacher(user):
    """
    Return True when the authenticated user is a Teacher.
    """

    return (
        get_current_role(user)
        == "Teacher"
    )


# ============================================================
# TEACHER ASSIGNMENT CHECK
# ============================================================

def teacher_has_assignment(
    request,
    class_room,
    subject,
):
    """
    Check whether the logged-in Teacher has an ACTIVE
    assignment for the specified class and subject.

    Administrator and Manager bypass this restriction.

    Returns:
        True  -> allowed
        False -> denied
    """

    role = get_current_role(
        request.user
    )

    # --------------------------------------------------------
    # ADMINISTRATOR / MANAGER
    # --------------------------------------------------------

    if role in [
        "Administrator",
        "Manager",
    ]:

        return True


    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    if role != "Teacher":

        return False


    return TeacherAssignment.objects.filter(
        teacher=request.user,
        class_room=class_room,
        subject=subject,
        status="Active",
    ).exists()


# ============================================================
# TEACHER ASSIGNED CLASSES
# ============================================================

def get_teacher_classes(request):
    """
    Return classes available to the current user.

    Administrator / Manager:
        all active classes.

    Teacher:
        only active classes assigned to that teacher.
    """

    role = get_current_role(
        request.user
    )


    # --------------------------------------------------------
    # ADMINISTRATOR / MANAGER
    # --------------------------------------------------------

    if role in [
        "Administrator",
        "Manager",
    ]:

        return (
            ClassRoom.objects
            .filter(
                status="Active"
            )
            .order_by(
                "name"
            )
        )


    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    if role == "Teacher":

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

        return (
            ClassRoom.objects
            .filter(
                status="Active",
                id__in=assigned_class_ids,
            )
            .order_by(
                "name"
            )
        )


    return ClassRoom.objects.none()


# ============================================================
# TEACHER ASSIGNED SUBJECTS
# ============================================================

def get_teacher_subjects(
    request,
    class_room=None,
):
    """
    Return subjects available to the current user.

    Administrator / Manager:
        all active subjects.

    Teacher:
        only subjects assigned to the selected class.
    """

    role = get_current_role(
        request.user
    )


    # --------------------------------------------------------
    # ADMINISTRATOR / MANAGER
    # --------------------------------------------------------

    if role in [
        "Administrator",
        "Manager",
    ]:

        return (
            Subject.objects
            .filter(
                status="Active"
            )
            .order_by(
                "name"
            )
        )


    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    if role == "Teacher":

        assignments = (
            TeacherAssignment.objects
            .filter(
                teacher=request.user,
                status="Active",
            )
        )


        if class_room:

            assignments = assignments.filter(
                class_room=class_room
            )


        assigned_subject_ids = (
            assignments
            .values_list(
                "subject_id",
                flat=True,
            )
            .distinct()
        )


        return (
            Subject.objects
            .filter(
                status="Active",
                id__in=assigned_subject_ids,
            )
            .order_by(
                "name"
            )
        )


    return Subject.objects.none()


# ============================================================
# GET LOGGED-IN STUDENT
# ============================================================

def get_logged_in_student(request):
    """
    Return the Student connected to the logged-in user.
    """

    login_redirect = login_required_redirect(
        request
    )

    if login_redirect:
        return None, login_redirect


    role = get_current_role(
        request.user
    )


    if role != "Student":

        return None, access_denied(
            request
        )


    try:

        student = (
            Student.objects
            .select_related(
                "user",
                "class_room",
            )
            .get(
                user=request.user
            )
        )


    except Student.DoesNotExist:

        messages.error(
            request,
            (
                "Your account is not connected to a student profile. "
                "Please contact the Administrator."
            ),
        )

        return None, access_denied(
            request
        )


    return student, None


# ============================================================
# ATTENDANCE HOME / DAILY ATTENDANCE
# ============================================================

def attendanceHome(request):
    """
    Teacher Daily Attendance.

    Workflow:

        Select Class
            ↓
        Select Subject
            ↓
        Select Date
            ↓
        View all students
            ↓
        Select attendance status
            ↓
        Add optional notes
            ↓
        Save Attendance

    Existing records for the selected date/class/subject
    are loaded automatically.
    """

    access = attendance_management_required(
        request
    )

    if access:
        return access


    # ========================================================
    # DATE
    # ========================================================

    selected_date = (
        request.GET
        .get(
            "date",
            "",
        )
        .strip()
    )


    if not selected_date:

        selected_date = (
            timezone
            .localdate()
            .isoformat()
        )


    # ========================================================
    # CLASS ID
    # ========================================================

    selected_class_id = (
        request.GET
        .get(
            "class_id",
            "",
        )
        .strip()
    )


    # ========================================================
    # SUBJECT ID
    # ========================================================

    selected_subject_id = (
        request.GET
        .get(
            "subject_id",
            "",
        )
        .strip()
    )


    # ========================================================
    # AVAILABLE CLASSES
    # ========================================================

    classes = get_teacher_classes(
        request
    )


    # ========================================================
    # SELECTED CLASS
    # ========================================================

    selected_class = None


    if selected_class_id:

        selected_class = (
            classes
            .filter(
                id=selected_class_id
            )
            .first()
        )


        if not selected_class:

            messages.error(
                request,
                (
                    "You do not have access "
                    "to the selected class."
                ),
            )

            selected_class_id = ""


    # ========================================================
    # AVAILABLE SUBJECTS
    # ========================================================

    subjects = get_teacher_subjects(
        request,
        selected_class,
    )


    # ========================================================
    # SELECTED SUBJECT
    # ========================================================

    selected_subject = None


    if selected_subject_id:

        selected_subject = (
            subjects
            .filter(
                id=selected_subject_id
            )
            .first()
        )


        if not selected_subject:

            messages.error(
                request,
                (
                    "You do not have access "
                    "to the selected subject."
                ),
            )

            selected_subject_id = ""


    # ========================================================
    # STUDENTS IN SELECTED CLASS
    # ========================================================

    students = Student.objects.none()


    if selected_class:

        students = (
            Student.objects
            .filter(
                class_room=selected_class
            )
            .select_related(
                "user",
                "class_room",
            )
            .order_by(
                "first_name",
                "last_name",
            )
        )


    # ========================================================
    # EXISTING ATTENDANCE
    # ========================================================

    attendance_records = Attendance.objects.none()


    if (
        selected_class
        and selected_subject
        and selected_date
    ):

        attendance_records = (
            Attendance.objects
            .filter(
                student__class_room=selected_class,
                subject=selected_subject,
                date=selected_date,
            )
            .select_related(
                "student",
                "subject",
                "student__class_room",
            )
        )


    # ========================================================
    # ATTENDANCE MAP
    # ========================================================

    attendance_map = {}


    for record in attendance_records:

        attendance_map[
            record.student_id
        ] = {
            "status": record.status,
            "notes": record.notes or "",
        }


    # ========================================================
    # STUDENT ROWS
    # ========================================================

    student_rows = []


    for student in students:

        existing_record = attendance_map.get(
            student.id
        )


        if existing_record:

            row_status = existing_record.get(
                "status",
                "Present",
            )

            row_notes = existing_record.get(
                "notes",
                "",
            )

            already_recorded = True

        else:

            row_status = "Present"

            row_notes = ""

            already_recorded = False


        student_rows.append(
            {
                "student": student,
                "status": row_status,
                "notes": row_notes,
                "already_recorded": already_recorded,
            }
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    total_records = (
        attendance_records.count()
    )


    present_count = (
        attendance_records
        .filter(
            status="Present"
        )
        .count()
    )


    absent_count = (
        attendance_records
        .filter(
            status="Absent"
        )
        .count()
    )


    late_count = (
        attendance_records
        .filter(
            status="Late"
        )
        .count()
    )


    # ========================================================
    # CURRENT ROLE
    # ========================================================

    current_role = get_current_role(
        request.user
    )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        # -----------------------------------------------
        # Classes
        # -----------------------------------------------

        "classes": classes,


        # -----------------------------------------------
        # Subjects
        # -----------------------------------------------

        "subjects": subjects,


        # -----------------------------------------------
        # Students
        # -----------------------------------------------

        "students": students,

        "student_rows": student_rows,


        # -----------------------------------------------
        # Attendance
        # -----------------------------------------------

        "attendance_records": (
            attendance_records
        ),


        # -----------------------------------------------
        # Selected
        # -----------------------------------------------

        "selected_date": (
            selected_date
        ),

        "selected_class_id": (
            selected_class_id
        ),

        "selected_subject_id": (
            selected_subject_id
        ),

        "selected_class": (
            selected_class
        ),

        "selected_subject": (
            selected_subject
        ),


        # -----------------------------------------------
        # Summary
        # -----------------------------------------------

        "total_records": (
            total_records
        ),

        "present_count": (
            present_count
        ),

        "absent_count": (
            absent_count
        ),

        "late_count": (
            late_count
        ),


        # -----------------------------------------------
        # Role
        # -----------------------------------------------

        "current_role": (
            current_role
        ),
    }


    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "attendance/attendance_home.html",
        context,
    )


# ============================================================
# SAVE DAILY ATTENDANCE
# ============================================================

@transaction.atomic
def saveAttendance(request):
    """
    Save or update daily attendance.

    Teacher must have an ACTIVE assignment
    for the selected class + subject.

    Each student receives one attendance record
    for the selected date and subject.

    Existing records are updated automatically.
    """

    access = attendance_management_required(
        request
    )

    if access:
        return access


    # ========================================================
    # METHOD
    # ========================================================

    if request.method != "POST":

        return redirect(
            "attendance-home"
        )


    # ========================================================
    # FORM DATA
    # ========================================================

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


    attendance_date = (
        request.POST
        .get(
            "date",
            "",
        )
        .strip()
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    if not class_id:

        messages.error(
            request,
            "Please select a class.",
        )

        return redirect(
            "attendance-home"
        )


    if not subject_id:

        messages.error(
            request,
            "Please select a subject.",
        )

        return redirect(
            "attendance-home"
        )


    if not attendance_date:

        messages.error(
            request,
            "Please select a date.",
        )

        return redirect(
            "attendance-home"
        )


    # ========================================================
    # CLASS
    # ========================================================

    class_room = get_object_or_404(
        ClassRoom,
        id=class_id,
        status="Active",
    )


    # ========================================================
    # SUBJECT
    # ========================================================

    subject = get_object_or_404(
        Subject,
        id=subject_id,
        status="Active",
    )


    # ========================================================
    # TEACHER AUTHORIZATION
    # ========================================================

    if not teacher_has_assignment(
        request,
        class_room,
        subject,
    ):

        messages.error(
            request,
            (
                "You are not assigned to this "
                "class and subject. "
                "Attendance cannot be recorded."
            ),
        )

        return redirect(
            (
                f"/attendance/?class_id={class_id}"
                f"&subject_id={subject_id}"
                f"&date={attendance_date}"
            )
        )


    # ========================================================
    # STUDENTS
    # ========================================================

    students = (
        Student.objects
        .filter(
            class_room=class_room
        )
        .order_by(
            "first_name",
            "last_name",
        )
    )


    # ========================================================
    # SAVE / UPDATE
    # ========================================================

    saved_count = 0


    valid_statuses = [
        "Present",
        "Absent",
        "Late",
    ]


    for student in students:

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = (
            request.POST
            .get(
                f"status_{student.id}",
                "Present",
            )
            .strip()
        )


        # ----------------------------------------------------
        # NOTES
        # ----------------------------------------------------

        notes = (
            request.POST
            .get(
                f"notes_{student.id}",
                "",
            )
            .strip()
        )


        # ----------------------------------------------------
        # VALIDATE STATUS
        # ----------------------------------------------------

        if status not in valid_statuses:

            status = "Present"


        # ----------------------------------------------------
        # CREATE OR UPDATE
        # ----------------------------------------------------

        Attendance.objects.update_or_create(

            student=student,

            subject=subject,

            date=attendance_date,

            defaults={
                "status": status,
                "notes": notes,
            },
        )


        saved_count += 1


    # ========================================================
    # SUCCESS
    # ========================================================

    messages.success(
        request,
        (
            "Daily attendance saved successfully "
            f"for {saved_count} students."
        ),
    )


    # ========================================================
    # RETURN
    # ========================================================

    return redirect(
        (
            f"/attendance/?class_id={class_id}"
            f"&subject_id={subject_id}"
            f"&date={attendance_date}"
        )
    )


# ============================================================
# ATTENDANCE RECORD LIST
# ============================================================

def attendanceList(request):
    """
    Display attendance records.

    Teacher:
        Only assigned class + subject records.

    Administrator / Manager:
        All attendance records.
    """

    access = attendance_management_required(
        request
    )

    if access:
        return access


    # ========================================================
    # BASE RECORDS
    # ========================================================

    records = (
        Attendance.objects
        .select_related(
            "student",
            "subject",
            "student__class_room",
        )
        .all()
        .order_by(
            "-date",
            "student__first_name",
            "student__last_name",
        )
    )


    # ========================================================
    # TEACHER RESTRICTION
    # ========================================================

    if is_teacher(
        request.user
    ):

        active_assignments = (
            TeacherAssignment.objects
            .filter(
                teacher=request.user,
                status="Active",
            )
        )


        # ----------------------------------------------------
        # EXACT CLASS + SUBJECT MATCHING
        # ----------------------------------------------------

        assignment_filter = Q(
            pk__in=[]
        )


        for assignment in active_assignments:

            assignment_filter |= Q(

                student__class_room_id=(
                    assignment.class_room_id
                ),

                subject_id=(
                    assignment.subject_id
                ),

            )


        # ----------------------------------------------------
        # APPLY RESTRICTION
        # ----------------------------------------------------

        records = (
            records
            .filter(
                assignment_filter
            )
            .distinct()
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


    if search:

        records = records.filter(

            Q(
                student__first_name__icontains=search
            )

            |

            Q(
                student__last_name__icontains=search
            )

            |

            Q(
                student__student_id__icontains=search
            )

            |

            Q(
                subject__name__icontains=search
            )

        )


    # ========================================================
    # CLASS FILTER
    # ========================================================

    class_id = (
        request.GET
        .get(
            "class",
            "",
        )
        .strip()
    )


    if class_id:

        # Teacher cannot bypass assigned classes
        if is_teacher(request.user):

            teacher_classes = get_teacher_classes(
                request
            )

            class_allowed = (
                teacher_classes
                .filter(
                    id=class_id
                )
                .exists()
            )

            if not class_allowed:

                records = records.none()

            else:

                records = records.filter(
                    student__class_room_id=class_id
                )

        else:

            records = records.filter(
                student__class_room_id=class_id
            )


    # ========================================================
    # STATUS FILTER
    # ========================================================

    status_filter = (
        request.GET
        .get(
            "status",
            "",
        )
        .strip()
    )


    if status_filter in [
        "Present",
        "Absent",
        "Late",
        "Excused",
    ]:

        records = records.filter(
            status=status_filter
        )


    # ========================================================
    # DATE FILTER
    # ========================================================

    date_filter = (
        request.GET
        .get(
            "date",
            "",
        )
        .strip()
    )


    if date_filter:

        records = records.filter(
            date=date_filter
        )


    # ========================================================
    # AVAILABLE CLASSES
    # ========================================================

    classes = get_teacher_classes(
        request
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    total_records = (
        records.count()
    )


    present_count = (
        records
        .filter(
            status="Present"
        )
        .count()
    )


    absent_count = (
        records
        .filter(
            status="Absent"
        )
        .count()
    )


    late_count = (
        records
        .filter(
            status="Late"
        )
        .count()
    )


    # ========================================================
    # CURRENT ROLE
    # ========================================================

    current_role = get_current_role(
        request.user
    )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "attendance_records": records,

        "classes": classes,

        "total_records": (
            total_records
        ),

        "present_count": (
            present_count
        ),

        "absent_count": (
            absent_count
        ),

        "late_count": (
            late_count
        ),

        "current_role": (
            current_role
        ),
    }


    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "attendance/attendance_list.html",
        context,
    )


# ============================================================
# EDIT ATTENDANCE
# ============================================================

def editAttendance(
    request,
    pk,
):
    """
    Edit an existing attendance record.

    Teacher:
        Can edit only records belonging to an active
        class + subject assignment.

    Administrator / Manager:
        Can edit attendance records without assignment
        restrictions.
    """

    access = attendance_management_required(
        request
    )

    if access:
        return access


    # ========================================================
    # GET RECORD
    # ========================================================

    attendance = get_object_or_404(

        Attendance.objects
        .select_related(
            "student",
            "subject",
            "student__class_room",
            "student__user",
        ),

        pk=pk,
    )


    # ========================================================
    # CLASS
    # ========================================================

    class_room = (
        attendance
        .student
        .class_room
    )


    # ========================================================
    # CLASS VALIDATION
    # ========================================================

    if not class_room:

        messages.error(
            request,
            (
                "This attendance record "
                "is not connected to a class."
            ),
        )

        return redirect(
            "attendance-list"
        )


    # ========================================================
    # TEACHER AUTHORIZATION
    # ========================================================

    if not teacher_has_assignment(
        request,
        class_room,
        attendance.subject,
    ):

        messages.error(
            request,
            (
                "You are not assigned to this "
                "class and subject. "
                "You cannot edit this attendance record."
            ),
        )

        return redirect(
            "attendance-list"
        )


    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        status = (
            request.POST
            .get(
                "status",
                "",
            )
            .strip()
        )


        notes = (
            request.POST
            .get(
                "notes",
                "",
            )
            .strip()
        )


        # ----------------------------------------------------
        # VALID STATUS
        # ----------------------------------------------------

        valid_statuses = [
            "Present",
            "Absent",
            "Late",
        ]


        if status not in valid_statuses:

            messages.error(
                request,
                "Please select a valid attendance status.",
            )


        else:

            # ------------------------------------------------
            # UPDATE
            # ------------------------------------------------

            attendance.status = status

            attendance.notes = notes


            attendance.save(
                update_fields=[
                    "status",
                    "notes",
                ]
            )


            # ------------------------------------------------
            # STUDENT NAME
            # ------------------------------------------------

            student_name = (
                f"{attendance.student.first_name} "
                f"{attendance.student.last_name}"
            ).strip()


            if not student_name:

                try:

                    student_name = (
                        attendance
                        .student
                        .user
                        .get_full_name()
                    ).strip()


                except AttributeError:

                    try:

                        student_name = (
                            attendance
                            .student
                            .user
                            .username
                        )

                    except AttributeError:

                        student_name = "Student"


            if not student_name:

                student_name = "Student"


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            messages.success(
                request,
                (
                    f"Attendance for {student_name} "
                    "was updated successfully."
                ),
            )


            return redirect(
                "attendance-list"
            )


    # ========================================================
    # CURRENT ROLE
    # ========================================================

    current_role = get_current_role(
        request.user
    )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "attendance": attendance,

        "student": attendance.student,

        "subject": attendance.subject,

        "class_room": class_room,

        "current_role": current_role,

        "status_choices": [
            "Present",
            "Absent",
            "Late",
        ],
    }


    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "attendance/attendance_edit.html",
        context,
    )


# ============================================================
# UPDATE ATTENDANCE
# ============================================================

# Compatibility alias.
#
# Any existing code that calls:
#
#     updateAttendance
#
# will use editAttendance().

updateAttendance = editAttendance


# ============================================================
# STUDENT MY ATTENDANCE
# ============================================================

def myAttendance(request):
    """
    Student can view only his/her own attendance records.
    """

    student, error_response = (
        get_logged_in_student(
            request
        )
    )


    if error_response:

        return error_response


    # ========================================================
    # RECORDS
    # ========================================================

    records = (
        Attendance.objects
        .filter(
            student=student
        )
        .select_related(
            "subject",
        )
        .order_by(
            "-date",
            "subject__name",
        )
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    total_days = (
        records.count()
    )


    present_count = (
        records
        .filter(
            status="Present"
        )
        .count()
    )


    absent_count = (
        records
        .filter(
            status="Absent"
        )
        .count()
    )


    late_count = (
        records
        .filter(
            status="Late"
        )
        .count()
    )


    attendance_percentage = 0


    if total_days > 0:

        attendance_percentage = round(

            (
                present_count
                / total_days
            ) * 100,

            2,
        )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "student": student,

        "attendance_records": records,

        "total_days": total_days,

        "present_count": present_count,

        "absent_count": absent_count,

        "late_count": late_count,

        "attendance_percentage": (
            attendance_percentage
        ),
    }


    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "attendance/my_attendance.html",
        context,
    )

