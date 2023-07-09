from django.db import models

from user.models import User

# Create your models here.


class Quiz(models.Model):
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="quizzes_created"
    )
    participants = models.ManyToManyField(User, related_name="quizzes_participated")
    name = models.CharField(verbose_name="quiz_name", max_length=30)

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
