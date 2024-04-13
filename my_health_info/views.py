from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from my_health_info.models import HealthInfo, Routine, Routine_Like
from my_health_info.serializers import HealthInfoSerializer, RoutineSerializer
from rest_framework.exceptions import (
    MethodNotAllowed,
    NotFound,
    ValidationError,
    NotAuthenticated,
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.utils import timezone
from my_health_info.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action


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
    """

    queryset = Routine.objects.filter(is_deleted=False)
    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = RoutineSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    ordering_fields = ["like_count"]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.order_queryset(queryset)

        return queryset

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

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def perform_create(self, serializer):
        """루틴 정보 생성 시 author 정보를 추가"""
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

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
        return Response(
            data={"like_count": f"{routine.like_count}"}, status=status.HTTP_201_CREATED
        )
