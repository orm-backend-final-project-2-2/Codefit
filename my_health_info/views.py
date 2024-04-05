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


class MyHealthInfoLastView(APIView): ...
