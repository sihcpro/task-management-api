"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from task.urls import router as task_router
from user.views import LoginAPIView
from .swagger import urlpatterns as swagger_urlpatterns

router = DefaultRouter()
router.registry.extend(task_router.registry)

urlpatterns = [
    # path("login/", LoginAPIView.as_view(), name="login"),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
] + swagger_urlpatterns
