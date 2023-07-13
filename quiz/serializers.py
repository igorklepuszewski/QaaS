from email.headerregistry import Address

from rest_framework import serializers

from quiz.models import Answer, Question, Quiz, Vote
from user.models import User
from user.serializers import UserSerializer


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
    participants = UserSerializer(many=True, required=False)
    invitees = UserSerializer(many=True)
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ["id", "name", "creator", "questions", "participants", "invitees"]
        read_only_fields = ["creator", "participants"]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        invitees_data = validated_data.pop("invitees", [])
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            answers_data = question_data.pop("answers", [])
            question = Question.objects.create(quiz=quiz, **question_data)

            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        def create_users(data):
            users = set()
            for value in data:
                email = value.get("email")
                user = User.objects.filter(email=email).first()
                if not user:
                    username = Address(addr_spec=email).username
                    user = User.objects.create_user(email=email, username=username)
                users.add(user)
            return users

        quiz.invitees.add(*create_users(invitees_data))
        quiz.save()

        self._validated_data = validated_data

        return quiz


class VoteSerializer(serializers.ModelSerializer):
    participant = UserSerializer()
    answer = AnswerSerializer()

    class Meta:
        model = Vote
        fields = ["id", "participant", "answer"]


class QuizSubmissionSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    answers_id = serializers.ListField(child=serializers.IntegerField())


class QuizCheckProgressSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()


class QuizUsageSerializer(serializers.Serializer):
    date = serializers.DateField()

    FORMAT_CHOICES = (
        ("json", "JSON"),
        ("csv", "CSV"),
    )
    format = serializers.ChoiceField(choices=FORMAT_CHOICES, default="json")
