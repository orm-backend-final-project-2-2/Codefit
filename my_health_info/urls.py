from django.urls import path, include
from .views import MyHealthInfoView, MyHealthInfoLastView

urlpatterns = [
    path("my_health_info/", MyHealthInfoView.as_view(), name="my_health_info"),
    path(
        "my_health_info/last/",
        MyHealthInfoLastView.as_view(),
        name="my_health_info_last",
    ),
]
