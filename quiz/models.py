import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from invitations import app_settings, signals
from invitations.adapters import get_invitations_adapter
from invitations.app_settings import app_settings
from invitations.models import AbstractBaseInvitation

from user.models import User

# Create your models here.


class Quiz(models.Model):
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="quizzes_created"
    )
    participants = models.ManyToManyField(User, related_name="quizzes_participated")
    invitees = models.ManyToManyField(User, related_name="quizess_invited")
    name = models.CharField(verbose_name="quiz_name", max_length=30)
    date_created = models.DateTimeField(verbose_name="date created", auto_now_add=True)

    def __str__(self):
        return f"{self.creator}'s {self.name} quiz"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(
        max_length=60, blank=False, null=False, verbose_name="question_text"
    )

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    text = models.CharField(
        max_length=60, blank=False, null=False, verbose_name="answer_text"
    )
    is_correct = models.BooleanField(verbose_name="is_correct", blank=False, null=False)

    @property
    def votes(self):
        return len(self.votes)

    def __str__(self):
        return f"{self.question} - {self.text}"


class Vote(models.Model):
    participant = models.ForeignKey(
        User, related_name="votes", on_delete=models.CASCADE
    )
    answer = models.ForeignKey(Answer, related_name="votes", on_delete=models.CASCADE)
    date_created = models.DateTimeField(verbose_name="date created", auto_now_add=True)

    def __str__(self):
        return str(self.answer)


class Invitation(AbstractBaseInvitation):
    email = models.EmailField(
        verbose_name=_("e-mail address"),
        max_length=app_settings.EMAIL_MAX_LENGTH,
    )
    created = models.DateTimeField(verbose_name=_("created"), default=timezone.now)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="quiz_invitations",
    )

    @classmethod
    def create(cls, email, inviter=None, **kwargs):
        key = get_random_string(64).lower()
        instance = cls._default_manager.create(
            email=email, key=key, inviter=inviter, **kwargs
        )
        return instance

    def key_expired(self):
        expiration_date = self.sent + datetime.timedelta(
            days=app_settings.INVITATION_EXPIRY,
        )
        return expiration_date <= timezone.now()

    def send_invitation(self, request, **kwargs):
        current_site = get_current_site(request)
        invite_url = reverse(app_settings.CONFIRMATION_URL_NAME, args=[self.key])
        invite_url = request.build_absolute_uri(invite_url)
        ctx = kwargs
        ctx.update(
            {
                "invite_url": invite_url,
                "site_name": current_site.name,
                "email": self.email,
                "key": self.key,
                "inviter": self.inviter,
            },
        )

        email_template = "invitations/email/email_invite"

        get_invitations_adapter().send_mail(email_template, self.email, ctx)
        self.sent = timezone.now()
        self.save()

        signals.invite_url_sent.send(
            sender=self.__class__,
            instance=self,
            invite_url_sent=invite_url,
            inviter=self.inviter,
        )

    def __str__(self):
        return f"Invite: {self.email}"
