"""
URL configuration for qaas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from rest_framework import routers

from quiz.views import (
    QaasUsageView,
    QuizProgressView,
    QuizScoresView,
    QuizSubmissionView,
    QuizViewSet,
    SendQuizResultsView,
    VoteViewSet,
)
from user.views import UserViewSet

router = routers.DefaultRouter()
router.register("quizzes", QuizViewSet)
router.register("votes", VoteViewSet)
router.register("users", UserViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include(router.urls)),
    path("invitations/", include("invitations.urls", namespace="invitations")),
    path("user/", include("user.urls")),
    path("api/quiz-submission/", QuizSubmissionView.as_view(), name="quiz-submission"),
    path("api/quiz-progress/", QuizProgressView.as_view(), name="quiz-progress"),
    path("api/quiz-scores/", QuizScoresView.as_view(), name="quiz-scores"),
    path("api/usage/", QaasUsageView.as_view(), name="qaas-usage"),
    path(
        "api/send-quiz-result/<int:quiz_id>/",
        SendQuizResultsView.as_view(),
        name="send-quiz-results",
    ),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
