import base64
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.utils import timezone
from accounts.models import Profile
from .models import Assessments, SoapModality, Soaps, PatientReevaluation
from .utils import is_section_complete
from .constants import (
    SECTION_1_FIELDS,
    SECTION_2_FIELDS,
    SECTION_3_FIELDS,
    SECTION_4_FIELDS,
    TREATMENT_PLAN_FIELDS,
)


class AssessmentsListSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    clinician = serializers.CharField(source="evaluator", read_only=True)
    updated_by = serializers.CharField(
        source="updated_by.official_name", read_only=True
    )
    created_by = serializers.CharField(
        source="created_by.official_name", read_only=True
    )

    reason_for_discharge_text = serializers.CharField(
        source="get_reason_for_discharge_display", read_only=True
    )

    is_section_1_complete = serializers.SerializerMethodField()
    is_section_2_complete = serializers.SerializerMethodField()
    is_section_3_complete = serializers.SerializerMethodField()
    is_section_4_complete = serializers.SerializerMethodField()
    is_treatment_plan_complete = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")

    class Meta:
        model = Assessments
        fields = [
            "id",
            "patient_name",
            "file_number",
            "student",
            "clinician",
            "is_section_1_signed",
            "section_1_signed_at",
            "is_section_1_complete",
            "is_section_2_signed",
            "section_2_signed_at",
            "is_section_2_complete",
            "is_section_3_signed",
            "section_3_signed_at",
            "is_section_3_complete",
            "is_section_4_signed",
            "section_4_signed_at",
            "is_section_4_complete",
            "is_treatment_plan_signed",
            "is_treatment_plan_complete",
            "is_discharged",
            "reason_for_discharge",
            "reason_for_discharge_text",
            "discharge_remarks",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        ]

    def get_is_section_1_complete(self, obj):
        return is_section_complete(obj, SECTION_1_FIELDS)

    def get_is_section_2_complete(self, obj):
        return is_section_complete(obj, SECTION_2_FIELDS)

    def get_is_section_3_complete(self, obj):
        return is_section_complete(obj, SECTION_3_FIELDS)

    def get_is_section_4_complete(self, obj):
        return is_section_complete(obj, SECTION_4_FIELDS)

    def get_is_treatment_plan_complete(self, obj):
        return is_section_complete(obj, TREATMENT_PLAN_FIELDS)


class AssessmentSection1And2CreateSerializer(serializers.ModelSerializer):
    evaluator = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(role="clinician"), required=True
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(role="student"), required=True
    )
    section_1_anatomy_markers = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    signature_data = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Assessments
        fields = [
            "student",
            "evaluator",
            # Section 1 – Initial Assessment
            "patient_name",
            "file_number",
            "gender",
            "date_of_birth",
            "pulse",
            "respiratory",
            "systolic_bp",
            "diastolic_bp",
            "summary",
            "special_direction",
            "section_1_anatomy_markers",
            "education_consent",
            "research_consent",
            "marketing_consent",
            "initial_patient_consent_signature",
            "signature_data",
            # Section 2 – Presenting Complaint
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
            "red_flags",
            "yellow_flags",
            "contraindications",
            "is_discharged",
            "reason_for_discharge",
            "discharge_remarks",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        user_profile = request.user.profile

        # If user is a student, override student field
        if user_profile.role == "student":
            validated_data["student"] = user_profile

        # If user is admin, must select student manually
        elif user_profile.role == "admin" and not validated_data.get("student"):
            raise serializers.ValidationError(
                {"student": "This field is required for admins."}
            )

        # -----------------------------
        # Audit fields (CREATE)
        # -----------------------------
        validated_data["created_by"] = user_profile
        validated_data["updated_by"] = user_profile

        signature_data = validated_data.pop("signature_data", None)
        instance = super().create(validated_data)

        if signature_data:
            self._save_signature(instance, signature_data)

        return instance

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user_profile = request.user.profile
        instance.updated_by = user_profile

        signature_data = validated_data.pop("signature_data", None)
        instance = super().update(instance, validated_data)

        if signature_data:
            self._save_signature(instance, signature_data)

        return instance

    def validate_section_1_anatomy_markers(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Markers must be a list.")

        cleaned = []

        for m in value:
            if not isinstance(m, dict):
                continue

            if "x" not in m or "y" not in m:
                continue

            try:
                cleaned.append({
                    "id": int(m.get("id")) if m.get("id") is not None else None,
                    "x": float(m["x"]),
                    "y": float(m["y"]),
                })
            except (ValueError, TypeError):
                continue

        # optional safety limit
        if len(cleaned) > 50:
            cleaned = cleaned[:50]

        return cleaned

    def _save_signature(self, instance, signature_data):
        if not signature_data:
            return
        try:
            format, imgstr = signature_data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name=f"signature_{instance.id}.{ext}"
            )
            instance.initial_patient_consent_signature = data
            instance.is_initial_patient_consent_signed = True
            instance.initial_patient_consent_signed_at = timezone.now()
            instance.save()
        except Exception as e:
            raise serializers.ValidationError(
                {"signature_data": f"Invalid image data: {str(e)}"}
            )


class AssessmentSection3Serializer(serializers.ModelSerializer):
    class Meta:
        model = Assessments
        fields = [
            "id",
            "student",
            "evaluator",
            "inspection_posture",
            "inspection_gait",
            "inspection_regional",
            "palpation",
            "percussion",
            "instrumentation",
            "rom_active",
            "rom_passive",
            "rom_resisted",
            "rom_drawing",
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
        ]
        read_only_fields = [
            "is_section_3_signed",
        ]

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request:
            instance.updated_by = request.user.profile

        return super().update(instance, validated_data)


class AssessmentSection4Serializer(serializers.ModelSerializer):
    class Meta:
        model = Assessments
        fields = [
            "id",
            "student",
            "evaluator",
            "diagnosis",
            "diagnosis_date",
            "is_section_4_signed",
            "section_4_signed_by",
            "section_4_signed_at",
        ]
        read_only_fields = [
            "is_section_4_signed",
        ]


class AssessmentTreatmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessments
        fields = [
            "id",
            "phase_1",
            "phase_2",
            "phase_3",
            "treatment_remarks",
            "is_treatment_plan_signed",
        ]
        read_only_fields = [
            "is_treatment_plan_signed",
        ]


class SoapModalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SoapModality
        fields = [
            "id",
            "modality",
            "location",
            "settings",
            "duration_intensity",
        ]


class SoapSerializer(serializers.ModelSerializer):
    soap_modalities = SoapModalitySerializer(many=True, read_only=True)

    evaluator = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(role="clinician"), required=True
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(role="student"), required=True
    )

    student_name = serializers.CharField(source="student.official_name", read_only=True)
    evaluator_name = serializers.CharField(
        source="evaluator.official_name", read_only=True
    )

    markers = serializers.ListField(child=serializers.DictField(), required=False)

    updated_by = serializers.CharField(
        source="updated_by.official_name", read_only=True
    )
    created_by = serializers.CharField(
        source="created_by.official_name", read_only=True
    )
    signed_by_name = serializers.CharField(
        source="soap_signed_by.official_name", read_only=True
    )

    class Meta:
        model = Soaps
        fields = [
            "id",
            "assessment",
            "student",
            "evaluator",
            "soap_pulse",
            "soap_respiratory",
            "soap_systolic_bp",
            "soap_diastolic_bp",
            "subjective",
            "objective",
            "soap_assessment",
            "plan",
            "markers",
            "patient_tolerated_treatment_well",
            "patient_improved_with_treatment",
            "pain_after_treatment",
            "adverse_reactions_to_treatment",
            "notes",
            "next_appointment",
            "is_soap_signed",
            "soap_signed_by",
            "soap_signed_at",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            # display fields
            "student_name",
            "evaluator_name",
            "signed_by_name",
            "soap_modalities",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
            "is_soap_signed",
            "soap_signed_at",
        ]

    def validate_markers(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Markers must be a list.")

        cleaned = []

        for m in value:
            if not isinstance(m, dict):
                continue

            if "x" not in m or "y" not in m or "note" not in m:
                continue

            try:
                note = str(m["note"]).strip()
                if not note:
                    continue

                cleaned.append(
                    {
                        "id": int(m.get("id")) if m.get("id") is not None else None,
                        "x": float(m["x"]),
                        "y": float(m["y"]),
                        "note": str(m["note"]).strip(),
                    }
                )
            except (ValueError, TypeError):
                continue

        # optional safety limit
        if len(cleaned) > 50:
            cleaned = cleaned[:50]

        return cleaned

    def validate(self, data):
        modalities = self.initial_data.get("soap_modalities", [])

        if not modalities:
            raise serializers.ValidationError(
                {"soap_modalities": "At least one modality is required."}
            )

        return data
    

class PatientReevaluationSerializer(serializers.ModelSerializer):
    evaluator = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(role="clinician"),
        required=True,
    )

    student = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.filter(role="student"),
        required=True,
    )

    student_name = serializers.CharField(
        source="student.official_name",
        read_only=True,
    )

    evaluator_name = serializers.CharField(
        source="evaluator.official_name",
        read_only=True,
    )

    signed_by_name = serializers.CharField(
        source="reevaluation_signed_by.official_name",
        read_only=True,
    )

    created_by = serializers.CharField(
        source="created_by.official_name",
        read_only=True,
    )

    updated_by = serializers.CharField(
        source="updated_by.official_name",
        read_only=True,
    )

    class Meta:
        model = PatientReevaluation

        fields = [
            "id",
            "assessment",
            "student",
            "evaluator",

            "date_of_reevaluation",
            "current_status",
            "physical_examination",
            "diagnosis",
            "treatment_plan",
            "outcome_measures",
            "next_reevaluation",

            "is_reevaluation_signed",
            "reevaluation_signed_by",
            "reevaluation_signed_at",

            "created_by",
            "created_at",
            "updated_by",
            "updated_at",

            "student_name",
            "evaluator_name",
            "signed_by_name",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
            "is_reevaluation_signed",
            "reevaluation_signed_at",
        ]

    def validate(self, data):
        date_of_reevaluation = data.get("date_of_reevaluation")
        next_reevaluation = data.get("next_reevaluation")

        if (
            date_of_reevaluation
            and next_reevaluation
            and next_reevaluation < date_of_reevaluation
        ):
            raise serializers.ValidationError(
                {
                    "next_reevaluation": (
                        "Next reevaluation date cannot be earlier "
                        "than reevaluation date."
                    )
                }
            )

        return data