# ============================================================
# USERS VIEWS
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from .models import Profile, LoginAttempt
from students.models import Student, ClassRoom
from subjects.models import Subject
from teacherapp.models import TeacherAssignment


# ============================================================
# OPTIONAL AUDIT LOG
# ============================================================

try:
    from system_logs.models import AuditLog
except ImportError:
    AuditLog = None


# ============================================================
# CONSTANTS
# ============================================================

VALID_ROLES = [
    "Administrator",
    "Manager",
    "Teacher",
    "Student",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_client_ip(request):
    """
    Get the client's IP address.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    return ip


def get_user_profile(user):
    """
    Safely get user's Profile.
    """
    try:
        return user.profile
    except Profile.DoesNotExist:
        return None


def is_user_approved(user):
    """
    Check whether user is approved.
    """
    if user.is_superuser:
        return True

    profile = get_user_profile(user)

    if not profile:
        return False

    return profile.is_approved


def access_denied(request, message=None):
    """
    Render access denied page.
    """
    return render(
        request,
        "users/access_denied.html",
        {
            "message": message
            or "Ma lihid permission aad ku samayn karto shaqadan."
        },
        status=403,
    )


def create_login_audit_log(
    user,
    action,
    request,
    description="",
):
    """
    Create optional audit log.
    """
    if AuditLog is None:
        return

    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            description=description,
            ip_address=get_client_ip(request),
        )
    except Exception:
        # Audit log should never break login/logout.
        pass


def has_management_access(user):
    """
    Check whether user can access management pages.
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    profile = get_user_profile(user)

    if not profile:
        return False

    if not profile.is_approved:
        return False

    return profile.role in [
        "Administrator",
        "Manager",
    ]


def has_user_management_access(user):
    """
    Check whether user can manage users.
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    profile = get_user_profile(user)

    if not profile:
        return False

    if not profile.is_approved:
        return False

    return (
        profile.role == "Administrator"
        and profile.can_manage_users
    )


def get_post_id(request, *names):
    """
    Get ID from POST using multiple possible field names.
    This keeps backward compatibility with existing templates.
    """
    for name in names:
        value = request.POST.get(name)

        if value:
            return value

    return None


# ============================================================
# REGISTER USER
# ============================================================

@require_http_methods(["GET", "POST"])
def registerUser(request):

    # --------------------------------------------------------
    # Already logged in
    # --------------------------------------------------------

    if request.user.is_authenticated:

        if request.user.is_superuser:
            return redirect("student-home")

        profile = get_user_profile(request.user)

        if profile:

            if profile.role == "Teacher":
                return redirect("teacherapp:teacher-dashboard")

            if profile.role == "Student":
                return redirect("student-dashboard")

            if profile.role in [
                "Administrator",
                "Manager",
            ]:
                return redirect("student-home")

        return redirect("student-home")

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        confirm_password = request.POST.get(
            "confirm_password",
            "",
        )

        errors = []

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not username:
            errors.append("Username waa required.")

        if not password:
            errors.append("Password waa required.")

        if password != confirm_password:
            errors.append("Passwords-ku isma laha.")

        if User.objects.filter(
            username=username
        ).exists():
            errors.append(
                "Username-kan hore ayaa loo isticmaalay."
            )

        if email and User.objects.filter(
            email=email
        ).exists():
            errors.append(
                "Email-kan hore ayaa loo isticmaalay."
            )

        # ----------------------------------------------------
        # Errors
        # ----------------------------------------------------

        if errors:

            return render(
                request,
                "users/register.html",
                {
                    "errors": errors,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                },
            )

        # ----------------------------------------------------
        # Create User
        # ----------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # ----------------------------------------------------
        # Create Profile
        # ----------------------------------------------------

        Profile.objects.create(
            user=user,
            role="Student",
            is_approved=False,
        )

        return render(
            request,
            "users/login.html",
            {
                "success_message": (
                    "Registration successful. "
                    "Account-kaaga wuxuu sugayaa "
                    "Administrator approval."
                )
            },
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    return render(
        request,
        "users/register.html",
    )


# ============================================================
# LOGIN USER
# ============================================================

@require_http_methods(["GET", "POST"])
def loginUser(request):

    # --------------------------------------------------------
    # Already logged in
    # --------------------------------------------------------

    if request.user.is_authenticated:

        if request.user.is_superuser:
            return redirect("student-home")

        profile = get_user_profile(request.user)

        if profile:

            if profile.role == "Teacher":
                return redirect("teacherapp:teacher-dashboard")

            if profile.role == "Student":
                return redirect("student-dashboard")

            if profile.role in [
                "Administrator",
                "Manager",
            ]:
                return redirect("student-home")

        return redirect("student-home")

    # --------------------------------------------------------
    # POST LOGIN
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        next_url = request.POST.get(
            "next",
            "",
        ).strip()

        # ----------------------------------------------------
        # Authenticate
        # ----------------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        # ----------------------------------------------------
        # Invalid login
        # ----------------------------------------------------

        if user is None:

            LoginAttempt.objects.create(
                username=username,
                ip_address=get_client_ip(request),
            )

            create_login_audit_log(
                None,
                "LOGIN_FAILED",
                request,
                f"Failed login attempt for username: {username}",
            )

            return render(
                request,
                "users/login.html",
                {
                    "error": (
                        "Username ama password-ka waa khalad."
                    ),
                    "username": username,
                },
            )

        # ----------------------------------------------------
        # Inactive user
        # ----------------------------------------------------

        if not user.is_active:

            LoginAttempt.objects.create(
                username=username,
                ip_address=get_client_ip(request),
            )

            create_login_audit_log(
                user,
                "LOGIN_BLOCKED",
                request,
                "Login blocked because user account is inactive.",
            )

            return render(
                request,
                "users/login.html",
                {
                    "error": (
                        "Account-kan waa inactive. "
                        "Fadlan la xiriir Administrator."
                    ),
                    "username": username,
                },
            )

        # ----------------------------------------------------
        # Get Profile
        # ----------------------------------------------------

        profile = get_user_profile(user)

        # ----------------------------------------------------
        # Missing Profile
        # ----------------------------------------------------

        if profile is None:

            # -----------------------------------------------
            # Try to find Student record
            # -----------------------------------------------

            try:
                student_record = Student.objects.get(
                    user=user
                )
            except Student.DoesNotExist:
                student_record = None

            # -----------------------------------------------
            # Student exists but Profile missing
            # -----------------------------------------------

            if student_record:

                profile = Profile.objects.create(
                    user=user,
                    role="Student",
                    is_approved=True,
                )

            else:

                return render(
                    request,
                    "users/login.html",
                    {
                        "error": (
                            "Account-kaaga Profile ma laha. "
                            "Fadlan la xiriir Administrator."
                        ),
                        "username": username,
                    },
                )

        # ====================================================
        # SUPERUSER
        # ====================================================

        if user.is_superuser:

            login(request, user)

            create_login_audit_log(
                user,
                "LOGIN_SUCCESS",
                request,
                "Superuser logged in successfully.",
            )

            if next_url:
                return redirect(next_url)

            return redirect("student-home")

        # ====================================================
        # GET STUDENT RECORD
        # ====================================================

        try:

            student_record = (
                Student.objects
                .select_related("class_room")
                .get(user=user)
            )

        except Student.DoesNotExist:

            student_record = None

        # ====================================================
        # STUDENT
        # ====================================================

        if profile.role == "Student":

            # ------------------------------------------------
            # Student record must exist
            # ------------------------------------------------

            if student_record:

                # --------------------------------------------
                # Student can automatically be approved
                # --------------------------------------------

                if not profile.is_approved:

                    profile.is_approved = True

                    profile.save()

                # --------------------------------------------
                # Login
                # --------------------------------------------

                login(request, user)

                create_login_audit_log(
                    user,
                    "LOGIN_SUCCESS",
                    request,
                    "Student logged in successfully.",
                )

                # students/urls.py has no app_name="students"
                # therefore do NOT use students:student-dashboard

                return redirect("student-dashboard")

            # ------------------------------------------------
            # No Student record
            # ------------------------------------------------

            return render(
                request,
                "users/login.html",
                {
                    "error": (
                        "Student account-kaaga lama xiriirin "
                        "Student record. Fadlan la xiriir "
                        "Administrator."
                    ),
                    "username": username,
                },
            )

        # ====================================================
        # TEACHER
        # ====================================================
        #
        # IMPORTANT:
        #
        # Teacher approval is NOT required for login.
        #
        # Haddii username + password sax yihiin:
        #     authenticate()
        #             ↓
        #        Profile Teacher
        #             ↓
        #          login()
        #             ↓
        #     Teacher Dashboard
        #
        # ====================================================

        if profile.role == "Teacher":

            # ------------------------------------------------
            # Automatically approve Teacher after successful
            # username/password authentication.
            # ------------------------------------------------

            if not profile.is_approved:

                profile.is_approved = True

                profile.save(
                    update_fields=[
                        "is_approved",
                    ]
                )

            # ------------------------------------------------
            # Login Teacher
            # ------------------------------------------------

            login(request, user)

            create_login_audit_log(
                user,
                "LOGIN_SUCCESS",
                request,
                "Teacher logged in successfully.",
            )

            # ------------------------------------------------
            # Teacher Dashboard
            # ------------------------------------------------

            return redirect(
                "teacherapp:teacher-dashboard"
            )

        # ====================================================
        # APPROVAL CHECK
        # ====================================================
        #
        # This applies to other non-Teacher roles.
        #
        # Teacher is already handled above.
        #
        # ====================================================

        if not profile.is_approved:

            create_login_audit_log(
                user,
                "LOGIN_BLOCKED",
                request,
                "Login blocked because account is awaiting approval.",
            )

            return render(
                request,
                "users/login.html",
                {
                    "error": (
                        "Account-kaaga wali lama approve-gareyn. "
                        "Fadlan sug Administrator approval."
                    ),
                    "username": username,
                },
            )

        # ====================================================
        # ADMINISTRATOR
        # ====================================================

        if profile.role == "Administrator":

            login(request, user)

            create_login_audit_log(
                user,
                "LOGIN_SUCCESS",
                request,
                "Administrator logged in successfully.",
            )

            if next_url:
                return redirect(next_url)

            return redirect("student-home")

        # ====================================================
        # MANAGER
        # ====================================================

        if profile.role == "Manager":

            login(request, user)

            create_login_audit_log(
                user,
                "LOGIN_SUCCESS",
                request,
                "Manager logged in successfully.",
            )

            if next_url:
                return redirect(next_url)

            return redirect("student-home")

        # ====================================================
        # UNKNOWN ROLE
        # ====================================================

        logout(request)

        return render(
            request,
            "users/login.html",
            {
                "error": (
                    "Role-ka account-kan lama aqoonsana. "
                    "Fadlan la xiriir Administrator."
                ),
                "username": username,
            },
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    return render(
        request,
        "users/login.html",
    )


# ============================================================
# LOGOUT USER
# ============================================================

@login_required
def logoutUser(request):

    user = request.user

    create_login_audit_log(
        user,
        "LOGOUT",
        request,
        "User logged out successfully.",
    )

    logout(request)

    return redirect("users:login")


# ============================================================
# MANAGE USERS
# ============================================================

@login_required
def manageUsers(request):

    if not has_user_management_access(request.user):

        return access_denied(
            request,
            "Ma lihid permission aad ku maamuli karto users-ka.",
        )

    search_query = request.GET.get(
        "search",
        "",
    ).strip()

    users = (
        User.objects
        .select_related("profile")
        .all()
        .order_by("-date_joined")
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search_query:

        users = users.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(profile__role__icontains=search_query)
        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    total_users = users.count()

    active_users = users.filter(
        is_active=True
    ).count()

    inactive_users = users.filter(
        is_active=False
    ).count()

    approved_users = users.filter(
        profile__is_approved=True
    ).count()

    pending_users = users.filter(
        profile__is_approved=False
    ).count()

    context = {
        "users": users,
        "search_query": search_query,
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "approved_users": approved_users,
        "pending_users": pending_users,
    }

    return render(
        request,
        "users/manage_users.html",
        context,
    )


# ============================================================
# ADD USER
# ============================================================

@require_http_methods(["GET", "POST"])
@login_required
def addUser(request):

    # --------------------------------------------------------
    # Only Administrator / Superuser
    # --------------------------------------------------------

    if not has_user_management_access(request.user):

        return access_denied(
            request,
            "Kaliya Administrator ayaa user cusub abuuri kara.",
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        role = request.POST.get(
            "role",
            "Student",
        ).strip()

        is_approved = request.POST.get(
            "is_approved"
        ) == "on"

        is_active = request.POST.get(
            "is_active"
        ) != "off"

        errors = []

        # ----------------------------------------------------
        # Validate Role
        # ----------------------------------------------------

        if role not in VALID_ROLES:

            errors.append(
                "Role-ka la doortay ma saxna."
            )

        # ----------------------------------------------------
        # Validate Username
        # ----------------------------------------------------

        if not username:

            errors.append(
                "Username waa required."
            )

        elif User.objects.filter(
            username=username
        ).exists():

            errors.append(
                "Username-kan hore ayaa loo isticmaalay."
            )

        # ----------------------------------------------------
        # Validate Password
        # ----------------------------------------------------

        if not password:

            errors.append(
                "Password waa required."
            )

        # ----------------------------------------------------
        # Validate Email
        # ----------------------------------------------------

        if email and User.objects.filter(
            email=email
        ).exists():

            errors.append(
                "Email-kan hore ayaa loo isticmaalay."
            )

        # ----------------------------------------------------
        # Errors
        # ----------------------------------------------------

        if errors:

            return render(
                request,
                "users/add_user.html",
                {
                    "errors": errors,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "role": role,
                },
            )

        # ----------------------------------------------------
        # Create User
        # ----------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        user.is_active = is_active

        user.save()

        # ----------------------------------------------------
        # Create Profile
        # ----------------------------------------------------

        Profile.objects.create(
            user=user,
            role=role,
            is_approved=is_approved,
        )

        # ----------------------------------------------------
        # Audit
        # ----------------------------------------------------

        create_login_audit_log(
            request.user,
            "USER_CREATED",
            request,
            f"Created user: {username}",
        )

        return redirect(
            "users:manage-users"
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    return render(
        request,
        "users/add_user.html",
    )


# ============================================================
# EDIT USER PERMISSIONS
# ============================================================

@require_http_methods(["GET", "POST"])
@login_required
def editUserPermissions(request, pk):

    # --------------------------------------------------------
    # Permission
    # --------------------------------------------------------

    if not has_user_management_access(request.user):

        return access_denied(
            request,
            "Ma lihid permission aad ku beddeli karto "
            "user permissions.",
        )

    # --------------------------------------------------------
    # Target User
    # --------------------------------------------------------

    target_user = get_object_or_404(
        User,
        pk=pk,
    )

    # --------------------------------------------------------
    # Target Profile
    # --------------------------------------------------------

    profile = get_user_profile(target_user)

    if profile is None:

        profile = Profile.objects.create(
            user=target_user,
            role="Student",
            is_approved=False,
        )

    # --------------------------------------------------------
    # Student Record
    # --------------------------------------------------------

    try:

        student_record = (
            Student.objects
            .select_related("class_room")
            .get(user=target_user)
        )

    except Student.DoesNotExist:

        student_record = None

    # --------------------------------------------------------
    # Teacher Assignments
    # --------------------------------------------------------

    teacher_assignments = (
        TeacherAssignment.objects
        .select_related(
            "class_room",
            "subject",
        )
        .filter(
            teacher=target_user
        )
        .order_by(
            "class_room__name",
            "subject__name",
        )
    )

    # --------------------------------------------------------
    # Available Classes
    # --------------------------------------------------------

    classes = (
        ClassRoom.objects
        .filter(status="Active")
        .order_by("name")
    )

    # --------------------------------------------------------
    # Available Subjects
    # --------------------------------------------------------

    subjects = (
        Subject.objects
        .order_by("name")
    )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        old_role = profile.role

        # ----------------------------------------------------
        # New Role
        # ----------------------------------------------------

        new_role = request.POST.get(
            "role",
            old_role,
        ).strip()

        if new_role not in VALID_ROLES:

            return render(
                request,
                "users/edit_user_permissions.html",
                {
                    "target_user": target_user,
                    "profile": profile,
                    "student_record": student_record,
                    "teacher_assignments": teacher_assignments,
                    "classes": classes,
                    "subjects": subjects,
                    "error": "Role-ka la doortay ma saxna.",
                },
            )

        # ----------------------------------------------------
        # Approval
        # ----------------------------------------------------

        is_approved = request.POST.get(
            "is_approved"
        ) == "on"

        # ----------------------------------------------------
        # Student Class
        # ----------------------------------------------------

        student_class_id = get_post_id(
            request,
            "class_room",
            "student_class",
        )

        # ----------------------------------------------------
        # Teacher Class
        # ----------------------------------------------------

        teacher_class_id = get_post_id(
            request,
            "teacher_class",
            "class_room",
        )

        # ----------------------------------------------------
        # Teacher Subject
        # ----------------------------------------------------

        teacher_subject_id = get_post_id(
            request,
            "subject",
        )

        # ====================================================
        # UPDATE PROFILE
        # ====================================================

        profile.role = new_role

        profile.is_approved = is_approved

        # Profile.save() automatically applies role permissions.

        profile.save()

        # ====================================================
        # STUDENT
        # ====================================================

        if new_role == "Student":

            # ------------------------------------------------
            # Assign class only if Student record exists
            # ------------------------------------------------

            if student_record:

                if student_class_id:

                    try:

                        selected_class = ClassRoom.objects.get(
                            pk=student_class_id
                        )

                        student_record.class_room = selected_class

                        student_record.save(
                            update_fields=[
                                "class_room",
                                "updated_at",
                            ]
                        )

                    except ClassRoom.DoesNotExist:
                        pass

            # ------------------------------------------------
            # If changing Teacher -> Student
            # deactivate teacher assignments
            # ------------------------------------------------

            if old_role == "Teacher":

                TeacherAssignment.objects.filter(
                    teacher=target_user,
                    status="Active",
                ).update(
                    status="Inactive"
                )

        # ====================================================
        # TEACHER
        # ====================================================

        elif new_role == "Teacher":

            # ------------------------------------------------
            # Teacher must have class + subject
            # ------------------------------------------------

            if teacher_class_id and teacher_subject_id:

                try:

                    selected_class = ClassRoom.objects.get(
                        pk=teacher_class_id
                    )

                    selected_subject = Subject.objects.get(
                        pk=teacher_subject_id
                    )

                    assignment, created = (
                        TeacherAssignment.objects.get_or_create(
                            teacher=target_user,
                            class_room=selected_class,
                            subject=selected_subject,
                            defaults={
                                "status": "Active",
                            },
                        )
                    )

                    # ----------------------------------------
                    # Reactivate existing assignment
                    # ----------------------------------------

                    if (
                        not created
                        and assignment.status != "Active"
                    ):

                        assignment.status = "Active"

                        assignment.save(
                            update_fields=[
                                "status",
                                "updated_at",
                            ]
                        )

                except (
                    ClassRoom.DoesNotExist,
                    Subject.DoesNotExist,
                ):
                    pass

        # ====================================================
        # ADMINISTRATOR / MANAGER
        # ====================================================

        elif new_role in [
            "Administrator",
            "Manager",
        ]:

            # ------------------------------------------------
            # If changed from Teacher, deactivate assignments
            # ------------------------------------------------

            if old_role == "Teacher":

                TeacherAssignment.objects.filter(
                    teacher=target_user,
                    status="Active",
                ).update(
                    status="Inactive"
                )

        # ====================================================
        # AUDIT LOG
        # ====================================================

        create_login_audit_log(
            request.user,
            "USER_PERMISSIONS_UPDATED",
            request,
            (
                f"Updated user {target_user.username}: "
                f"role {old_role} -> {new_role}"
            ),
        )

        # ====================================================
        # REDIRECT
        # ====================================================

        return redirect(
            "users:manage-users"
        )

    # ========================================================
    # GET
    # ========================================================

    selected_class_id = None

    # --------------------------------------------------------
    # Student selected class
    # --------------------------------------------------------

    if student_record and student_record.class_room:

        selected_class_id = (
            student_record.class_room.id
        )

    # --------------------------------------------------------
    # Teacher selected class
    # --------------------------------------------------------

    if (
        profile.role == "Teacher"
        and teacher_assignments.exists()
    ):

        first_assignment = teacher_assignments.first()

        if first_assignment:

            selected_class_id = (
                first_assignment.class_room.id
            )

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {
        "target_user": target_user,
        "profile": profile,
        "student_record": student_record,
        "teacher_assignments": teacher_assignments,
        "classes": classes,
        "subjects": subjects,
        "selected_class_id": selected_class_id,
        "valid_roles": VALID_ROLES,
    }

    return render(
        request,
        "users/edit_user_permissions.html",
        context,
    )


# ============================================================
# USER DETAIL
# ============================================================

@login_required
def userDetail(request, pk):

    if not has_user_management_access(request.user):

        return access_denied(
            request,
            "Ma lihid permission aad ku arki karto user-kan.",
        )

    target_user = get_object_or_404(
        User,
        pk=pk,
    )

    profile = get_user_profile(
        target_user
    )

    # --------------------------------------------------------
    # Student
    # --------------------------------------------------------

    try:

        student_record = (
            Student.objects
            .select_related("class_room")
            .get(user=target_user)
        )

    except Student.DoesNotExist:

        student_record = None

    # --------------------------------------------------------
    # Teacher assignments
    # --------------------------------------------------------

    teacher_assignments = (
        TeacherAssignment.objects
        .select_related(
            "class_room",
            "subject",
        )
        .filter(
            teacher=target_user
        )
        .order_by(
            "class_room__name",
            "subject__name",
        )
    )

    context = {
        "target_user": target_user,
        "profile": profile,
        "student_record": student_record,
        "teacher_assignments": teacher_assignments,
    }

    return render(
        request,
        "users/user_detail.html",
        context,
    )


# ============================================================
# TOGGLE USER STATUS
# ============================================================

@login_required
def toggleUserStatus(request, pk):

    if not has_user_management_access(request.user):

        return access_denied(
            request,
            "Ma lihid permission aad ku beddeli karto "
            "user status."
        )

    target_user = get_object_or_404(
        User,
        pk=pk,
    )

    # --------------------------------------------------------
    # Prevent changing own status
    # --------------------------------------------------------

    if target_user == request.user:

        return access_denied(
            request,
            "Ma beddeli kartid status-ka account-kaaga."
        )

    # --------------------------------------------------------
    # Toggle
    # --------------------------------------------------------

    target_user.is_active = not target_user.is_active

    target_user.save(
        update_fields=[
            "is_active",
        ]
    )

    # --------------------------------------------------------
    # Audit
    # --------------------------------------------------------

    create_login_audit_log(
        request.user,
        "USER_STATUS_CHANGED",
        request,
        (
            f"Changed status for "
            f"{target_user.username} to "
            f"{target_user.is_active}"
        ),
    )

    return redirect(
        "users:manage-users"
    )


# ============================================================
# DELETE USER
# ============================================================

@login_required
def deleteUser(request, pk):

    if not has_user_management_access(request.user):

        return access_denied(
            request,
            "Ma lihid permission aad ku delete-gareyn karto user."
        )

    target_user = get_object_or_404(
        User,
        pk=pk,
    )

    # --------------------------------------------------------
    # Prevent deleting yourself
    # --------------------------------------------------------

    if target_user == request.user:

        return access_denied(
            request,
            "Ma delete-gareyn kartid account-kaaga."
        )

    # --------------------------------------------------------
    # Prevent deleting superuser
    # --------------------------------------------------------

    if target_user.is_superuser:

        return access_denied(
            request,
            "Superuser lama delete-gareyn karo."
        )

    # --------------------------------------------------------
    # POST = Confirm delete
    # --------------------------------------------------------

    if request.method == "POST":

        username = target_user.username

        target_user.delete()

        create_login_audit_log(
            request.user,
            "USER_DELETED",
            request,
            f"Deleted user: {username}",
        )

        return redirect(
            "users:manage-users"
        )

    # --------------------------------------------------------
    # GET = Confirmation page
    # --------------------------------------------------------

    return render(
        request,
        "users/delete_user.html",
        {
            "target_user": target_user,
        },
    )
