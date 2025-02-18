from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import status, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from helpers.responses import AppResponse
from user.serializers import LoginSerializer


class LoginAPIView(views.APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "login.html"

    serializer_class = LoginSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"serializer": LoginSerializer()})

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            print("serializer", serializer, serializer.data["username"])
            user = authenticate(
                username=serializer.data["username"], password=serializer.data["password"]
            )
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return AppResponse(
                    {
                        "success": True,
                        "message": "Login SuccessFully",
                        "data": {"token": token.key},
                    },
                    status=status.HTTP_201_CREATED,
                )
            return AppResponse(
                {"success": False, "message": "Invalid Username and Password"}, status=401
            )
