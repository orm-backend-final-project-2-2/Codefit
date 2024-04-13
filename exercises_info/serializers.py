from account.models import CustomUser as User
from exercises_info.models import ExercisesInfo, FocusArea
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from utils.enums import FocusAreaEnum
from drf_writable_nested import WritableNestedModelSerializer


class FocusAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusArea
        fields = ["focus_area"]

    def validate_focus_area(self, value):
        valid_focus_area_names = [enum.value for enum in FocusAreaEnum]
        if value not in valid_focus_area_names:
            raise ValidationError(f"{value} is not a valid focus area.")
        return value


class ExercisesInfoSerializer(WritableNestedModelSerializer):
    focus_areas = FocusAreaSerializer(many=True)
    username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = ExercisesInfo
        fields = ["title", "author", "username", "description", "video", "focus_areas"]
        read_only_fields = ["author", "username"]
