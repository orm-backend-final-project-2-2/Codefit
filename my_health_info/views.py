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

    def post(self, request, *args, **kwargs):

        serializer = HealthInfoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        serializer.save(user=request.user)
        return Response(serializer.data, status=201)


class MyHealthInfoLastView(APIView):
    def get(self, request):
        user = request.user

        latest_health_info = (
            HealthInfo.objects.filter(user=user).order_by("-created_at").first()
        )

        serializer = HealthInfoSerializer(latest_health_info)

        return Response(serializer.data)
