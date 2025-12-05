import re
from django.conf import settings
from django.shortcuts import redirect


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to access any page
    except those defined in settings.LOGIN_EXEMPT_URLS.
    Prevents redirect loops for the login page.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Compile regex patterns from settings
        self.exempt_urls = [
            re.compile(url) for url in getattr(settings, "LOGIN_EXEMPT_URLS", [])
        ]
        # Ensure LOGIN_URL itself is exempt to prevent loops
        login_url_path = settings.LOGIN_URL.lstrip("/").rstrip("/")
        self.exempt_urls.append(re.compile(f"^{login_url_path}/?$"))

    def __call__(self, request):
        # Only check for unauthenticated users
        if not request.user.is_authenticated:
            path = request.path_info.lstrip("/").rstrip("/")

            # If path is not in exempt URLs, redirect to login
            if not any(url.match(path) for url in self.exempt_urls):
                # Prevent redirect loop if next is login
                next_url = f"/{path}" if path else "/"
                if next_url.lstrip("/") != settings.LOGIN_URL.lstrip("/"):
                    return redirect(f"{settings.LOGIN_URL}?next={next_url}")

        response = self.get_response(request)
        return response
