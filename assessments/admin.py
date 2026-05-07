import json

from django.contrib import admin
from django.utils.html import format_html
from .models import Assessments, PatientReevaluation, SoapModality, Soaps

@admin.register(Assessments)
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
        "pretty_section_1_markers",
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
                    "pretty_section_1_markers",
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
                    "red_flags",
                    "yellow_flags",
                    "contraindications",
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
                    "first_chiropractic",
                    "cranial_nerves",
                    "cerebellar",
                    "spinal_cord",
                    "nerve_root",
                    "peripheral",
                    "pathological",
                    "orthopedic_assessment",
                    "second_chiropractic",
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
            {"fields": ("is_discharged", "reason_for_discharge", "discharge_remarks")},
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

    # =========================================
    # Section 1 Anatomy Markers Display
    # =========================================
    def pretty_section_1_markers(self, obj):
        if not obj.section_1_anatomy_markers:
            return "No markers"

        formatted = json.dumps(obj.section_1_anatomy_markers, indent=2)

        return format_html(
            "<div style='max-height:200px; overflow:auto; background:#111; color:#0f0; padding:10px; border-radius:6px;'>"
            "<pre style='margin:0; white-space: pre-wrap;'>{}</pre>"
            "</div>",
            formatted,
        )

    pretty_section_1_markers.short_description = "Section 1 Anatomy Markers"

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


# =========================================
# Inline: Soap Modality
# =========================================
class SoapModalityInline(admin.TabularInline):
    model = SoapModality
    extra = 1
    fields = ("modality", "location", "settings", "duration_intensity")


# =========================================
# SOAP Admin
# =========================================
@admin.register(Soaps)
class SoapsAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "assessment",
        "student",
        "evaluator",
        "created_at",
        "next_appointment",
        "is_soap_signed",
    )

    list_filter = (
        "is_soap_signed",
        "created_at",
        "next_appointment",
    )

    search_fields = (
        "assessment__patient_name",
        "assessment__file_number",
        "student__user__username",
        "evaluator__user__username",
    )

    autocomplete_fields = (
        "assessment",
        "student",
        "evaluator",
        "soap_signed_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "pretty_markers",
    )

    inlines = [SoapModalityInline]

    fieldsets = (
        (
            "Assessment Link",
            {"fields": ("assessment",)},
        ),
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
            "Vitals",
            {
                "fields": (
                    "soap_pulse",
                    "soap_respiratory",
                    "soap_systolic_bp",
                    "soap_diastolic_bp",
                )
            },
        ),
        (
            "SOAP Notes",
            {
                "fields": (
                    "subjective",
                    "objective",
                    "soap_assessment",
                    "plan",
                )
            },
        ),
        (
            "Treatment",
            {
                "fields": (
                    "patient_tolerated_treatment_well",
                    "patient_improved_with_treatment",
                    "pain_after_treatment",
                    "adverse_reactions_to_treatment",
                    "notes",
                )
            },
        ),
        (
            "Markers",
            {
                "fields": ("pretty_markers",),  # 👈 here
            },
        ),
        (
            "Follow Up",
            {"fields": ("next_appointment",)},
        ),
        (
            "Sign Off",
            {
                "fields": (
                    "is_soap_signed",
                    "soap_signed_by",
                    "soap_signed_at",
                )
            },
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

    # =========================================
    # Pretty Markers Display
    # =========================================
    def pretty_markers(self, obj):
        if not obj.markers:
            return "No markers"

        formatted = json.dumps(obj.markers, indent=2)

        return format_html(
            "<div style='max-height:200px; overflow:auto; background:#111; color:#0f0; padding:10px; border-radius:6px;'>"
            "<pre style='margin:0; white-space: pre-wrap;'>{}</pre>"
            "</div>",
            formatted,
        )

    pretty_markers.short_description = "Markers"

    # =========================================
    # Auto set created_by and updated_by
    # =========================================
    def save_model(self, request, obj, form, change):
        if request.user.is_authenticated and hasattr(request.user, "profile"):
            profile = request.user.profile

            if not change and obj.created_by is None:
                obj.created_by = profile

            obj.updated_by = profile

        super().save_model(request, obj, form, change)


# =========================================
# Soap Modality Admin (standalone view)
# =========================================
@admin.register(SoapModality)
class SoapModalityAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "soap",
        "modality",
        "location",
    )

    list_filter = ("modality",)

    search_fields = (
        "soap__assessment__patient_name",
        "location",
    )

    autocomplete_fields = ("soap",)


# =========================================
# Patient Reevaluation Admin
# =========================================
@admin.register(PatientReevaluation)
class PatientReevaluationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "assessment",
        "student",
        "evaluator",
        "date_of_reevaluation",
        "next_reevaluation",
        "created_at",
        "is_reevaluation_signed",
    )

    list_filter = (
        "is_reevaluation_signed",
        "date_of_reevaluation",
        "next_reevaluation",
        "created_at",
    )

    search_fields = (
        "assessment__patient_name",
        "assessment__file_number",
        "student__user__username",
        "evaluator__user__username",
    )

    autocomplete_fields = (
        "assessment",
        "student",
        "evaluator",
        "reevaluation_signed_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Assessment Link",
            {"fields": ("assessment",)},
        ),
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
            "Reevaluation Details",
            {
                "fields": (
                    "date_of_reevaluation",
                    "current_status",
                    "physical_examination",
                    "diagnosis",
                    "treatment_plan",
                    "outcome_measures",
                )
            },
        ),
        (
            "Follow Up",
            {"fields": ("next_reevaluation",)},
        ),
        (
            "Sign Off",
            {
                "fields": (
                    "is_reevaluation_signed",
                    "reevaluation_signed_by",
                    "reevaluation_signed_at",
                )
            },
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

    # =========================================
    # Auto set created_by and updated_by
    # =========================================
    def save_model(self, request, obj, form, change):
        if request.user.is_authenticated and hasattr(request.user, "profile"):
            profile = request.user.profile

            if not change and obj.created_by is None:
                obj.created_by = profile

            obj.updated_by = profile

        super().save_model(request, obj, form, change)
