from django.contrib.auth import get_user_model
from django.dispatch import receiver
from invitations.signals import invite_accepted
from invitations.utils import get_invitation_model

User = get_user_model()
Invitation = get_invitation_model()


@receiver(invite_accepted, sender=Invitation)
def handle_invite_accepted(sender, email, invitation, **kwargs):
    user = User.objects.get(email=email)
    quiz = invitation.quiz
    quiz.participants.add(user)
    quiz.save()
