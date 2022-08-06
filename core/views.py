from __future__ import annotations
from webbrowser import get
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from core.forms import (
    ContactUsForm,
    DepartmentCreateForm,
    DepartmentUpdateForm,
    IntervalCreateForm,
    IntervalUpdateForm,
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
from core.models import Course, Department, Interval, User
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def handle_404_view(request, exception: Exception):
    print(exception)
    return render(request, "404.html")


@require_http_methods(["GET"])
def index_view(request):
    q = request.GET.get("q", "")
    query = (
        Q(name__icontains=q)
        | Q(department__name__icontains=q)
        | Q(teacher__username__icontains=q)
        | Q(teacher__first_name__icontains=q)
        | Q(teacher__last_name__icontains=q)
        | Q(course_number__contains=q)
        | Q(group_number__contains=q)
        | Q(first_day__icontains=q)
        | Q(second_day__icontains=q)
    )
    courses = Course.objects.filter(query)[:5]
    context = {"courses": courses}
    if "q" in request.GET:
        context["q"] = q
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
    if q == "" and "q" in request.GET:  # search an empty string
        print("searched empty string")
        teacher_users = User.objects.none()
        student_users = User.objects.none()
    else:
        query = (
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        )
        teacher_users = User.objects.filter(Q(is_staff=True) & query).all()
        student_users = User.objects.filter(Q(is_staff=False) & query).all()
    context = {
        "teacher_users": teacher_users,
        "student_users": student_users,
    }
    if "q" in request.GET:
        context["q"] = q
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
            try:
                user.full_clean()
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, str(e))
                return redirect("core:user_create")
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
    context = {"form": form, "user": user}
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            gender = request.POST.get("gender")
            user.gender = gender
            try:
                user.full_clean()
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, str(e))
                return redirect("core:user_update", username=username)
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
            course = Course(
                **form.cleaned_data,
                first_day=first_day,
                second_day=second_day,
                user=request.user,
            )
            try:
                course.full_clean()
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, str(e))
                return redirect("core:course_create")
            course.save()
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
    print()
    print(course)
    print()
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
    form = CourseUpdateForm(request.POST or None, instance=course)
    context = {"form": form, "course": course}
    if request.method == "POST":
        if form.is_valid():
            course = form.save(commit=False)
            course.first_day = request.POST.get("first_day")
            course.second_day = request.POST.get("second_day")
            try:
                course.full_clean()
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, str(e))
                return redirect("core:course_update", course_number=course_number)
            course.save()
            messages.add_message(
                request, messages.SUCCESS, "Course was updated successfully."
            )
            return redirect("core:course_details", course_number=course_number)
        else:
            messages.add_message(request, messages.ERROR, form.errors.as_text())
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
        try:
            course.full_clean()
        except ValidationError as e:
            messages.add_message(request, messages.ERROR, str(e))
            return redirect("core:course_details", course_number=course_number)
        course.save()
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
    if "q" in request.GET:
        context["q"] = q
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
            department = Department(**form.cleaned_data, manager=request.user)
            try:
                department.full_clean()
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, str(e))
                return redirect("core:department_create")
            department.save()
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
    form = DepartmentUpdateForm(request.POST or None, instance=department)
    context = {"form": form, "department": department}
    if request.method == "POST":
        if form.is_valid():
            department = form.save(commit=False)
            try:
                department.full_clean()
            except Exception as e:
                messages.add_message(request, messages.ERROR, str(e))
                return redirect(
                    "core:department_update", department_number=department_number
                )
            department.save()
            messages.add_message(
                request, messages.SUCCESS, "Department was updated successfully."
            )
            return redirect(
                "core:department_details", department_number=department_number
            )
        else:
            messages.add_message(request, messages.ERROR, form.errors.as_text())
    return render(request, "department/department_update.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
@require_http_methods(["GET", "POST"])
def user_interval_create_view(request, username: str):
    form = IntervalCreateForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST":
        if form.is_valid():
            interval = form.save(commit=False)
            try:
                interval.full_clean()
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, str(e))
                return redirect("core:interval_create", username=username)
            interval.save()
            messages.add_message(
                request, messages.SUCCESS, "Interval was added successfully."
            )
        else:
            messages.add_message(request, messages.ERROR, form.errors.as_text())
            return redirect("core:interval_create", username=username)

    return render(request, "interval/interval_create.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
@require_http_methods(["GET", "POST"])
def user_interval_update_view(request, username: str, pk: int):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        messages.add_message(
            request, messages.ERROR, "You can only edit your own Interval."
        )
        return redirect("core:user_details", username=request.user.username)

    interval = get_object_or_404(Interval, pk=pk)
    form = IntervalUpdateForm(request.POST or None, instance=interval)
    context = {"form": form, "interval": interval}
    if request.method == "POST":
        if form.is_valid():
            interval = form.save(commit=False)
            try:
                interval.full_clean()
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, str(e))
                return redirect("core:interval_update", username=username, pk=pk)
            interval.save()
            messages.add_message(
                request,
                messages.ERROR,
                "Capacity can not be lower than currently reserving students.",
            )
        else:
            messages.add_message(request, messages.ERROR, "Invalid data.")
    return render(request, "interval/interval_update.html", context=context)


@login_required(login_url=reverse_lazy("core:user_login"))  # type: ignore
@require_http_methods(["GET", "POST"])
def user_interval_delete_view(request, username: str, pk: int):
    interval = get_object_or_404(Interval, pk=pk)
    context = {"interval": interval}
    if request.method == "POST":
        interval.delete()
        messages.add_message(
            request, messages.SUCCESS, "Interval was deleted successfully."
        )
        return redirect("core:use_details", username=username)

    return render(request, "interval/interval_delete.html", context=context)
