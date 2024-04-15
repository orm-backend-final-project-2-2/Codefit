from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from my_health_info.models import (
    HealthInfo,
    Routine,
    Routine_Like,
    UsersRoutine,
    MirroredRoutine,
    ExerciseInRoutine,
    WeeklyRoutine,
)
from my_health_info.serializers import (
    HealthInfoSerializer,
    RoutineSerializer,
    UsersRoutineSerializer,
    WeeklyRoutineSerializer,
)
from rest_framework.exceptions import (
    MethodNotAllowed,
    NotFound,
    ValidationError,
    PermissionDenied,
)
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.utils import timezone
from my_health_info.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from django.db.models import Q
from my_health_info.services import UsersRoutineManagementService


class MyHealthInfoViewSet(viewsets.ModelViewSet):
    """
    내 건강 정보에 대한 ViewSet

    url_prefix: /my_health_info/my_health_info/

    functions:
    - list: GET /my_health_info/my_health_info/
    - create: POST /my_health_info/my_health_info/
    - retrieve: GET /my_health_info/my_health_info/<pk>/
    - last: GET /my_health_info/my_health_info/last/
    """

    http_method_names = ["get", "post"]
    serializer_class = HealthInfoSerializer
    permission_classes = [IsAuthenticated]
    days_to_show = 35

    def get_queryset(self):
        """현재 유저의 건강 정보를 최신순으로 조회"""
        return HealthInfo.objects.filter(user=self.request.user).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        """최근 35일간의 건강 정보를 조회"""
        queryset = self.get_queryset().all()[: self.days_to_show]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """건강 정보 생성 시 user 정보를 추가"""

        last_health_info = self.get_queryset()
        if last_health_info.exists():
            last_health_info = last_health_info.first()
            if last_health_info.created_at.date() == timezone.now().date():
                raise ValidationError("Health info already exists for today")

        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="last", url_name="last")
    def last(self, request, *args, **kwargs):
        """가장 최근 생성된 건강 정보 조회"""
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data)
        raise NotFound("No health info found")


class RoutineViewSet(viewsets.ModelViewSet):
    """
    루틴 정보에 대한 ViewSet

    url_prefix: /my_health_info/routine/

    functions:
    - list: GET /my_health_info/routine/
    - create: POST /my_health_info/routine/
    - retrieve: GET /my_health_info/routine/<pk>/
    - subscribe: POST /my_health_info/routine/<pk>/subscribe/
    """

    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = RoutineSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    ordering_fields = ["like_count"]

    def get_queryset(self):
        return Routine.objects.filter(is_deleted=False)

    def order_queryset(self, queryset):
        base_ordering = ["-created_at"]

        orderings = self.request.query_params.get("ordering", None)

        if not orderings:
            return queryset.order_by(*base_ordering)

        orderings = orderings.split(",")
        orderings = [
            ordering
            for ordering in orderings
            if ordering.lstrip("-") in self.ordering_fields
        ]
        orderings += base_ordering

        queryset = queryset.order_by(*orderings)

        return queryset

    def search_queryset(self, queryset):
        author__id = self.request.query_params.get("author__id", None)

        if not author__id:
            return queryset

        queryset = queryset.filter(Q(author__id=author__id))

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.search_queryset(queryset)
        queryset = self.order_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def perform_create(self, serializer):
        exercises_in_routine_data = serializer.validated_data.pop(
            "exercises_in_routine", []
        )

        routine = serializer.save(author=self.request.user)

        mirrored_routine = MirroredRoutine.objects.create(
            title=routine.title,
            author_name=routine.author.username,
            original_routine=routine,
        )

        for exercise_data in exercises_in_routine_data:
            ExerciseInRoutine.objects.create(
                routine=routine, mirrored_routine=mirrored_routine, **exercise_data
            )

        service = UsersRoutineManagementService(
            user=self.request.user, routine=serializer.instance
        )

        service.user_create_routine(mirrored_routine=mirrored_routine)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        if request.data.get("exercises_in_routine"):

            ExerciseInRoutine.objects.filter(routine=instance).update(routine=None)

            last_mirrored_routine = instance.mirrored_routine.last()
            last_mirrored_routine.original_routine = None
            last_mirrored_routine.save()

            new_mirrored_routine = MirroredRoutine.objects.create(
                title=instance.title,
                author_name=instance.author.username,
                original_routine=instance,
            )

            exercises_in_routine_data = serializer.validated_data.pop(
                "exercises_in_routine", []
            )

            new_exercise_in_routines = [
                ExerciseInRoutine(
                    routine=instance,
                    mirrored_routine=new_mirrored_routine,
                    **exercise_data,
                )
                for exercise_data in exercises_in_routine_data
            ]
            ExerciseInRoutine.objects.bulk_create(new_exercise_in_routines)

            subscribers = list(instance.subscribers.all())
            for users_routine in subscribers:
                if users_routine.user.id == instance.author.id:
                    users_routine.mirrored_routine = new_mirrored_routine
                else:
                    users_routine.need_update = True

            UsersRoutine.objects.bulk_update(
                subscribers, ["mirrored_routine", "need_update"]
            )

        serializer.save()

        data = self.get_serializer(instance).data

        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        authors_users_routine = instance.subscribers.filter(
            user=instance.author
        ).first()
        authors_users_routine.delete()

        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        url_path="like",
        url_name="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request, *args, **kwargs):
        routine = self.get_object()
        user = request.user

        if Routine_Like.objects.filter(routine=routine, user=user).exists():
            raise MethodNotAllowed("Already liked")

        Routine_Like.objects.create(routine=routine, user=user)

        routine.like_count += 1

        return Response(
            data={"like_count": f"{routine.like_count}"}, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, *args, **kwargs):
        routine = self.get_object()
        user = request.user
        service = UsersRoutineManagementService(user=user, routine=routine)

        users_routine = service.user_subscribe_routine()

        data = UsersRoutineSerializer(users_routine).data

        return Response(data, status=status.HTTP_201_CREATED)


class UsersRoutineViewSet(viewsets.ModelViewSet):
    """
    유저의 루틴 정보에 대한 ViewSet

    url_prefix: /my_health_info/users_routine/

    functions:
    - list: GET /my_health_info/users_routine/
    - retrieve: GET /my_health_info/users_routine/<pk>/
    - unsubscribe: DELETE /my_health_info/users_routine/<pk>/unsubscribe/
    """

    http_method_names = ["get", "delete"]
    serializer_class = UsersRoutineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UsersRoutine.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class WeeklyRoutineView(APIView):
    """
    유저의 주간 루틴 정보에 대한 View

    url_prefix: /my_health_info/weekly_routine/

    functions:
    - get: GET /my_health_info/weekly_routine/
    - post: POST /my_health_info/weekly_routine/
    - patch: PATCH /my_health_info/weekly_routine/
    - delete: DELETE /my_health_info/weekly_routine/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """유저의 주간 루틴 정보 조회"""
        user = request.user
        weekly_routines = WeeklyRoutine.objects.filter(user=user)
        serializer = WeeklyRoutineSerializer(weekly_routines, many=True)

        return Response(serializer.data)
