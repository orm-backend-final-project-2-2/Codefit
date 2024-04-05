from django.urls import path, include
from .views import MyHealthInfoView

urlpatterns = [
    path("my_health_info/", MyHealthInfoView.as_view(), name="my_health_info"),
]
