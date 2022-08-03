from django.contrib import admin
from core.models import Course, User, Department


class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "is_staff", "email", "first_name", "last_name"]


class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "course_number", "group_number"]


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "department_number", "manager"]


admin.site.register(User, UserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Course, CourseAdmin)
