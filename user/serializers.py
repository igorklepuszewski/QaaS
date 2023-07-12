from rest_framework import serializers

from user.models import User


class UserTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]
        extra_kwargs = {
            "email": {"validators": []},
        }
