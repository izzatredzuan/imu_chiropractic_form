from django.db.models import F
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views import View


class Home(View):
    def get(self, request):
        return render(
            request,
            "home.html",
        )


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to next page or LOGIN_REDIRECT_URL
            next_url = request.GET.get("next") or settings.LOGIN_REDIRECT_URL
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")
            return render(request, self.template_name)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")
