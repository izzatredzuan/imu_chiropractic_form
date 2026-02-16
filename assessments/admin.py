from django.contrib import admin
from .models import Assessments


class AssessmentsAdmin(admin.ModelAdmin):
    # =====================
    # List view
    # =====================
    list_display = (
        "patient_name",
        "student",
        "evaluator",
        "is_initial_patient_consent_signed",
        "is_section_1_signed",
        "is_section_2_signed",
        "is_section_3_signed",
        "is_section_4_signed",
        "is_treatment_plan_signed",
        "is_discharged",
        "updated_at",
    )

    list_filter = (
        "gender",
        "is_initial_patient_consent_signed",
        "is_section_1_signed",
        "is_section_2_signed",
        "is_section_3_signed",
        "is_section_4_signed",
        "is_treatment_plan_signed",
        "is_discharged",
        "created_at",
    )

    search_fields = (
        "patient_name",
        "student__user__username",
        "evaluator__user__username",
    )

    ordering = ("-updated_at",)

    # =====================
    # Read-only fields
    # =====================
    readonly_fields = (
        "created_at",
        "updated_at",
        "initial_patient_consent_signed_at",
        "section_1_signed_at",
        "section_2_signed_at",
        "section_3_signed_at",
        "section_4_signed_at",
        "treatment_plan_signed_at",
    )

    # =====================
    # Form layout
    # =====================
    fieldsets = (
        (
            "Assignment",
            {
                "fields": (
                    "student",
                    "evaluator",
                )
            },
        ),
        (
            "Initial Patient Consent",
            {
                "fields": (
                    "is_initial_patient_consent_signed",
                    "marketing_consent",
                    "education_consent",
                    "research_consent",
                    "initial_patient_consent_signature",
                    "initial_patient_consent_signed_at",
                )
            },
        ),
        (
            "Section 1 – Initial Assessment",
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
                    "is_section_1_signed",
                    "section_1_signed_by",
                    "section_1_signed_at",
                )
            },
        ),
        (
            "Section 2 – Presenting Complaint",
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
                    "differential_diagnosis",
                    "special_examination_instruction",
                    "is_section_2_signed",
                    "section_2_signed_by",
                    "section_2_signed_at",
                )
            },
        ),
        (
            "Section 3 – Physical & Neurological Examination",
            {
                "fields": (
                    "inspection_posture",
                    "inspection_gait",
                    "inspection_regional",
                    "palpation",
                    "percussion",
                    "instrumentation",
                    "rom_active",
                    "rom_passive",
                    "rom_resisted",
                    "second_chiropractic_notes",
                    "further_diagnostic_procedures",
                    "ptt",
                    "procedures_signed_by",
                    "procedures_signed_at",
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
                    "working_diagnosis",
                    "is_section_3_signed",
                    "section_3_signed_by",
                    "section_3_signed_at",
                )
            },
        ),
        (
            "Section 4 – Problem & Interventions",
            {
                "fields": (
                    "diagnosis",
                    "diagnosis_date",
                    "is_section_4_signed",
                    "section_4_signed_by",
                    "section_4_signed_at",
                )
            },
        ),
        (
            "Section 5 – Treatment Plan",
            {
                "fields": (
                    "phase_1",
                    "phase_2",
                    "phase_3",
                    "is_treatment_plan_signed",
                    "treatment_plan_signed_by",
                    "treatment_plan_signed_at",
                )
            },
        ),
        (
            "Discharge",
            {"fields": ("is_discharged",)},
        ),
        (
            "Meta",
            {
                "fields": (
                    "created_at",
                    "created_by",
                    "updated_at",
                    "updated_by",
                )
            },
        ),
    )

    # =====================
    # Auto set created_by and updated_by
    # =====================
    def save_model(self, request, obj, form, change):
        if request.user.is_authenticated and hasattr(request.user, "profile"):
            profile = request.user.profile

            # Set created_by ONLY on first creation
            if not change and obj.created_by is None:
                obj.created_by = profile

            # Always update updated_by
            obj.updated_by = profile

        super().save_model(request, obj, form, change)


# Register the model and the custom admin class
admin.site.register(Assessments, AssessmentsAdmin)
