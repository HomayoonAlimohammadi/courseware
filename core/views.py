from __future__ import annotations
from webbrowser import get
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from core.forms import (
    ContactUsForm,
    DepartmentCreateForm,
    DepartmentUpdateForm,
    UserCreateForm,
    UserLoginForm,
    UserUpdateForm,
    CourseCreateForm,
    CourseUpdateForm,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from core.utils import send_email_to_support, ContactSupportException
from core.models import Course, Department, User
from django.db.models import Q


def handle_404_view(request, exception: Exception):
    print(exception)
    return render(request, "404.html")


@require_http_methods(["GET"])
def index_view(request):
    q = request.GET.get("q", "")
    courses = Course.objects.filter(name__icontains=q)[:5]
    context = {"courses": courses}
    return render(request, "index.html", context=context)


@require_http_methods(["GET", "POST"])
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
                    subject=title, message=text, customer_email=customer_email
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
            messages.add_message(request, messages.ERROR, form.errors.as_text())
    return render(request, "contact_us.html", context=context)


@require_http_methods(["GET"])
def user_list_view(request):
    q = request.GET.get("q", "")
    teacher_users = User.objects.filter(is_staff=True, username__icontains=q).all()
    student_users = User.objects.filter(is_staff=False, username__icontains=q).all()
    context = {
        "teacher_users": teacher_users,
        "student_users": student_users,
    }
    return render(request, "user/user_list.html", context=context)


@require_http_methods(["GET"])
def user_details_view(request, username: str):
    user = get_object_or_404(User, username=username)
    context = {"user": user}
    return render(request, "user/user_details.html", context=context)


@require_http_methods(["GET", "POST"])
def user_login_view(request):
    if request.user.is_authenticated:
        messages.add_message(request, messages.ERROR, "You are already logged in.")
        return redirect("core:index")
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
                messages.add_message(request, messages.ERROR, "Invalid credentials.")

    return render(request, "user/user_login.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
@require_http_methods(["GET", "POST"])
def user_logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.add_message(request, messages.SUCCESS, "Logged out successfully.")
        return redirect("core:index")
    return render(request, "user/user_logout.html")


@require_http_methods(["GET", "POST"])
def user_create_view(request):
    form = UserCreateForm(request.POST, request.FILES or None)
    context = {"form": form}
    if request.method == "POST":
        if form.is_valid():
            password = form.cleaned_data.get("password")
            title = request.POST.get("title")
            user = form.save()
            user.is_staff = title == "Teacher"
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
@require_http_methods(["GET", "POST"])
def user_update_view(request, username: str):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        messages.add_message(
            request, messages.ERROR, "You can only update your own profile!"
        )
        return redirect("core:index")
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=user)
    context = {"form": form}
    if request.method == "POST":
        if form.is_valid():
            gender = request.POST.get("gender")
            user.gender = gender
            user.save()
            messages.add_message(
                request, messages.SUCCESS, "Information were updated successfully."
            )
            return redirect("core:user_details", username=user.username)
        else:
            messages.add_message(request, messages.ERROR, form.errors.as_text())
    return render(request, "user/user_update.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
@require_http_methods(["GET", "POST"])
def course_create_view(request):
    if not request.user.is_superuser:
        messages.add_message(request, messages.ERROR, "Only Admins can create Courses.")
        return redirect("core:index")
    form = CourseCreateForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST":
        if form.is_valid():
            first_day = request.POST.get("first_day")
            second_day = request.POST.get("second_day")
            teacher = form.cleaned_data.get("teacher")
            if not teacher.is_staff:  # type: ignore
                messages.add_message(request, messages.ERROR, "Teacher is invalid.")
                return redirect("core:course_create")
            if first_day.lower() == second_day.lower():
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Course should be held in two different days.",
                )
                return redirect("core:course_create")

            course = Course.objects.create(
                **form.cleaned_data,
                first_day=first_day,
                second_day=second_day,
                user=request.user,
            )
            messages.add_message(
                request, messages.SUCCESS, f"Course `{course.name}` was added."
            )
            return redirect("core:index")
        else:
            messages.add_message(request, messages.ERROR, form.errors.as_text())

    return render(request, "course/course_create.html", context=context)


@require_http_methods(["GET"])
def course_details_view(request, course_number: int):
    course = get_object_or_404(Course, course_number=course_number)
    context = {"course": course}
    return render(request, "course/course_details.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
@require_http_methods(["GET", "POST"])
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
            if teacher and not teacher.is_staff:
                messages.add_message(request, messages.ERROR, "Teacher is not valid.")
            else:
                course.teacher = teacher
            course.start_time = start_time
            course.end_time = end_time
            course.first_day = first_day
            course.second_day = second_day
            course.save()
            return redirect("core:course_details", course_number=course_number)
        else:
            messages.add_message(request, messages.ERROR, form.errors.as_text())

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


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
@require_http_methods(["GET"])
def course_add_user_view(request, course_number: int):
    course = get_object_or_404(Course, course_number=course_number)
    user = request.user
    if user.is_superuser or user.is_staff:
        messages.add_message(
            request, messages.ERROR, "Admins and Teachers can not take courses."
        )
        return redirect("core:course_details", course_number=course_number)
    if course not in user.participated_courses.all():
        course.participants.add(user)
        messages.add_message(
            request,
            messages.SUCCESS,
            f"Course {course.name} was added to your course list.",
        )
        return redirect("core:user_details", username=user.username)
    else:
        messages.add_message(request, messages.ERROR, "Can only add a course once.")
        return redirect("core:course_details", course_number=course_number)


@require_http_methods(["GET"])
def department_list_view(request):
    q = request.GET.get("q", "")
    departments = Department.objects.filter(name__icontains=q)
    context = {"departments": departments}
    return render(request, "department/department_list.html", context=context)


@require_http_methods(["GET"])
def department_details_view(request, department_number: int):
    department = get_object_or_404(Department, department_number=department_number)
    context = {"department": department}
    return render(request, "department/department_details.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
@require_http_methods(["GET", "POST"])
def department_create_view(request):
    form = DepartmentCreateForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST":
        if not request.user.is_superuser:
            messages.add_message(
                request, messages.ERROR, "Only Admins can create a department"
            )
            return redirect("core:index")
        if form.is_valid():
            department = Department.objects.create(
                **form.cleaned_data, manager=request.user
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Department `{department.name}` was added successfully.",
            )
            return redirect(
                "core:department_details",
                department_number=department.department_number,
            )
        else:
            messages.add_message(request, messages.ERROR, form.errors.as_text())

    return render(request, "department/department_create.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
@require_http_methods(["GET", "POST"])
def department_update_view(request, department_number: int):
    department = get_object_or_404(Department, department_number=department_number)
    if request.user != department.manager:
        messages.add_message(
            request,
            messages.ERROR,
            "Only the department manager can update information.",
        )
        return redirect("core:department_details", department_number=department_number)
    form = DepartmentUpdateForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data.get("name")
            department_number = form.cleaned_data.get("department_number")  # type: ignore
            description = form.cleaned_data.get("description")
            department.name = name
            department.description = description
            department.department_number = department_number
            try:
                department.save()
            except Exception as e:
                print(e.__class__)
                print(e)
                messages.add_message(request, messages.ERROR, "Invalid data.")
            return redirect(
                "core:department_details", department_number=department_number
            )
        else:
            messages.add_message(request, messages.ERROR, form.errors.as_text())

    initial_data = {
        "name": department.name,
        "department_number": department.department_number,
        "description": department.description,
    }
    form = DepartmentUpdateForm(initial=initial_data)
    context = {"form": form, "department": department}
    return render(request, "department/department_update.html", context=context)


### TODO: add this to layout hrefs
@require_http_methods(["GET"])
def teacher_list_view(request):
    q = request.GET.get("q", "")
    teachers = (
        User.objects.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q))
        .filter(is_staff=True)
        .order_by("last_name")
    )
    context = {"users": teachers}
    return render(request, "user/user_list.html", context)


def user_interval_create_view(request, username: str):
    HttpResponse("Not implemented yet.")


def user_interval_list_view(request, username: str):
    HttpResponse("Not implemented yet.")


def user_interval_details_view(request, username: str, pk: int):
    HttpResponse("Not implemented yet.")


def user_interval_update_view(request, username: str, pk: int):
    HttpResponse("Not implemented yet.")


def user_interval_delete_view(request, username: str, pk: int):
    HttpResponse("Not implemented yet.")
