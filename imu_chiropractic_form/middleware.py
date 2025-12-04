import re
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to access any page
    except those defined in settings.LOGIN_EXEMPT_URLS.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Compile regex patterns once
        self.exempt_urls = [
            re.compile(url) for url in getattr(settings, "LOGIN_EXEMPT_URLS", [])
        ]

    def __call__(self, request):
        # If the user is not authenticated
        if not request.user.is_authenticated:
            path = request.path_info.lstrip("/")
            # Check if the URL matches any exempt patterns
            if not any(url.match(path) for url in self.exempt_urls):
                # Redirect to login page with ?next=original_path
                return redirect(f"{settings.LOGIN_URL}?next=/{path}")
        response = self.get_response(request)
        return response
