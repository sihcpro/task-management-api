from django.db import models

from helpers.models import TrackingModel
from task.enums import TaskStatus


class Tasks(TrackingModel):
    STATUS = (
        (TaskStatus.IN_PROGRESS.value, "In Progress"),
        (TaskStatus.COMPLETED.value, "Completed"),
    )

    status = models.SmallIntegerField(choices=STATUS, default=TaskStatus.IN_PROGRESS.value)

    title = models.CharField(max_length=255)
    description = models.TextField(default="")

    due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = "task"
