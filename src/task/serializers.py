from rest_framework import serializers

from user.models import Users, UserTasks
from .models import Tasks


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ["id", "title", "description", "status", "due_date", "_created", "_updated"]


class UserInTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id", "username", "role"]


class UserTaskSerializer(serializers.ModelSerializer):
    user = UserInTaskSerializer()

    class Meta:
        model = UserTasks
        fields = ["user"]


class TaskDetailSerializer(serializers.ModelSerializer):
    users = UserTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Tasks
        fields = [
            "id",
            "title",
            "description",
            "status",
            "users",
            "due_date",
            "_created",
            "_updated",
        ]
