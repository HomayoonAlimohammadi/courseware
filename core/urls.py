from django.urls import path
from core import views


app_name = "core"

urlpatterns = [
    path("", views.index_view, name="index"),
    path("contact-us", views.contact_us_view, name="contact_us"),
    path("users/", views.user_list_view, name="user_list"),
    path("users/create", views.user_create_view, name="user_create"),
    path("users/login", views.user_login_view, name="user_login"),
    path("users/logout", views.user_logout_view, name="user_logout"),
    path("users/<str:username>", views.user_details_view, name="user_details"),
    path("users/<str:username>/update", views.user_update_view, name="user_update"),
    ####
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
]