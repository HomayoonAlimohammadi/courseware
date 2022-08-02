from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Course(models.Model):
    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, related_name="courses", on_delete=models.CASCADE)
    department = models.CharField(max_length=128)
    course_number = models.IntegerField(unique=True)
    group_number = models.IntegerField()
    teacher = models.CharField(max_length=128)
    start_time = models.TimeField()
    end_time = models.TimeField()
    first_day = models.CharField(max_length=32)
    second_day = models.CharField(max_length=32)

    def __str__(self) -> str:
        return f"Course({self.name[:10]}...)"
