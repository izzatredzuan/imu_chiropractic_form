from django.contrib import admin
from .models import Profile, Department


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Columns shown in the list view
    list_display = (
        "user",
        "member_id",
        "official_name",
        "role",
        "department",
        "cohort_code",
        "location",
        "phone",
        "is_admin",
        "is_locked",
        "account_creation_date",
        "first_time_password_change",
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
        "first_time_password_change",
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
        "department__department_code",
        "department__department_name",
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
                    "first_time_password_change",
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
                    "address_4",
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
                    "department",
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

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "department_code",
        "department_name",
    )

    search_fields = (
        "department_code",
        "department_name",
    )

    ordering = (
        "department_code",
    )