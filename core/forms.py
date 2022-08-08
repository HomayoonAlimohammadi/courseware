from django import forms
from core.models import Course, Department, User, Interval


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


class UserUpdateForm(forms.ModelForm):
    bio_placeholder = "Write about yourself using Markdown language:"
    bio = forms.CharField(
        widget=forms.Textarea({"placeholder": bio_placeholder}), required=False
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "bio",
            "image",
        ]


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=128)
    password = forms.CharField(widget=forms.PasswordInput())


class ContactUsForm(forms.Form):
    title = forms.CharField(max_length=128)
    email = forms.EmailField()
    text = forms.CharField(widget=forms.Textarea(), required=False)


class CourseCreateForm(forms.Form):
    name = forms.CharField(max_length=128)
    teacher = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True))
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    course_number = forms.IntegerField()
    group_number = forms.IntegerField()
    start_time = forms.TimeField(help_text="Example: 10:00")
    end_time = forms.TimeField(help_text="Example: 12:00")


class CourseUpdateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "name",
            "department",
            "course_number",
            "group_number",
            "teacher",
            "start_time",
            "end_time",
        ]


class DepartmentCreateForm(forms.ModelForm):
    class Meta:
        model = Department
        exclude = ["manager"]


class DepartmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "description", "department_number"]


class IntervalCreateForm(forms.Form):
    start_time = forms.TimeField(help_text="Example: 10:00")
    end_time = forms.TimeField(help_text="Example: 12:00")
    capacity = forms.IntegerField()


class IntervalUpdateForm(forms.Form):
    start_time = forms.TimeField(help_text="Example: 10:00")
    end_time = forms.TimeField(help_text="Example: 12:00")
    capacity = forms.IntegerField()
