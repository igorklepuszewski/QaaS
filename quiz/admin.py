from django.contrib import admin

from quiz.models import Answer, Question, Quiz, Vote

# Register your models here.

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Vote)
