import logging
from django.db.models import F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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

            # Force password change on first login
            if user.profile.first_time_password_change:
                return redirect("change_password")

            return redirect("/assessments/")

        auth_logger.warning(
            "LOGIN FAILED | username=%s | ip=%s | ua=%s",
            username,
            ip,
            user_agent,
        )

        messages.error(request, "Invalid username or password")
        return render(request, self.template_name)


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = "change_password.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        user = request.user

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # 1. check current password
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return render(request, self.template_name)

        # 2. check match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, self.template_name)

        # 3. validate password strength (ADD THIS)
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, self.template_name)

        # 4. set new password
        user.set_password(new_password)
        user.save()

        # 5. update flag
        user.profile.first_time_password_change = False
        user.profile.save(update_fields=["first_time_password_change"])

        # 6. keep user logged in
        update_session_auth_hash(request, user)

        messages.success(request, "Password changed successfully.")

        return redirect("/assessments/")
    

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
