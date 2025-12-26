from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User

import requests

# -----------------------------
# Helper function
# -----------------------------
def is_admin(user):
    return hasattr(user, "profile") and user.profile.role == "admin"


# -----------------------------
# List Users
# -----------------------------
class UserListView(View):
    template_name = "accounts/user_list.html"

    def get(self, request):
        if not is_admin(request.user):
            messages.error(request, "You are not authorized to access this page.")
            return redirect("/assessments") 
        
        return render(request, self.template_name)
