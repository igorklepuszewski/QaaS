from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from user.views import WhoAmI, user_signup

urlpatterns = [
    path("signup/", user_signup, name="account_signup"),
    path("whoami/", WhoAmI.as_view(), name="whoami"),
]
