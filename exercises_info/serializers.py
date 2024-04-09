from account.models import CustomUser as User
from exercises_info.models import ExercisesInfo
from rest_framework import serializers


class ExercisesInfoSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    )

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
