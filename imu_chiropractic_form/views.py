import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.views import View
from django.contrib.auth.models import User
from .utils import get_client_ip

from accounts.services import send_reset_password_email

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


class ForgotPasswordView(View):
    template_name = "forgot_password.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username", "").strip()

        user = User.objects.filter(username=username).first()

        if user and user.email:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = request.build_absolute_uri(
                reverse(
                    "reset_password",
                    kwargs={
                        "uidb64": uid,
                        "token": token,
                    },
                )
            )
            send_reset_password_email(user, reset_link)

            auth_logger.info(
                "PASSWORD RESET REQUEST | user=%s | user_id=%s | ip=%s",
                user.username,
                user.id,
                get_client_ip(request),
            )

        messages.success(
            request,
            "If an account with that username exists, a password reset link has been sent to the registered email address.",
        )

        return redirect("forgot_password")


class ResetPasswordView(View):
    template_name = "reset_password.html"

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, token):
            messages.error(request, "This password reset link is invalid or has expired.")
            return redirect("login")

        return render(
            request,
            self.template_name,
            {
                "uidb64": uidb64,
                "token": token,
            },
        )

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, token):
            messages.error(request, "This password reset link is invalid or has expired.")
            return redirect("login")

        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(
                request,
                self.template_name,
                {"uidb64": uidb64, "token": token},
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)

            return render(
                request,
                self.template_name,
                {"uidb64": uidb64, "token": token},
            )

        user.set_password(new_password)
        user.save()

        if hasattr(user, "profile"):
            user.profile.first_time_password_change = False
            user.profile.save(update_fields=["first_time_password_change"])

        auth_logger.info(
            "PASSWORD RESET SUCCESS | user=%s | user_id=%s | ip=%s",
            user.username,
            user.id,
            get_client_ip(request),
        )
        
        messages.success(
            request,
            "Your password has been reset successfully. Please log in."
        )

        return redirect("login")
    

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
