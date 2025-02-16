from django.contrib.auth.models import AbstractUser
from django.db import models

from helpers.models import TrackingModel
from .enums import UserRole


class Users(AbstractUser, TrackingModel):
    ROLE = (
        (UserRole.EMPLOYEE.value, "Employee"),
        (UserRole.EMPLOYER.value, "Employer"),
    )

    role = models.CharField(max_length=1, choices=ROLE, default=UserRole.EMPLOYEE.value)

    class Meta:
        managed = True
        db_table = "user"


class UserTasks(TrackingModel):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="tasks")
    task = models.ForeignKey("task.Tasks", on_delete=models.CASCADE, related_name="users")

    class Meta:
        managed = True
        db_table = "user_task"
