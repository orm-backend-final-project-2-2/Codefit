from rest_framework import serializers
from my_health_info.models import HealthInfo


class HealthInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthInfo
        fields = ["age", "height", "weight", "bmi", "created_at"]

    ...