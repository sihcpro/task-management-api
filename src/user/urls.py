from rest_framework import routers

from .views import LoginAPIView

router = routers.DefaultRouter()

router.register(r"v1/login", LoginAPIView, basename="login")
