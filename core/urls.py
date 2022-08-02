from django.urls import path
from core import views


app_name = "core"

urlpatterns = [
    path("", views.index_view, name="index"),
    path("users/", views.user_list_view, name="user_list"),
    path("users/create", views.user_create_view, name="user_create"),
    path("users/login", views.user_login_view, name="user_login"),
    path("users/logout", views.user_logout_view, name="user_logout"),
    path("users/<str:username>", views.user_details_view, name="user_details"),
]
