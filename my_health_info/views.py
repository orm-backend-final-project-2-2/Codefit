import datetime
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
    RoutineStreak,
)
from my_health_info.serializers import (
    HealthInfoSerializer,
    RoutineSerializer,
    UsersRoutineSerializer,
    WeeklyRoutineSerializer,
    RoutineStreakSerializer,
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
        """
        건강 정보를 리스트로 반환

        - 최근 35일간의 건강 정보만 조회 가능
        """
        queryset = (
            self.get_queryset()
            .all()
            .filter(
                created_at__gte=timezone.now()
                - timezone.timedelta(days=self.days_to_show)
            )
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        새로운 건강 정보 생성

        이미 오늘의 건강 정보가 존재한다면 400 에러 반환
        """

        last_health_info = self.get_queryset()
        if last_health_info.exists():
            last_health_info = last_health_info.first()
            if last_health_info.created_at.date() == timezone.now().date():
                raise ValidationError("Health info already exists for today")

        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="last", url_name="last")
    def last(self, request, *args, **kwargs):
        """
        가장 최근의 건강 정보 조회

        사용자의 건강 정보가 없다면 404 에러 반환
        """
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
    - partial_update: PATCH /my_health_info/routine/<pk>/
    - subscribe: POST /my_health_info/routine/<pk>/subscribe/
    """

    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = RoutineSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    ordering_fields = ["like_count"]

    def get_queryset(self):
        """
        루틴 정보를 반환, 삭제되지 않은 루틴만 조회
        """
        return Routine.objects.filter(is_deleted=False)

    def order_queryset(self, queryset):
        """
        주어진 쿼리셋을 ordering에 따라 정렬

        기본 ordering은 -created_at
        ordering이 없다면 기본 ordering을 사용

        추가 ordering은 query_params의 ordering 리스트 + 기본 ordering 순으로 배열
        그 후 order_by 함수를 사용하여 정렬
        """
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
        """
        주어진 쿼리셋을 검색어에 따라 필터링

        query_params의 search에 해당하는 필드를 검색어로 포함하는 루틴만 반환

        검색어가 없다면 주어진 쿼리셋 그대로 반환

        Q 객체를 사용하여 검색어에 해당하는 필드를 필터링
        """
        author__id = self.request.query_params.get("author__id", None)

        if not author__id:
            return queryset

        queryset = queryset.filter(Q(author__id=author__id))

        return queryset

    def list(self, request, *args, **kwargs):
        """
        루틴 정보를 리스트로 반환

        주어진 쿼리셋을 검색어와 ordering에 따라 필터링 및 정렬

        그 후 serializer를 사용하여 데이터 반환
        """
        queryset = self.get_queryset()
        queryset = self.search_queryset(queryset)
        queryset = self.order_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        특정 루틴 정보 조회

        주어진 pk에 해당하는 루틴 정보를 반환
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        루틴을 생성하는 로직

        1. validated_data에서 외부 테이블의 데이터를 pop
        2. 루틴을 생성
        3. 루틴을 복제하여 MirroredRoutine 생성
        4. 루틴에 연결된 운동들을 ExerciseInRoutine으로 생성한 후 Routine과 MirroredRoutine에 연결
        5. UsersRoutineManagementService를 통해 UsersRoutine 생성
        """
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
        """
        루틴의 일부를 수정하는 로직

        1. 루틴 인스턴스를 가져옴
        2. 뷰셋과 연결된 serializer를 가져옴
        3. serializer.is_valid()를 통해 데이터 유효성 검사
        4. request.data에 exercises_in_routine이 있다면
        5. ExerciseInRoutine의 Routine을 None으로 수정하여 연결 해제
        6. Routine에 연결된 MirroredRoutine의 original_routine을 None으로 수정하여 연결 해제
        7. 새로운 MirroredRoutine 생성
        8. 새로운 ExerciseInRoutine를 생성하여 Routine과 MirroredRoutine에 연결
        9. Routine의 subscribers를 가져와서 순회
        10. subscriber == author의 경우 mirrored_routine을 새로운 MirroredRoutine으로 수정
        11. subscriber != author의 경우 mirrored_routine을 업데이트하는 대신 need_update를 True로 수정
        12. 나머지 Routine의 정보를 업데이트
        13. 업데이트된 정보를 반환
        """
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
        """
        루틴을 삭제하는 로직

        1. 루틴 인스턴스를 가져옴
        2. 루틴의 author의 UsersRoutine을 가져옴
        3. author의 UsersRoutine의 routine을 None으로 수정
        4. 루틴의 is_deleted를 True로 수정
        5. 204 응답 반환
        """
        instance = self.get_object()

        try:
            authors_users_routine = instance.subscribers.get(user=instance.author)
            authors_users_routine.routine = None
            authors_users_routine.save()
        except:
            raise NotFound("Author's routine not found")

        instance.is_deleted = True
        instance.save()

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
        """
        유저가 루틴을 구독하는 로직

        1. 루틴과 유저 인스턴스를 가져옴
        2. UsersRoutineManagementService를 통해 유저가 루틴을 구독하게 함
        3. 구독된 UsersRoutine을 반환
        """
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
        """
        본인이 소유한 루틴 정보를 반환
        """
        return UsersRoutine.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        유저가 소유한 UsersRoutine 정보를 리스트로 반환
        """
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
    - update: PUT /my_health_info/weekly_routine/
    - delete: DELETE /my_health_info/weekly_routine/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        유저의 주간 루틴 정보 조회

        1. 쿼리셋에서 유저의 주간 루틴 정보를 조회하여 요일 순으로 정렬
        2. WeeklyRoutineSerializer를 사용하여 데이터 반환
        """
        user = request.user
        queryset = WeeklyRoutine.objects.filter(user=user).order_by("day_index")
        serializer = WeeklyRoutineSerializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request):
        """
        유저의 주간 루틴 정보 생성

        1. WeeklyRoutineSerializer를 사용하여 데이터 유효성 검사
        2. WeeklyRoutine들을 생성
        3. 생성된 WeeklyRoutine을 요일 순으로 정렬
        4. 정렬된 WeeklyRoutine을 WeeklyRoutineSerializer를 사용하여 데이터 반환
        """
        serializer = WeeklyRoutineSerializer(data=request.data, many=True)
        if serializer.is_valid():
            if WeeklyRoutine.objects.filter(user=request.user).exists():
                raise PermissionDenied("Weekly routine already exists")
            instances = serializer.save(user=request.user)
            sorted_instances = sorted(instances, key=lambda x: x.day_index)
            sorted_serializer = WeeklyRoutineSerializer(sorted_instances, many=True)
            return Response(sorted_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        유저의 주간 루틴 정보 업데이트

        1. WeeklyRoutineSerializer를 사용하여 데이터 유효성 검사
        2. instances에 유저의 주간 루틴 정보를 조회
        3. 현재 주간 루틴 정보의 요일 인덱스와 새로운 주간 루틴 정보의 요일 인덱스를 비교하여 삭제, 생성, 업데이트할 요일 인덱스 저장
        4. 업데이트 할 인덱스가 있다면 해당 인덱스의 users_routine 정보를 업데이트
        5. 삭제할 인덱스가 있다면 인덱스에 해당하는 주간 루틴 정보 삭제
        6. 생성할 인덱스가 있다면 인덱스에 해당하는 주간 루틴 정보 생성
        7. 업데이트된 주간 루틴 정보를 요일 순으로 정렬
        8. 정렬된 주간 루틴 정보를 WeeklyRoutineSerializer를 사용하여 데이터 반환
        """
        serializer = WeeklyRoutineSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = WeeklyRoutine.objects.filter(user=request.user)

            current_indices = set(instance.day_index for instance in instances)
            new_indices = set(data["day_index"] for data in serializer.validated_data)

            to_delete = current_indices - new_indices
            to_create = new_indices - current_indices
            to_update = current_indices & new_indices

            if to_update:
                for data in serializer.validated_data:
                    if data["day_index"] in to_update:
                        WeeklyRoutine.objects.filter(
                            user=request.user, day_index=data["day_index"]
                        ).update(users_routine=data["users_routine"])
            if to_delete:
                WeeklyRoutine.objects.filter(
                    user=request.user, day_index__in=to_delete
                ).delete()
            if to_create:
                for data in serializer.validated_data:
                    if data["day_index"] in to_create:
                        WeeklyRoutine.objects.create(
                            user=request.user,
                            users_routine=data["users_routine"],
                            day_index=data["day_index"],
                        )

            instances = WeeklyRoutine.objects.filter(user=request.user)

            sorted_instances = sorted(instances, key=lambda x: x.day_index)
            sorted_serializer = WeeklyRoutineSerializer(sorted_instances, many=True)
            return Response(sorted_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        유저의 모든 주간 루틴 정보 삭제

        1. 유저의 주간 루틴 정보를 필터링하여 삭제
        2. 204 응답 반환
        """

        WeeklyRoutine.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoutineStreakViewSet(viewsets.ModelViewSet):
    """
    루틴 수행 여부를 나타내는 ViewSet

    url_prefix: /my_health_info/routine_streak/

    functions:
    - list: GET /my_health_info/routine_streak/
    - create: POST /my_health_info/routine_streak/
    - retrieve: GET /my_health_info/routine_streak/<pk>/
    """

    http_method_names = ["get", "post"]
    serializer_class = RoutineStreakSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        유저의 루틴 수행 여부를 반환
        """
        return RoutineStreak.objects.filter(user=self.request.user)

    def list(self, request):
        """
        루틴 수행 여부를 리스트로 반환

        1. 쿼리셋에서 유저의 루틴 수행 여부를 조회 후 날짜 역순으로 정렬
        2. serializer를 사용하여 데이터 반환
        """
        queryset = RoutineStreak.objects.filter(user=request.user).order_by("-date")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        루틴 수행 여부를 생성

        1. serializer에서 validated_data를 가져옴
        2. validated_data에서 user를 현재 유저로 설정
        3. RoutineStreak을 생성
        """
        validated_data = serializer.validated_data
        validated_data["user"] = self.request.user

        if RoutineStreak.objects.filter(
            user=self.request.user, date=datetime.datetime.now().date()
        ).exists():
            raise ValidationError("Routine streak already exists for today")

        serializer.save()
