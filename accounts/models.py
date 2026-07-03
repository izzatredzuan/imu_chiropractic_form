from . import choices
from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    department_code = models.CharField(
        max_length=20,
        unique=True,
        blank=False,
        null=False,
        help_text="Unique code for department.",
    )
    department_name =  models.CharField(max_length=30, blank=False, null=False)

    class Meta:
        ordering = ["department_name"]

    def __str__(self):
        return f"{self.department_code} - {self.department_name}"


class Profile(models.Model):
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
        choices=choices.ROLE_CHOICES,
        blank=False,  # required in forms
        null=False,  # required in database
        default="student",
    )

    is_admin = models.BooleanField(default=False)
    first_time_password_change = models.BooleanField(default=True)

    # Shared fields
    nricpsprt = models.CharField("IC / Passport", max_length=30, blank=True, null=True)
    # For students, this is the student cohorts. For clinicians, this is department code.
    gender = models.CharField(max_length=10, choices=choices.GENDER_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    personal_email = models.EmailField(blank=True, null=True)
    address_1 = models.CharField(max_length=255, blank=True, null=True)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    address_3 = models.CharField(max_length=255, blank=True, null=True)
    address_4 = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)

    # Business location or campus location for students
    location = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=80, blank=True, null=True)

    # student-specific fields (can be blank for clinicians)
    cohort_code = models.CharField("Cohort Code", max_length=20, choices=choices.COHORT_CODE_CHOICES, blank=True, null=True, help_text="Student cohort code")
    program_description = models.CharField(max_length=50, blank=True, null=True)
    transcript_description = models.CharField(max_length=200, blank=True, null=True)
    advisor_name = models.CharField(max_length=150, blank=True, null=True)
    advisor_email = models.EmailField(blank=True, null=True)

    # clinicians-specific fields (can be blank for students)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="profiles",
        help_text="Clinician department"
    )
    business_unit = models.CharField(max_length=30, blank=True, null=True)

    # Extra fields
    account_creation_date = models.DateTimeField(auto_now_add=True)
    profile_log = models.TextField(blank=True, null=True)
    is_locked = models.BooleanField(default=False)

    class Meta:
        ordering = ["official_name"]

    def __str__(self):
        return f"{self.member_id} - {self.official_name}"
