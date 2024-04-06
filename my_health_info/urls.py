from django.urls import path, include
from my_health_info.views import MyHealthInfoViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"my-health-info", MyHealthInfoViewSet, basename="my-health-info")

urlpatterns = [
    path("", include(router.urls)),
]
