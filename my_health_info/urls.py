from django.urls import path, include
from my_health_info.views import MyHealthInfoViewSet, RoutineViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"my-health-info", MyHealthInfoViewSet, basename="my-health-info")
router.register(r"routine", RoutineViewSet, basename="routine")

urlpatterns = [
    path("", include(router.urls)),
]
