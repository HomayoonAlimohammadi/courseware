"""courseware URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
import notifications.urls


password_reset_email_sent_view = auth_views.PasswordResetDoneView.as_view(
    template_name="password/reset_email_sent.html"
)
password_reset_confirm_view = auth_views.PasswordResetConfirmView.as_view(
    template_name="password/reset_confirm.html"
)
password_reset_complete_view = auth_views.PasswordResetCompleteView.as_view(
    template_name="password/reset_complete.html"
)


urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("", include("core.urls")),
        path("api/", include("api.urls")),
        path(
            "passwords/reset/email-sent",
            password_reset_email_sent_view,
            name="password_reset_email_sent",
        ),
        path(
            "passwords/reset/<uidb64>/<token>",
            password_reset_confirm_view,
            name="password_reset_confirm",
        ),
        path(
            "passwords/reset/complete",
            password_reset_complete_view,
            name="password_reset_complete",
        ),
        re_path(
            "^inbox/notifications/",
            include(notifications.urls, namespace="notifications"),
        ),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
