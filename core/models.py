from __future__ import annotations
import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from core.utils import uuid_namer
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from notifications.signals import notify


class User(AbstractUser):
    image = models.ImageField(blank=True, null=True, upload_to=uuid_namer)
    bio = models.CharField(blank=True, null=True, max_length=1024)
    gender = models.CharField(max_length=16, default="Other")

    def __str__(self) -> str:
        role = "Student"
        if self.is_staff:
            role = "Teacher"
        return f"{self.username} - {role}"

    def clean(self):
        if self.gender.lower() not in ["male", "female", "other"]:
            raise ValidationError(_("Invalid gender was selected."))


class Department(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    department_number = models.IntegerField(unique=True)
    manager = models.ForeignKey(
        User, related_name="departments_owned", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"Department({self.name[:5]})"


class Course(models.Model):
    name = models.CharField(max_length=128)
    user = models.ForeignKey(
        User, related_name="added_courses", on_delete=models.CASCADE
    )
    participants = models.ManyToManyField(
        User, related_name="participated_courses", blank=True
    )
    department = models.ForeignKey(
        Department, related_name="courses", on_delete=models.CASCADE
    )
    course_number = models.IntegerField(unique=True)
    group_number = models.IntegerField()
    teacher = models.ForeignKey(User, related_name="courses", on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    first_day = models.CharField(max_length=32)
    second_day = models.CharField(max_length=32)

    def __str__(self) -> str:
        return f"Course({self.name[:10]}...)"

    def clean(self):
        valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        if self.start_time >= self.end_time:
            raise ValidationError(_("Course should start before it ends!"))
        if self.first_day.lower() == self.second_day.lower():
            raise ValidationError(_("Course should be held in two different days."))
        if (
            self.first_day.lower() not in valid_days
            or self.second_day.lower() not in valid_days
        ):
            raise ValidationError(_("Course should be held in valid working days."))
        if not self.teacher.is_staff:
            raise ValidationError(_("Teacher must be a staff."))


class Interval(models.Model):
    teacher = models.ForeignKey(
        User, related_name="intervals", on_delete=models.CASCADE
    )
    day = models.CharField(max_length=16)
    reserving_students = models.ManyToManyField(User, related_name="reserved_intervals")
    capacity = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self) -> str:
        return f"{self.day} | {self.start_time} - {self.end_time} | {self.capacity} | {self.teacher.first_name} {self.teacher.last_name}"

    def clean(self):
        if self.day.lower() not in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
        ]:
            raise ValidationError(_("Interval should be held in valid working days."))
        if self.pk and self.capacity < self.reserving_students.count():
            raise ValidationError(
                _("Capacity can not be less than already reserving students.")
            )
        if self.start_time >= self.end_time:
            raise ValidationError(_("Course should start before it ends!"))


@receiver(models.signals.post_delete, sender=User)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes image from filesystem
    when corresponding `User` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=User)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old image from filesystem
    when corresponding `User` object is updated
    with new image.
    """
    if not instance.pk:
        return False

    try:
        old_file = User.objects.get(pk=instance.pk).image
    except User.DoesNotExist:
        return False

    try:
        new_file = instance.image
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except Exception as e:
        # TODO: These two lines should be logged.
        print(e.__class__)
        print(e)
        pass


@receiver(
    models.signals.pre_delete, sender=Interval, dispatch_uid="interval_delete_signal"
)
def notify_reserving_student_on_interval_delete(sender, instance, *args, **kwargs):
    description = f"Teacher {instance.teacher.username} deleted Interval on {instance}"
    for student in instance.reserving_students.all():
        notify.send(
            instance.teacher, recipient=student, verb="Message", description=description
        )
