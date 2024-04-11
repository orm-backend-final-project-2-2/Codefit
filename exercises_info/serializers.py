from account.models import CustomUser as User
from exercises_info.models import ExercisesInfo
from rest_framework import serializers
from utils.enums import FocusAreaEnum


class FocusAreaSerializer(serializers.ChoiceField):
    def __init__(self, **kwargs):
        super().__init__(choices=FocusAreaEnum.choices(), **kwargs)

    def to_internal_value(self, data):
        if data not in [choice[0] for choice in self.choices]:
            self.fail("invalid_choice", input=data)
        return FocusAreaEnum[data]

    def to_representation(self, value):
        return value.name


class ExercisesInfoSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    )
    focus_areas = FocusAreaSerializer(
        many=True,
        required=True,
        min_length=1,
        error_messages={"min_length": "최소 1개 이상 선택해주세요."},
    )

    class Meta:
        model = ExercisesInfo
        fields = [
            "id",
            "author",
            "title",
            "description",
            "video",
            "focus_areas",
        ]
        read_only_fields = ["author"]
