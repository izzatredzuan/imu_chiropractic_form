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
        "is_admin",
        "phone",
        "account_creation_date",
        "is_locked",
    )

    # Fields you can filter by on the right-hand sidebar
    list_filter = (
        "official_name",
        "role",
        "is_admin",
        "is_locked",
        "account_creation_date",
    )

    # Fields you can search by
    search_fields = (
        "member_id",
        "user__username",  # search by username
        "official_name",
        "phone",
    )

    # Fields editable directly in the list view
    list_editable = ("role", "is_admin", "phone", "is_locked")

    # Fields that are read-only in the detail page
    readonly_fields = ("account_creation_date",)

    # Organize fields in the detail page
    fieldsets = (
        (
            "User Info",
            {"fields": ("user", "official_name", "member_id", "role", "is_admin")},
        ),  # added official_name
        ("Contact", {"fields": ("phone",)}),
        (
            "Status & Logs",
            {"fields": ("account_creation_date", "is_locked", "profile_log")},
        ),
    )
