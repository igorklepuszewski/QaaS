from rest_framework import serializers


class UserTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
