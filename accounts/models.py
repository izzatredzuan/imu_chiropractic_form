from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    ROLE_CHOICES = (
        ("student", "Student"),
        ("clinician", "Clinician"),
        ("admin", "Admin"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Combined ID for both Students and Clinicians
    member_id = models.CharField(
        max_length=50,
        unique=True,
        blank=False,  # required in forms
        null=False,  # required in database
        help_text="Unique ID for student or clinician.",
    )

    official_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        help_text="Official full name of the user",
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        blank=False,  # required in forms
        null=False,  # required in database
        default="student",
    )

    is_admin = models.BooleanField(default=False)

    # Shared fields
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Extra fields
    account_creation_date = models.DateTimeField(auto_now_add=True)
    profile_log = models.TextField(blank=True, null=True)
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.member_id} - {self.official_name}"
