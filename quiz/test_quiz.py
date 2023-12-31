# Generated by CodiumAI
from django.test import RequestFactory
from pytest_mock import mocker
from quiz.models import Quiz
from quiz.models import Answer
from quiz.views import QuizSubmissionView
from rest_framework.test import force_authenticate
from rest_framework import status

import pytest

from user.models import User


class TestQuizSubmissionView:
    def setup_method(self, test_method):
        self.user, _ = User.objects.get_or_create(
            email="test@test.com", username="test"
        )
        self.factory = RequestFactory()

    @pytest.mark.django_db
    def test_valid_quiz_submission(self):
        quiz = Quiz.objects.create(name="Test Quiz", creator=self.user)
        quiz.participants.add(self.user)
        self.question = mocker.MagicMock()
        answer1 = Answer.objects.create(
            text="Answer 1", is_correct=True, question=self.question
        )
        answer2 = Answer.objects.create(
            text="Answer 2", is_correct=False, question=self.question
        )
        data = {"quiz_id": quiz.id, "answers_id": [answer1.id, answer2.id]}
        request = self.factory.post("/quiz-submission/", data=data, format="json")
        force_authenticate(request, user=self.user)
        response = QuizSubmissionView.as_view()(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"message": "Quiz submission successful"}

    @pytest.mark.django_db
    def test_invalid_quiz_id_submission(self):
        answer1 = Answer.objects.create(
            text="Answer 1", is_correct=True, question=self.question
        )
        data = {"quiz_id": 999, "answers_id": [answer1.id]}
        request = self.factory.post("/quiz-submission/", data=data, format="json")
        force_authenticate(request, user=self.user)
        response = QuizSubmissionView.as_view()(request)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"message": "Not found."}

    @pytest.mark.django_db
    def test_invalid_answer_id_submission(self):
        quiz = Quiz.objects.create(name="Test Quiz", creator=self.user)
        quiz.participants.add(self.user)
        data = {"quiz_id": quiz.id, "answers_id": [999]}
        request = self.factory.post("/quiz-submission/", data=data, format="json")
        force_authenticate(request, user=self.user)
        response = QuizSubmissionView.as_view()(request)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"message": "Not found."}

    @pytest.mark.django_db
    def test_no_answers_submission(self):
        quiz = Quiz.objects.create(name="Test Quiz", creator=self.user)
        quiz.participants.add(self.user)
        data = {"quiz_id": quiz.id, "answers_id": []}
        request = self.factory.post("/quiz-submission/", data=data, format="json")
        force_authenticate(request, user=self.user)
        response = QuizSubmissionView.as_view()(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"answers_id": ["This list may not be empty."]}

    @pytest.mark.django_db
    def test_non_participant_submission(self):
        quiz = Quiz.objects.create(name="Test Quiz", creator=self.user)
        data = {"quiz_id": quiz.id, "answers_id": []}
        request = self.factory.post("/quiz-submission/", data=data, format="json")
        force_authenticate(request, user=self.user2)
        response = QuizSubmissionView.as_view()(request)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {"message": "You are not a participant of this quiz"}
