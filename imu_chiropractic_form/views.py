from django.db.models import F
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import (
    AnonymousUser,
)
from django.shortcuts import (
    HttpResponseRedirect,
)
from django.urls import reverse


class Home(View):
    def get(self, request):
        return render(
            request,
            "home.html",
        )