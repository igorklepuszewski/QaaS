from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework import status
from quiz.models import Quiz, Question, Answer, Vote
from quiz.serializers import (
    QuizSerializer,
    QuestionSerializer,
    AnswerSerializer,
    VoteSerializer,
)
from user.models import Role, User


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_role(Role.CREATOR):
            return Response(
                {"detail": "User is not a creator and cannot create quizzes."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer.validated_data["creator"] = request.user

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def list(self, request, *args, **kwargs):
        # Filter the queryset based on the creator
        queryset = self.queryset
        if not request.user.check_role(Role.ADMIN):
            queryset = queryset.filter(creator=request.user)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
