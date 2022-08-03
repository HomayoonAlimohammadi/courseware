from __future__ import annotations
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from core.forms import (
    ContactUsForm,
    UserCreateForm,
    UserLoginForm,
    UserUpdateForm,
    CourseCreateForm,
    CourseUpdateForm,
)
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from core.utils import send_email_to_support, ContactSupportException
from core.models import Course


User = get_user_model()


@require_http_methods(["GET"])
def index_view(request):
    courses = Course.objects.all()[:5]
    context = {"courses": courses}
    return render(request, "index.html", context=context)


def contact_us_view(request):
    form = ContactUsForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST":
        if form.is_valid():
            title = form.cleaned_data.get("title", "")
            text = form.cleaned_data.get("text", "")
            customer_email = form.cleaned_data.get("email", "")
            try:
                send_email_to_support(
                    subject=title, message=text, recipient=customer_email
                )
            except ContactSupportException:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Could not email the support, This might be due to invalid data or some initial problem.",
                )
                return redirect("core:contact_us")
            messages.add_message(
                request, messages.SUCCESS, "Email was sent successfully."
            )
            return redirect("core:index")
        else:
            messages.add_message(request, messages.ERROR, "Invalid data.")
    return render(request, "contact_us.html", context=context)


@require_http_methods(["GET"])
def user_list_view(request):
    users = User.objects.all()
    context = {"users": users}
    return render(request, "user/user_list.html", context=context)


@require_http_methods(["GET"])
def user_details_view(request, username: str):
    user = get_object_or_404(User, username=username)
    context = {"user": user}
    return render(request, "user/user_details.html", context=context)


@require_http_methods(["GET", "POST"])
def user_login_view(request):
    form = UserLoginForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.add_message(
                    request, messages.SUCCESS, f"Logged in as `{username}`."
                )
                return redirect("core:index")
            else:
                messages.add_message(request, messages.ERROR, "Invalid data.")

    return render(request, "user/user_login.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
def user_logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.add_message(request, messages.SUCCESS, "Logged out successfully.")
        return redirect("core:index")
    return render(request, "user/user_logout.html")


@require_http_methods(["GET", "POST"])
def user_create_view(request):
    form = UserCreateForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST":
        if form.is_valid():
            password = form.cleaned_data.get("password")
            user = form.save()
            user.set_password(password)
            user.save()
            login(request, user)
            messages.add_message(
                request,
                messages.SUCCESS,
                f"User `{user.username}` was created Successfully.",
            )
            return redirect("core:index")
        else:
            messages.add_message(request, messages.ERROR, form.errors.as_text())

    return render(request, "user/user_create.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
def user_update_view(request, username: str):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        messages.add_message(
            request, messages.ERROR, "You can only update your own profile!"
        )
        return redirect("core:index")
    form = UserUpdateForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user.first_name = first_name  # type: ignore
            user.last_name = last_name  # type: ignore
            user.email = email  # type: ignore
            if password:
                user.set_password(password)
            user.save()
            return redirect("core:user_details", username=user.username)  # type: ignore
        else:
            messages.add_message(request, messages.ERROR, "Invalid data.")

    initial_data = {
        "first_name": user.first_name,  # type: ignore
        "last_name": user.last_name,  # type: ignore
        "email": user.email,  # type: ignore
        "username": user.username,  # type: ignore
    }
    form = UserUpdateForm(initial=initial_data)
    context = {"form": form}
    return render(request, "user/user_update.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
def course_create_view(request):
    if not request.user.is_superuser:
        messages.add_message(request, messages.ERROR, "Only Admins can create Courses.")
        return redirect("core:index")
    form = CourseCreateForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST":
        if form.is_valid():
            course = Course.objects.create(**form.cleaned_data, user=request.user)
            messages.add_message(
                request, messages.SUCCESS, f"Course `{course.name[:10]}` was added."
            )
            return redirect("core:index")
        else:
            messages.add_message(request, messages.ERROR, "Invalid data.")

    return render(request, "course/course_create.html", context=context)


def course_details_view(request, course_number: int):
    course = get_object_or_404(Course, course_number=course_number)
    context = {"course": course}
    return render(request, "course/course_details.html", context=context)


def course_update_view(request, course_number: int):
    course = get_object_or_404(Course, course_number=course_number)
    if request.user != course.user:
        messages.add_message(
            request, messages.ERROR, "You can only update your own Course!"
        )
        return redirect("core:course_details", course_number=course_number)
    form = CourseUpdateForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data.get("name")
            department = form.cleaned_data.get("department")
            course_number = form.cleaned_data.get("course_number")  # type: ignore
            group_number = form.cleaned_data.get("group_number")
            teacher = form.cleaned_data.get("teacher")
            start_time = form.cleaned_data.get("start_time")
            end_time = form.cleaned_data.get("end_time")
            first_day = form.cleaned_data.get("first_day")
            second_day = form.cleaned_data.get("second_day")
            course.name = name
            course.department = department
            course.course_number = course_number
            course.group_number = group_number
            course.teacher = teacher
            course.start_time = start_time
            course.end_time = end_time
            course.first_day = first_day
            course.second_day = second_day
            course.save()
            return redirect("core:course_details", course_number=course_number)
        else:
            messages.add_message(request, messages.ERROR, "Invalid data.")

    initial_data = {
        "name": course.name,
        "department": course.department,
        "course_number": course.course_number,
        "group_number": course.group_number,
        "teacher": course.teacher,
        "start_time": course.start_time,
        "end_time": course.end_time,
        "first_day": course.first_day,
        "second_day": course.second_day,
    }
    form = CourseUpdateForm(initial=initial_data)
    context = {"form": form}
    return render(request, "course/course_update.html", context=context)
