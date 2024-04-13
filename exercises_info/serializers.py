from account.models import CustomUser as User
from exercises_info.models import ExercisesInfo, FocusArea
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from utils.enums import FocusAreaEnum


class FocusAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusArea
        fields = "__all__"
        read_only_fields = ["id"]


class ExercisesInfoSerializer(serializers.ModelSerializer):
    focus_areas = FocusAreaSerializer(many=True)
    username = serializers.CharField(source="author.username", read_only=True)

    def create(self, validated_data):
        focus_areas_data = validated_data.pop("focus_areas")

        exercises_info = ExercisesInfo.objects.create(**validated_data)
        for focus_area_data in focus_areas_data:
            focus_area = FocusArea.objects.create(**focus_area_data)
            exercises_info.focus_areas.add(focus_area)
        return exercises_info

    def update(self, instance, validated_data):
        focus_areas_data = validated_data.pop("focus_areas")

        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.video = validated_data.get("video", instance.video)
        instance.save()

        instance.focus_areas.clear()

        for focus_area_data in focus_areas_data:
            focus_area = FocusArea.objects.create(**focus_area_data)
            instance.focus_areas.add(focus_area)
        return instance

    def validate(self, data):
        validators = {
            "focus_areas": self.validate_focus_areas,
        }

        for attr, validator in validators.items():
            data[attr] = validator(data.get(attr, None))

        return data

    def validate_focus_areas(self, attr_data):
        if not attr_data:
            raise ValidationError("Focus areas are required.")

        valid_focus_area_names = [enum.value for enum in FocusAreaEnum]

        for focus_area_data in attr_data:
            if focus_area_data.get("focus_area") not in [
                enum.value for enum in FocusAreaEnum
            ]:
                raise ValidationError("Invalid focus area name.")

        return attr_data

    class Meta:
        model = ExercisesInfo
        fields = ["title", "author", "username", "description", "video", "focus_areas"]
        read_only_fields = ["author", "username"]
