from django.urls import path
from api import views


app_name = "api"

urlpatterns = [
    path("teachers/", views.teacher_list_view, name="teacher_list"),
    path("students/", views.student_list_view, name="student_list"),
]
