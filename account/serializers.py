from rest_framework import serializers
from account.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=20, min_length=8, write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "profile_picture", "age", "password"]
