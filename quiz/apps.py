from django.apps import AppConfig
from invitations.signals import invite_accepted


class QuizConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "quiz"

    def ready(self):
        from quiz import signals

        invite_accepted.connect(
            signals.handle_invite_accepted,
        )
