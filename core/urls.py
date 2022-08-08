from django.urls import path
from core import views


app_name = "core"

handler404 = "core.views.handle_404_view"

urlpatterns = [
    path("", views.index_view, name="index"),
    path("support/", views.contact_us_view, name="contact_us"),
    path("users/", views.user_list_view, name="user_list"),
    path("users/create", views.user_create_view, name="user_create"),
    path("users/login", views.user_login_view, name="user_login"),
    path("users/logout", views.user_logout_view, name="user_logout"),
    path("users/<str:username>", views.user_details_view, name="user_details"),
    path("users/<str:username>/delete", views.user_delete_view, name="user_delete"),
    path("users/<str:username>/update", views.user_update_view, name="user_update"),
    path(
        "users/<str:username>/intervals/create",
        views.user_interval_create_view,
        name="user_interval_create",
    ),
    path(
        "users/<str:username>/intervals/<int:pk>/update",
        views.user_interval_update_view,
        name="user_interval_update",
    ),
    path(
        "users/<str:username>/intervals/<int:pk>/delete",
        views.user_interval_delete_view,
        name="user_interval_delete",
    ),
    path(
        "users/<str:username>/intervals/<int:pk>/reserve",
        views.user_interval_reserve_view,
        name="user_interval_reserve",
    ),
    path(
        "users/<str:username>/intervals/<int:pk>/release",
        views.user_interval_release_view,
        name="user_interval_release",
    ),
    #### Courses
    path("courses/", views.index_view, name="course_list"),
    path("courses/create", views.course_create_view, name="course_create"),
    path(
        "courses/<int:course_number>/", views.course_details_view, name="course_details"
    ),
    path(
        "courses/<int:course_number>/update",
        views.course_update_view,
        name="course_update",
    ),
    path(
        "courses/<int:course_number>/add-user",
        views.course_add_user_view,
        name="course_add_user",
    ),
    #### Departments
    path("departments/", views.department_list_view, name="department_list"),
    path("departments/create", views.department_create_view, name="department_create"),
    path(
        "departments/<int:department_number>/",
        views.department_details_view,
        name="department_details",
    ),
    path(
        "departments/<int:department_number>/update",
        views.department_update_view,
        name="department_update",
    ),
]
