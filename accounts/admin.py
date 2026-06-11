from django.contrib import admin
from .models import Profile


from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Columns shown in the list view
    list_display = (
        "user",
        "member_id",
        "official_name",
        "role",
        "department_code",
        "cohort_code",
        "location",
        "phone",
        "is_admin",
        "is_locked",
        "account_creation_date",
    )

    # Filters in the sidebar
    list_filter = (
        "role",
        "gender",
        "is_admin",
        "is_locked",
        "location",
        "country",
        "state",
        "account_creation_date",
    )

    # Searchable fields
    search_fields = (
        "member_id",
        "official_name",
        "user__username",
        "user__first_name",
        "user__last_name",
        "personal_email",
        "phone",
        "nricpsprt",
        "department_code",
        "cohort_code",
        "location",
    )

    # Editable directly from list page
    list_editable = (
        "role",
        "is_admin",
        "is_locked",
    )

    # Read-only fields
    readonly_fields = (
        "account_creation_date",
    )

    # Default ordering
    ordering = (
        "official_name",
    )

    # Detail page layout
    fieldsets = (
        (
            "Account Information",
            {
                "fields": (
                    "user",
                    "member_id",
                    "official_name",
                    "role",
                    "is_admin",
                    "is_locked",
                    "account_creation_date",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "nricpsprt",
                    "gender",
                    "phone",
                    "emergency_contact",
                    "personal_email",
                )
            },
        ),
        (
            "Address",
            {
                "fields": (
                    "address_1",
                    "address_2",
                    "address_3",
                    "postal_code",
                    "city",
                    "state",
                    "country",
                )
            },
        ),
        (
            "Organization Details",
            {
                "fields": (
                    "location",
                    "position",
                )
            },
        ),
        (
            "Student Information",
            {
                "classes": ("collapse",),
                "fields": (
                    "cohort_code",
                    "program_description",
                    "transcript_description",
                    "advisor_name",
                    "advisor_email",
                ),
            },
        ),
        (
            "Clinician Information",
            {
                "classes": ("collapse",),
                "fields": (
                    "department_code",
                    "business_unit",
                ),
            },
        ),
        (
            "Logs",
            {
                "classes": ("collapse",),
                "fields": (
                    "profile_log",
                ),
            },
        ),
    )