from django.urls import path

from . import views

app_name = "users"

urlpatterns = [


# ============================================================
# AUTHENTICATION
# ============================================================

path(
    "login/",
    views.loginUser,
    name="login",
),

path(
    "register/",
    views.registerUser,
    name="register",
),

path(
    "logout/",
    views.logoutUser,
    name="logout",
),

# ============================================================
# USER MANAGEMENT
# ============================================================

path(
    "dashboard/users/",
    views.manageUsers,
    name="manage-users",
),

# ============================================================
# ADD USER
# ============================================================

path(
    "dashboard/users/add/",
    views.addUser,
    name="add-user",
),

# ============================================================
# EDIT ROLE / ACCESS
# ============================================================

path(
    "dashboard/users/<int:user_id>/permissions/",
    views.editUserPermissions,
    name="edit-user-permissions",
),

# ============================================================
# USER DETAIL
# ============================================================

path(
    "dashboard/users/<int:user_id>/detail/",
    views.userDetail,
    name="user-detail",
),

# ============================================================
# ACTIVATE / DEACTIVATE
# ============================================================

path(
    "dashboard/users/<int:user_id>/status/",
    views.toggleUserStatus,
    name="toggle-user-status",
),

# ============================================================
# DELETE USER
# ============================================================

path(
    "dashboard/users/<int:user_id>/delete/",
    views.deleteUser,
    name="delete-user",
),


]
