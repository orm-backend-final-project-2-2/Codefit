from rest_framework import serializers
from my_health_info.models import HealthInfo, Routine


class HealthInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthInfo
        fields = ["user", "age", "height", "weight", "bmi", "created_at"]
        read_only_fields = ["user", "bmi", "created_at"]


class RoutineSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Routine
        fields = [
            "author",
            "username",
            "title",
            "created_at",
            "is_deleted",
            "like_count",
        ]
        read_only_fields = ["author", "created_at", "is_deleted", "like_count"]

    def get_username(self, obj):
        # print(obj.author)
        return obj.author.username
