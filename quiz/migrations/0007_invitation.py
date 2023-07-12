# Generated by Django 4.2.3 on 2023-07-10 21:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("quiz", "0006_rename_invitee_quiz_invitees"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invitation",
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
                (
                    "accepted",
                    models.BooleanField(default=False, verbose_name="accepted"),
                ),
                (
                    "key",
                    models.CharField(max_length=64, unique=True, verbose_name="key"),
                ),
                ("sent", models.DateTimeField(null=True, verbose_name="sent")),
                (
                    "email",
                    models.EmailField(max_length=254, verbose_name="e-mail address"),
                ),
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="created"
                    ),
                ),
                (
                    "inviter",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quiz_invitations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "quiz",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="quiz.quiz"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]