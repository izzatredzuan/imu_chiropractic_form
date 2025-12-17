from django.contrib import admin
from .models import Assessments
from django.utils.translation import gettext_lazy as _


class AssessmentsAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = (
        "patient_name",
        "student",
        "evaluator",
        "gender",
        "date_of_birth",
        "systolic_bp",
        "diastolic_bp",
        "is_student_signed",
        "is_section_1_signed",
        "is_section_2_signed",
        "is_section_3_signed",
        "created_at",
        "updated_at",
    )

    # Add search capability for certain fields
    search_fields = (
        "patient_name",
        "student__user__username",
        "evaluator__user__username",
    )

    # Add filters for certain fields in the sidebar (to help filter in the admin)
    list_filter = (
        "gender",
        "is_student_signed",
        "is_section_1_signed",
        "is_section_2_signed",
        "is_section_3_signed",
        "created_at",
        "updated_at",
    )

    # Fields to display in the form when adding/editing an instance
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "patient_name",
                    "gender",
                    "date_of_birth",
                    "pulse",
                    "respiratory",
                    "systolic_bp",
                    "diastolic_bp",
                    "summary",
                    "special_direction",
                ),
            },
        ),
        (
            _("Presenting Complaint"),
            {
                "fields": (
                    "chief_complaint",
                    "history_of_condition",
                    "pain",
                    "aggravating_factors",
                    "relieving_factors",
                    "associated_symptoms",
                    "health_hx_review",
                    "past_illnesses",
                    "family_hx",
                    "psycho_social_hx",
                    "occupational",
                    "diet",
                    "system_review",
                ),
            },
        ),
        (
            _("Sign Offs"),
            {
                "fields": (
                    "is_student_signed",
                    "student_signed_by",
                    "student_signed_at",
                    "is_section_1_signed",
                    "section_1_signed_by",
                    "section_1_signed_at",
                    "special_examination_instruction",
                    "is_section_2_signed",
                    "section_2_signed_by",
                    "section_2_signed_at",
                    "further_diagnostic_procedures",
                    "ptt",
                    "procedures_signed_at",
                    "procedures_signed_by",
                    "is_section_3_signed",
                    "section_3_signed_by",
                    "section_3_signed_at",
                ),
            },
        ),
        (
            _("Neurological & Final"),
            {
                "fields": (
                    "cranial_nerves",
                    "cerebellar",
                    "spinal_cord",
                    "nerve_root",
                    "peripheral",
                    "pathological",
                    "orthopedic_assessment",
                    "third_chiropractic_notes",
                    "imaging",
                    "lab",
                ),
            },
        ),
        (
            _("Meta Information"),
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    # Make fields read-only for certain fields that shouldn't be edited directly
    readonly_fields = ("created_at", "updated_at")

    # Optionally, you can make some fields non-editable in the admin
    def get_readonly_fields(self, request, obj=None):
        # Example: make `student_signed_at` non-editable when `is_student_signed` is True
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.is_student_signed:
            readonly_fields += ("student_signed_at",)
        return readonly_fields


# Register the model and the custom admin class
admin.site.register(Assessments, AssessmentsAdmin)
