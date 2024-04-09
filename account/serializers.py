from rest_framework import serializers
from account.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "profile_picture", "age"]
        read_only_fields = ["email"]
