import csv
import io
import json
from datetime import datetime

import django_filters.rest_framework
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from invitations.utils import get_invitation_model

# Create your views here.
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from quiz.models import Answer, Question, Quiz, Vote
from quiz.serializers import (
    QuizCheckProgressSerializer,
    QuizSerializer,
    QuizSubmissionSerializer,
    QuizUsageSerializer,
    VoteSerializer,
)
from user.models import Role, User


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    lookup_field = "pk"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply additional filtering based on your requirements
        # Example: Filter by a field based on a query parameter
        creator = self.request.query_params.get("creator")
        if creator:
            queryset = queryset.filter(creator__email=creator)

        paricipant = self.request.query_params.get("participant")
        if paricipant:
            queryset = queryset.filter(participants__email=paricipant)

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name=name)

        return queryset

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
        Invitation = get_invitation_model()

        def send_invite(email):
            invite = Invitation.create(
                email, inviter=request.user, quiz=serializer.instance
            )
            invite.send_invitation(request)

        # to be bulksend https://django-invitations.readthedocs.io/en/latest/usage.html
        for invitee in serializer.data["invitees"]:
            send_invite(invitee["email"])

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def list(self, request, *args, **kwargs):
        # Filter the queryset based on the creator
        queryset = self.get_queryset()
        if not request.user.check_role(Role.ADMIN):
            queryset = queryset.filter(
                Q(creator=request.user) | Q(participants=request.user)
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not request.user.check_role(Role.ADMIN):
            if not Q(creator=request.user) & Q(participants=request.user):
                return Response(
                    {"message": "You are not allowed to access this quiz"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    lookup_field = "pk"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply additional filtering based on your requirements
        # Example: Filter by a field based on a query parameter
        paricipant = self.request.query_params.get("participant")
        if paricipant:
            queryset = queryset.filter(paricipant__email=paricipant)

        answer = self.request.query_params.get("answer")
        if answer:
            queryset = queryset.filter(answer__id=answer)

        question = self.request.query_params.get("question")
        if question:
            queryset = queryset.filter(answer__question__id=question)

        quiz = self.request.query_params.get("quiz")
        if quiz:
            queryset = queryset.filter(answer__question__quiz__id=quiz)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not request.user.check_role(Role.ADMIN):
            if request.user.check_role(Role.CREATOR):
                queryset = queryset.filter(answer__question__quiz__creator=request.user)
            if request.user.check_role(Role.PARTICIPANT):
                queryset = queryset.filter(
                    answer__question__quiz__participants=request.user
                )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CustomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response({"message": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return super().handle_exception(exc)


class QuizSubmissionView(CustomView):
    def post(self, request):
        serializer = QuizSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            quiz_id = serializer.validated_data.get("quiz_id")
            answers_id = serializer.validated_data.get("answers_id")

            quiz = get_object_or_404(Quiz, id=quiz_id)
            participant = request.user

            if not participant.check_role(Role.PARTICIPANT):
                return Response(
                    {"message": "You do not have the participant role"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if participant not in quiz.participants.all():
                return Response(
                    {"message": "You are not a participant of this quiz"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            for answer_id in answers_id:
                answer = get_object_or_404(Answer, id=answer_id)
                vote = Vote.objects.create(participant=participant, answer=answer)

            # Save the data to the database or perform any other actions

            return Response({"message": "Quiz submission successful"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizProgressView(CustomView):
    def get(self, request):
        serializer = QuizCheckProgressSerializer(data=request.data)
        if serializer.is_valid():
            quiz_id = serializer.validated_data.get("quiz_id")

            quiz = get_object_or_404(Quiz, id=quiz_id)
            user = request.user

            is_creator = user == quiz.creator
            is_participant = user in quiz.participants.all()

            if not is_creator and not is_participant:
                return Response(
                    {
                        "message": "You are neither a creator nor the participant of this quiz"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            questions = quiz.questions.all()
            answered_questions = list()
            for question in questions:
                if not is_creator:
                    if question.answers.filter(votes__participant=user).exists():
                        answered_questions.append(question)
                else:
                    answers = question.answers.all()
                    for answer in answers:
                        if answer.votes.exists():
                            answered_questions.append(question)
                            break

            return Response(
                {
                    "number_of_answered_questions": len(answered_questions),
                    "number_of_all_questions": len(questions),
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizScoresView(CustomView):
    def get(self, request):
        serializer = QuizCheckProgressSerializer(data=request.data)
        if serializer.is_valid():
            quiz_id = serializer.validated_data.get("quiz_id")

            quiz = get_object_or_404(Quiz, id=quiz_id)
            user = request.user

            is_creator = user == quiz.creator

            if not is_creator:
                return Response(
                    {"message": "You are not a creator of this quiz"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            questions = quiz.questions.all()
            participants = quiz.participants.all()
            scores = dict()
            scores["all_questions"] = len(questions)
            for participant in participants:
                participant_score = scores[participant.email] = dict()
                count = 0
                for question in questions:
                    participant_answered = question.answers.filter(
                        votes__participant=participant
                    )
                    is_correct = not (
                        question.answers.filter(votes__participant=participant)
                        .exclude(is_correct=True)
                        .exists()
                    )
                    is_correct = is_correct if participant_answered.exists() else None
                    participant_score[question.id] = {"is_correct": is_correct}
                    if is_correct:
                        count += 1
                participant_score["all_correct"] = count
            return Response(scores)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QaasUsageView(CustomView):
    """
    This can be scheduled to the celery tasks with crontab(hour=23, minute=59),
    that will generate the report.

    Executing the View will first check if the file exists.
    Admin can for instance request a file from previous day,
    if there is no file then the file will be created.
    At the end of the day celery worker should
    override this file with a total usage from that day
    """

    def get(self, request):
        if not request.user.check_role(Role.ADMIN):
            return Response(
                {"message": "You are not an admin"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = QuizUsageSerializer(data=request.data)
        if serializer.is_valid():
            format = serializer["format"]
            date = datetime.strptime(str(serializer["date"].value), "%Y-%m-%d").date()
            quizzes_created = Quiz.objects.filter(date_created__date=date)
            questions_created = Question.objects.filter(quiz__date_created__date=date)
            questions_answered = Question.objects.filter(
                answers__votes__date_created__date=date
            )
            user_added = User.objects.filter(date_joined__date=date)
            dict_data = {
                "date": str(serializer["date"].value),
                "quzzes_created": len(quizzes_created),
                "question_created": len(questions_created),
                "questions_answered": len(questions_answered),
                "user_added": len(user_added),
            }

            if format == "json":
                parsed_data = json.dumps(dict_data)
                name = f"{str(serializer['date'].value)}.json"
            else:
                parsed_data = None
                name = f"{str(serializer['date'].value)}.csv"
                with io.StringIO() as output:
                    writer = csv.DictWriter(
                        output, fieldnames=dict_data.keys(), delimiter=";"
                    )
                    writer.writeheader()
                    writer.writerow(dict_data)
                    parsed_data = output.getvalue()
            storage = FileSystemStorage()
            content = ContentFile(parsed_data, name)
            filename = storage.save(name, content)
            file_url = storage.url(filename)
            return Response({"file_url": file_url})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendQuizResultsView(CustomView):
    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        if not quiz.creator == request.user:
            return Response(
                {"detail": "User is not a creator of that quiz."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Iterate over each participant and send email
        for participant in quiz.participants.all():
            participant_email = participant.email

            count = 0
            questions = quiz.questions.all()
            for question in questions:
                participant_answered = question.answers.filter(
                    votes__participant=participant
                )
                is_correct = not (
                    question.answers.filter(votes__participant=participant)
                    .exclude(is_correct=True)
                    .exists()
                )
                is_correct = is_correct if participant_answered.exists() else None
                if is_correct:
                    count += 1

            # Construct the email content
            subject = f"Quiz {quiz.name} Results"
            message = f"Dear {participant.username},\n\nHere are your quiz results:\n\n{count}/{len(questions)}\n\nThank you for participating in the quiz!\n\nRegards,\nThe QaaS Team"
            from_email = "quiz@example.com"
            recipient_list = [participant_email]

            # Send the email
            send_mail(subject, message, from_email, recipient_list)

        return Response({"msg": "Quiz results sent to participants."})
