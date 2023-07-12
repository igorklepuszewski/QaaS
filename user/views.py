from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from email.headerregistry import Address
from user.models import Role, User
from rest_framework.authtoken.models import Token
from invitations.utils import get_invitation_model
from rest_framework.views import APIView

from user.serializers import UserTokenSerializer
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions

# Create your views here.


@api_view(["GET"])
def user_signup(request):
    Invitation = get_invitation_model()
    print(Invitation)
    email = request.session["account_verified_email"]
    User = get_user_model()
    user = User.objects.filter(email=email).first()
    if not user:
        username = Address(addr_spec=email).username
        user = User.objects.create_user(email=email, username=username)
    user.roles.add(Role.PARTICIPANT)
    user.save()
    return Response({"email": email}, status=200)


class WhoAmI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response({"message": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return super().handle_exception(exc)

    def get(self, request):
        if not request.user.check_role(Role.ADMIN):
            return Response(
                {"message": "You are not an admin"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UserTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, email=serializer.validated_data["email"])
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": str(token)}, status=200)
