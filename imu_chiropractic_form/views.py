import logging
from django.db.models import F
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .utils import get_client_ip

auth_logger = logging.getLogger("auth")


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
        ip = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "unknown")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            auth_logger.info(
                "LOGIN SUCCESS | user=%s | user_id=%s | ip=%s | ua=%s",
                user.username,
                user.id,
                ip,
                user_agent,
            )

            return redirect("/assessments/")

        auth_logger.warning(
            "LOGIN FAILED | username=%s | ip=%s | ua=%s",
            username,
            ip,
            user_agent,
        )

        messages.error(request, "Invalid username or password")
        return render(request, self.template_name)


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            auth_logger.info(
                "LOGOUT | user=%s | user_id=%s | ip=%s",
                request.user.username,
                request.user.id,
                get_client_ip(request),
            )
        logout(request)
        return redirect("login")
