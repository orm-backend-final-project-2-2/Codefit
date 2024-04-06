from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from my_health_info.models import HealthInfo
from my_health_info.serializers import HealthInfoSerializer
from rest_framework.exceptions import MethodNotAllowed, NotFound, ValidationError
from rest_framework import viewsets
from rest_framework.decorators import action
from django.utils import timezone


class MyHealthInfoViewSet(viewsets.ModelViewSet):
    """
    내 건강 정보에 대한 VIEWSET

    url_prefix: /my_health_info/my_health_info/

    functions:
    - list: GET /my_health_info/my_health_info/
    - create: POST /my_health_info/my_health_info/
    - retrieve: GET /my_health_info/my_health_info/<pk>/
    - last: GET /my_health_info/my_health_info/last/
    """

    serializer_class = HealthInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """조회 범위를 최근 35일로 제한"""
        days_back = 35
        return HealthInfo.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )[:days_back]

    def list(self, request, *args, **kwargs):
        """최근 35일간의 건강 정보를 조회"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """특정 건강 정보 조회"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """건강 정보 생성 시 user 정보를 추가"""

        last_health_info = self.get_queryset()
        if last_health_info.exists():
            last_health_info = last_health_info.first()
            if last_health_info.created_at.date() == timezone.now().date():
                raise ValidationError("Health info already exists for today")

        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """건강 정보 수정 시도 시 에러 발생"""
        raise MethodNotAllowed("PUT")

    def perform_destroy(self, instance):
        """건강 정보 삭제 시도 시 에러 발생"""
        raise MethodNotAllowed("DELETE")

    @action(detail=False, methods=["get"], url_path="last", url_name="last")
    def last(self, request, *args, **kwargs):
        """가장 최근 생성된 건강 정보 조회"""
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data)
        raise NotFound("No health info found")
