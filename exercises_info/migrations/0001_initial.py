# Generated by Django 5.0.4 on 2024-04-13 11:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ExercisesAttribute",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("need_set", models.BooleanField(default=False)),
                ("need_rep", models.BooleanField(default=False)),
                ("need_weight", models.BooleanField(default=False)),
                ("need_duration", models.BooleanField(default=False)),
                ("need_speed", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="FocusArea",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("focus_area", models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name="ExercisesInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField(max_length=1000)),
                ("video", models.CharField(max_length=200)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exercises_info",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "exercises_attribute",
                    models.OneToOneField(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exercises_info",
                        to="exercises_info.exercisesattribute",
                    ),
                ),
                (
                    "focus_areas",
                    models.ManyToManyField(
                        blank=True,
                        related_name="exercises_info",
                        to="exercises_info.focusarea",
                    ),
                ),
            ],
        ),
    ]
