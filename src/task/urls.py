from rest_framework import routers

from .views import EmployerTaskViewSet, UserTaskViewSet

router = routers.DefaultRouter()

router.register(r"v1/my-tasks", UserTaskViewSet)
router.register(r"v1/tasks", EmployerTaskViewSet, basename="employer-task")
