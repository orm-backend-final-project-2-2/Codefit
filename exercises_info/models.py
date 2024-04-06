from django.db import models
from django.contrib.auth.models import User


class ExercisesInfo(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="exercises_info"
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    video = models.ImageField(upload_to="exercises_info_video/", blank=True)

    def __str__(self):
        return f"{self.title}"
