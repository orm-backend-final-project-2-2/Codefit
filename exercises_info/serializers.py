from account.models import CustomUser as User
from exercises_info.models import ExercisesInfo, FocusArea
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from utils.enums import FocusAreaEnum
from drf_writable_nested import WritableNestedModelSerializer


class FocusAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusArea
        fields = "__all__"
        read_only_fields = ["id"]


class ExercisesInfoSerializer(WritableNestedModelSerializer):
    focus_areas = FocusAreaSerializer(many=True)
    username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = ExercisesInfo
        fields = ["title", "author", "username", "description", "video", "focus_areas"]
        read_only_fields = ["author", "username"]

    def validate_focus_areas(self, attr_data):
        if not attr_data:
            raise ValidationError("Focus areas are required.")
        valid_focus_area_names = [enum.value for enum in FocusAreaEnum]
        for focus_area_data in attr_data:
            focus_area = focus_area_data.get("focus_area")
            if focus_area not in valid_focus_area_names:
                raise ValidationError(f"{focus_area} is not a valid focus area.")
        return attr_data

    def validate(self, data):
        # Apply custom validations
        if "focus_areas" in data:
            self.validate_focus_areas(data["focus_areas"])
        return data
