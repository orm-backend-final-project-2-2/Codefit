from django.urls import path, include
from community.views import PostViewSet, CommentViewSet
from rest_framework.routers import DefaultRouter
from community import views

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")


urlpatterns = [
    path("", include(router.urls)),
]
