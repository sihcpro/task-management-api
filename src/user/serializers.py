from rest_framework import serializers


from .models import Users


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=100, style={"placeholder": "username", "autofocus": True}
    )
    password = serializers.CharField(
        max_length=100, style={"input_type": "password", "placeholder": "password"}
    )
    remember_me = serializers.BooleanField()
