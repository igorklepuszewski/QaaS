from django.contrib import admin

from quiz.models import Answer, Question, Quiz

# Register your models here.

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
