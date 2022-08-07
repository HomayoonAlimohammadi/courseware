from django.contrib import admin
from core.models import Course, User, Department, Interval


class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "is_staff", "email", "first_name", "last_name"]


class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "course_number", "group_number"]


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "department_number", "manager"]


class IntervalAdmin(admin.ModelAdmin):
    list_display = ["teacher", "day", "capacity", "start_time", "end_time"]


admin.site.register(User, UserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Interval, IntervalAdmin)
