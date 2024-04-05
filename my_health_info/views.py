from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from my_health_info.models import HealthInfo
from my_health_info.serializers import HealthInfoSerializer


class MyHealthInfoView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=403)

        user = request.user
        health_info = HealthInfo.objects.get(user=user)

        serializer = HealthInfoSerializer(health_info)

        return Response(serializer.data)


class MyHealthInfoLastView(APIView):
    def get(self, request):
        user = request.user

        latest_health_info = (
            HealthInfo.objects.filter(user=user).order_by("-created_at").first()
        )

        serializer = HealthInfoSerializer(latest_health_info)

        return Response(serializer.data)
