from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("account.urls")),
    # path("community/", include("community.urls")),
    path("my_health_info/", include("my_health_info.urls")),
    path("exercises_info/", include("exercises_info.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
