from django.contrib.auth import get_user_model
from django import forms
from core.models import Course, Department, Teacher, User


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    error_messages = {
        "duplicate_username": "Your username is already available in the system!",
        "duplicate_email": "Your Email is already available in the system!",
    }

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "confirm_password",
            "image",
        ]

    def clean(self):
        cleaned_data = super(UserCreateForm, self).clean()
        password = cleaned_data.get("password")  # type: ignore
        confirm_password = cleaned_data.get("confirm_password")  # type: ignore
        if password != confirm_password:
            raise forms.ValidationError("Password and Confirmation do not match.")

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)

            raise forms.ValidationError(
                self.error_messages["duplicate_username"],
                code="duplicate_username",
            )
        except User.DoesNotExist:
            return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)

            raise forms.ValidationError(
                self.error_messages["duplicate_email"],
                code="duplicate_email",
            )
        except User.DoesNotExist:
            return email


class UserUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=128, required=False)
    last_name = forms.CharField(max_length=128, required=False)
    username = forms.CharField(max_length=128)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    def clean(self):
        cleaned_data = super(UserUpdateForm, self).clean()
        password = cleaned_data.get("password")  # type: ignore
        confirm_password = cleaned_data.get("confirm_password")  # type: ignore
        if password != confirm_password:
            raise forms.ValidationError("password and confirm_password does not match")


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=128)
    password = forms.CharField(widget=forms.PasswordInput())


class ContactUsForm(forms.Form):
    title = forms.CharField(max_length=128)
    email = forms.EmailField()
    text = forms.CharField(widget=forms.Textarea(), required=False)


class CourseCreateForm(forms.ModelForm):
    start_time = forms.TimeField(help_text="Example: 10:00")
    end_time = forms.TimeField(help_text="Example: 12:00")

    class Meta:
        model = Course
        exclude = ["user", "first_day", "second_day"]

    def clean(self):
        cleaned_data = super(CourseCreateForm, self).clean()
        start_time = cleaned_data.get("start_time")  # type: ignore
        end_time = cleaned_data.get("end_time")  # type: ignore
        if start_time >= end_time:  # type: ignore
            raise forms.ValidationError("Course should start before it ends!")


class CourseUpdateForm(forms.Form):
    name = forms.CharField(max_length=128)
    department = forms.CharField(max_length=128)
    course_number = forms.IntegerField()
    group_number = forms.IntegerField()
    teacher = forms.CharField(max_length=128)
    start_time = forms.TimeField()
    end_time = forms.TimeField()
    first_day = forms.CharField(max_length=32)
    second_day = forms.CharField(max_length=32)


class DepartmentCreateForm(forms.ModelForm):
    class Meta:
        model = Department
        exclude = ["manager"]


class DepartmentUpdateForm(forms.Form):
    name = forms.CharField(max_length=128)
    description = forms.CharField(widget=forms.Textarea(), required=False)
    department_number = forms.IntegerField()


class TeacherUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=128)
    last_name = forms.CharField(max_length=128)


class TeacherCreateForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["first_name", "last_name"]
