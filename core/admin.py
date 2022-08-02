from django.contrib import admin
from core.models import Course


class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "course_number", "group_number"]


admin.site.register(Course, CourseAdmin)
