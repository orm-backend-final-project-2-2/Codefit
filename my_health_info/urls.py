from django.urls import path, include
from my_health_info.views import (
    MyHealthInfoViewSet,
    RoutineViewSet,
    UsersRoutineViewSet,
    WeeklyRoutineView,
    RoutineStreakViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"my-health-info", MyHealthInfoViewSet, basename="my-health-info")
router.register(r"routine", RoutineViewSet, basename="routine")
router.register(r"users-routine", UsersRoutineViewSet, basename="users-routine")
router.register(r"routine-streak", RoutineStreakViewSet, basename="routine-streak")

urlpatterns = [
    path("", include(router.urls)),
    path("weekly-routine/", WeeklyRoutineView.as_view(), name="weekly-routine"),
]
