from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import mixins

from helpers.exceptions import BadRequestException
from helpers.responses import AppResponse
from user.models import UserTasks, Users
from user.permissions import EmployerPermission
from .serializers import TaskDetailSerializer, TaskSerializer
from .models import Tasks
from rest_framework.filters import OrderingFilter


class UserTaskViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """User Task ViewSet"""

    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        return self.queryset.filter(users__user=self.request.user)


class EmployerTaskViewSet(viewsets.ModelViewSet):
    """Employer Task ViewSet"""

    queryset = Tasks.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [EmployerPermission]
    filter_backends = [OrderingFilter]
    ordering_fields = ["_created", "due_date"]

    def get_queryset(self):
        query = super().get_queryset().prefetch_related("users", "users__user")

        assignee = self.request.query_params.get("assignee")
        if assignee:
            query = query.filter(users__user=assignee)

        status = self.request.query_params.get("status")
        if status:
            query = query.filter(status=status)

        return query

    @action(detail=True, methods=["post"], url_path="assign-task")
    def assign_task(self, request, pk):
        task = self.get_object()
        user_id = request.data.get("user")
        user = Users.objects.filter(id=user_id).first()
        if not user:
            raise BadRequestException("User is required")

        with transaction.atomic():
            user_task = UserTasks.objects.create(user=user, task=task)
            task.users.add(user_task)
            task.save()

        return AppResponse("Task assigned successfully")
