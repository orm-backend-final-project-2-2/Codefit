from rest_framework import serializers
from my_health_info.models import (
    HealthInfo,
    Routine,
    ExerciseInRoutine,
    UsersRoutine,
    MirroredRoutine,
    WeeklyRoutine,
    RoutineStreak,
)
from exercises_info.models import ExercisesInfo
from drf_writable_nested import WritableNestedModelSerializer
from exercises_info.serializers import ExercisesInfoSerializer


class HealthInfoSerializer(serializers.ModelSerializer):
    """
    사용자의 건강 정보를 다루는 Serializer
    """

    class Meta:
        """
        HealthInfoSerializer의 Meta 클래스

        모델: HealthInfo

        필드:
        - user: 사용자, read_only
        - age: 나이
        - height: 키
        - weight: 몸무게
        - bmi: BMI, read_only
        - created_at: 생성일, read_only
        """

        model = HealthInfo
        fields = ["user", "age", "height", "weight", "bmi", "created_at"]
        read_only_fields = ["user", "bmi", "created_at"]


class ExerciseInRoutineSerializer(WritableNestedModelSerializer):
    """
    루틴에 포함된 운동 정보를 다루는 Serializer
    """

    exercise_info = ExercisesInfoSerializer(source="exercise", read_only=True)
    exercise = serializers.PrimaryKeyRelatedField(
        queryset=ExercisesInfo.objects.all(), write_only=True
    )

    class Meta:
        """
        ExerciseInRoutineSerializer의 Meta 클래스

        모델: ExerciseInRoutine

        필드:
        - routine: 루틴, read_only
        - exercise_info: 운동 정보
        - exercise: 운동 정보의 PK, write_only
        - order: 운동 순서
        """

        model = ExerciseInRoutine
        fields = ["routine", "exercise", "order", "exercise_info"]
        read_only_fields = ["routine"]


class RoutineSerializer(WritableNestedModelSerializer):
    """
    Routine 모델을 위한 Serializer
    """

    username = serializers.SerializerMethodField()
    exercises_in_routine = ExerciseInRoutineSerializer(many=True)

    class Meta:
        """
        RoutineSerializer의 Meta 클래스

        모델: Routine

        필드:
        - author: 루틴 작성자
        - username: 루틴 작성자의 username
        - title: 루틴 제목
        - created_at: 루틴 생성일
        - is_deleted: 루틴 삭제 여부
        - like_count: 루틴 좋아요 수
        - exercises_in_routine: 루틴에 포함된 운동 정보
        """

        model = Routine
        fields = [
            "author",
            "username",
            "title",
            "created_at",
            "is_deleted",
            "like_count",
            "exercises_in_routine",
        ]
        read_only_fields = [
            "author",
            "username",
            "created_at",
            "is_deleted",
            "like_count",
        ]

    def get_username(self, obj):
        return obj.author.username


class MirroredRoutineSerializer(serializers.ModelSerializer):
    """
    MirroredRoutine 모델을 위한 Serializer
    """

    exercises_in_routine = ExerciseInRoutineSerializer(many=True)

    class Meta:
        """
        MirroredRoutineSerializer의 Meta 클래스

        모델: MirroredRoutine

        필드:
        - title: 루틴 제목, read_only
        - author_name: 루틴 작성자 이름, read_only
        - original_routine: 원본 루틴, read_only
        - exercises_in_routine: 루틴에 포함된 운동 정보, read_only, many
        """

        model = MirroredRoutine
        fields = ["title", "author_name", "original_routine", "exercises_in_routine"]
        read_only_fields = [
            "title",
            "author_name",
            "original_routine",
            "exercises_in_routine",
        ]


class UsersRoutineSerializer(serializers.ModelSerializer):
    """
    사용자의 루틴 정보를 다루는 Serializer
    """

    mirrored_routine = MirroredRoutineSerializer()

    class Meta:
        """
        UsersRoutineSerializer의 Meta 클래스

        모델: UsersRoutine

        필드:
        - user: 사용자, read_only
        - routine: 루틴
        - mirrored_routine: 복제된 루틴
        - need_update: 업데이트 필요 여부
        """

        model = UsersRoutine
        fields = ["user", "routine", "mirrored_routine", "need_update"]
        read_only_fields = ["user", "routine", "need_update", "mirrored_routine"]


class WeeklyRoutineSerializer(serializers.ModelSerializer):
    """
    주간 루틴 정보를 다루는 Serializer
    """

    class Meta:
        """
        WeeklyRoutineSerializer의 Meta 클래스

        모델: WeeklyRoutine

        필드:
        - user: 사용자, read_only
        - users_routine: 사용자의 루틴
        - day_index: 해당 루틴이 적용되는 요일 인덱스
        """

        model = WeeklyRoutine
        fields = ["user", "users_routine", "day_index"]
        read_only_fields = ["user"]

    def validate(self, data):
        """
        유효성 검사를 수행하는 메서드

        - day_index가 0~6 사이의 값인지 확인
        """

        if not 0 <= data["day_index"] <= 6:
            raise serializers.ValidationError("day_index는 0~6 사이의 값이어야 합니다.")
        return data


class RoutineStreakSerializer(serializers.ModelSerializer):
    """
    루틴 수행 여부를 다루는 Serializer
    """

    class Meta:
        """
        RoutineStreakSerializer의 Meta 클래스

        모델: RoutineStreak

        필드:
        - id: 루틴 수행 여부의 PK, read_only
        - user: 사용자, read_only
        - mirrored_routine: 수행된 복제된 루틴, read_only
        - date: 날짜, read_only
        """

        model = RoutineStreak
        fields = ["id", "user", "mirrored_routine", "date"]
        read_only_fields = ["id", "user", "mirrored_routine", "date"]
