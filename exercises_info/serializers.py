from django.contrib.auth.models import User
from exercises_info.models import ExercisesInfo
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class ExercisesInfoSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = ExercisesInfo
        fields = [
            "id",
            "author",
            "title",
            "description",
            "video",
        ]
        read_only_fields = ["author"]
