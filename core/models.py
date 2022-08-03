from __future__ import annotations
import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from core.utils import uuid_namer


class User(AbstractUser):
    image = models.ImageField(blank=True, null=True, upload_to=uuid_namer)

    def __str__(self) -> str:
        return f"User({self.username})"


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


class Teacher(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return f"Mr/Ms {self.last_name}"

    def __repr__(self) -> str:
        return f"Teacher({self.last_name[:5]})"


class Course(models.Model):
    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, related_name="courses", on_delete=models.CASCADE)
    participants = models.ManyToManyField(
        User, related_name="participated_courses", null=True, blank=True
    )
    department = models.ForeignKey(
        Department, related_name="courses", on_delete=models.CASCADE
    )
    course_number = models.IntegerField(unique=True)
    group_number = models.IntegerField()
    teacher = models.ForeignKey(
        Teacher, related_name="courses", on_delete=models.CASCADE
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    first_day = models.CharField(max_length=32)
    second_day = models.CharField(max_length=32)

    def __str__(self) -> str:
        return f"Course({self.name[:10]}...)"


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
