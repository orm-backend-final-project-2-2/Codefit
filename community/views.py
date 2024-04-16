from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer, CommentSerializer
from .models import Post, Comment
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_permissions(self):
        actions = {
            "create": [IsAuthenticated],
            "partial_update": [IsAuthenticated],
            "destroy": [IsAuthenticated],
        }

        permission_classes = actions.get(self.action, [AllowAny])
        return [permisson() for permisson in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
