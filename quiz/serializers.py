from rest_framework import serializers
from quiz.models import Answer, Question, Quiz, Vote
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "question", "text", "is_correct"]
        extra_kwargs = {"question": {"required": False}}


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "quiz", "text", "answers"]
        extra_kwargs = {"quiz": {"required": False}}

    def create(self, validated_data):
        answers_data = validated_data.pop("answers", [])
        question = Question.objects.create(**validated_data)

        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)

        return question


class QuizSerializer(serializers.ModelSerializer):
    creator = UserSerializer(required=False)
    # participants = UserSerializer(many=True)
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ["id", "name", "creator", "questions"]
        read_only_fields = ["creator"]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            answers_data = question_data.pop("answers", [])
            question = Question.objects.create(quiz=quiz, **question_data)

            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        return quiz


class VoteSerializer(serializers.ModelSerializer):
    participant = UserSerializer()
    answer = AnswerSerializer()

    class Meta:
        model = Vote
        fields = ["id", "participant", "answer"]
