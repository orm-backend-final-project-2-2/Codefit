from rest_framework import viewsets
from exercises_info.serializers import ExercisesInfoSerializer
from exercises_info.models import ExercisesInfo
from rest_framework import permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class ExercisesInfoViewSet(viewsets.ModelViewSet):
    queryset = ExercisesInfo.objects.all()
    serializer_class = ExercisesInfoSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    # 운동 정도 리스트를 모든 사용자가 볼 수 있도록 허용
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # 운동 정보를 모든 사용자가 볼 수 있도록 허용
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # 운동 정보를 생성할 때는 관리자만 가능하도록 허용
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    # 운동 정보를 수정할 때는 관리자만 가능하도록 허용
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    # 운동 정보를 삭제할 때는 관리자만 가능하도록 허용
    def destroy(self, request, *args, **kwargs):
        self.permission_classes = [permissions.IsAdminUser]
        return super().destroy(request, *args, **kwargs)
