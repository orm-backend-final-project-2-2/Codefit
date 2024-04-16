from django.urls import path, include
from community.views import PostViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
]
