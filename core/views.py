from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from core.forms import UserCreateForm, UserLoginForm
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


User = get_user_model()


@require_http_methods(["GET"])
def index_view(request):
    return render(request, "index.html")


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
            messages.add_message(request, messages.ERROR, "Invalid data.")

    return render(request, "user/user_create.html", context=context)
