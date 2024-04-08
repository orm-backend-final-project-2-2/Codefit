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
