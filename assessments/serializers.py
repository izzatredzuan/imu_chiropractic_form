import base64
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.utils import timezone
from accounts.models import Profile
from .models import (
    Assessments,
    PatientNewComplaint,
    SoapModality,
    Soaps,
    PatientReevaluation,
)
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
    gender_text = serializers.CharField(source="get_gender_display", read_only=True)
    section_1_anatomy_markers = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    signature_data = serializers.CharField(write_only=True, required=False)
    section_1_signed_by_name = serializers.CharField(
        source="section_1_signed_by.official_name", read_only=True
    )
    section_1_signed_by_role = serializers.CharField(
        source="section_1_signed_by.role", read_only=True
    )
    section_2_signed_by_name = serializers.CharField(
        source="section_2_signed_by.official_name", read_only=True
    )
    section_2_signed_by_role = serializers.CharField(
        source="section_2_signed_by.role", read_only=True
    )
    reason_for_discharge_text = serializers.CharField(
        source="get_reason_for_discharge_display", read_only=True
    )

    class Meta:
        model = Assessments
        fields = [
            "student",
            "evaluator",
            # Section 1 – Initial Assessment
            "patient_name",
            "file_number",
            "gender",
            "gender_text",
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
            # Common Fields
            "is_discharged",
            "reason_for_discharge",
            "reason_for_discharge_text",
            "discharge_remarks",
            "updated_by",
            "updated_at",
            "is_section_1_signed",
            "section_1_signed_by_name",
            "section_1_signed_by_role",
            "section_1_signed_at",
            "is_section_2_signed",
            "section_2_signed_by_name",
            "section_2_signed_by_role",
            "section_2_signed_at",
        ]
        read_only_fields = [
            "gender_text",
            "is_section_1_signed",
            "section_1_signed_by_name",
            "section_1_signed_by_role",
            "section_1_signed_at",
            "is_section_2_signed",
            "section_2_signed_by_name",
            "section_2_signed_by_role",
            "section_2_signed_at",
            "reason_for_discharge_text",
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
                cleaned.append(
                    {
                        "id": int(m.get("id")) if m.get("id") is not None else None,
                        "x": float(m["x"]),
                        "y": float(m["y"]),
                    }
                )
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
    section_3_signed_by_name = serializers.CharField(
        source="section_3_signed_by.official_name", read_only=True
    )
    section_3_signed_by_role = serializers.CharField(
        source="section_3_signed_by.role", read_only=True
    )

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
            "section_3_signed_by_name",
            "section_3_signed_by_role",
            "section_3_signed_at",
        ]
        read_only_fields = [
            "is_section_3_signed",
            "section_3_signed_by_name",
            "section_3_signed_by_role",
            "section_3_signed_at",
        ]

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request:
            instance.updated_by = request.user.profile

        return super().update(instance, validated_data)


class AssessmentSection4Serializer(serializers.ModelSerializer):
    section_4_signed_by_name = serializers.CharField(
        source="section_4_signed_by.official_name", read_only=True
    )
    section_4_signed_by_role = serializers.CharField(
        source="section_4_signed_by.role", read_only=True
    )

    class Meta:
        model = Assessments
        fields = [
            "id",
            "student",
            "evaluator",
            "diagnosis",
            "diagnosis_date",
            "is_section_4_signed",
            "section_4_signed_by_name",
            "section_4_signed_by_role",
            "section_4_signed_at",
        ]
        read_only_fields = [
            "is_section_4_signed",
            "section_4_signed_by_name",
            "section_4_signed_by_role",
            "section_4_signed_at",
        ]


class AssessmentTreatmentPlanSerializer(serializers.ModelSerializer):
    treatment_plan_signed_by_name = serializers.CharField(
        source="treatment_plan_signed_by.official_name", read_only=True
    )
    treatment_plan_signed_by_role = serializers.CharField(
        source="treatment_plan_signed_by.role", read_only=True
    )

    class Meta:
        model = Assessments
        fields = [
            "id",
            "phase_1",
            "phase_2",
            "phase_3",
            "treatment_remarks",
            "is_treatment_plan_signed",
            "treatment_plan_signed_by_name",
            "treatment_plan_signed_by_role",
            "treatment_plan_signed_at",
        ]
        read_only_fields = [
            "is_treatment_plan_signed",
            "treatment_plan_signed_by_name",
            "treatment_plan_signed_by_role",
            "treatment_plan_signed_at",
        ]


class SoapModalitySerializer(serializers.ModelSerializer):
    modality_text = serializers.CharField(source="get_modality_display", read_only=True)

    class Meta:
        model = SoapModality
        fields = [
            "id",
            "modality",
            "modality_text",
            "location",
            "settings",
            "duration_intensity",
        ]
        read_only_fields = [
            "modality_text",
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
    signed_by_role = serializers.CharField(source="soap_signed_by.role", read_only=True)

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
            "signed_by_role",
            "soap_modalities",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
            "is_soap_signed",
            "signed_by_name",
            "signed_by_role",
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
    signed_by_role = serializers.CharField(
        source="reevaluation_signed_by.role",
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
            "signed_by_role",
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


class PatientNewComplaintSerializer(serializers.ModelSerializer):
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
        source="new_complaint_signed_by.official_name",
        read_only=True,
    )

    signed_by_role = serializers.CharField(
        source="new_complaint_signed_by.role",
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
        model = PatientNewComplaint

        fields = [
            "id",
            "assessment",
            "student",
            "evaluator",
            "date_of_new_complaint",
            "new_complaint_history",
            "physical_examination",
            "different_diagnosis",
            "diagnosis",
            "treatment_plan",
            "outcome_measures",
            "next_reevaluation",
            "is_new_complaint_signed",
            "new_complaint_signed_by",
            "new_complaint_signed_at",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "student_name",
            "evaluator_name",
            "signed_by_name",
            "signed_by_role",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
            "is_new_complaint_signed",
            "new_complaint_signed_at",
        ]

    def validate(self, data):
        date_of_new_complaint = data.get("date_of_new_complaint")
        next_reevaluation = data.get("next_reevaluation")

        if (
            date_of_new_complaint
            and next_reevaluation
            and next_reevaluation < date_of_new_complaint
        ):
            raise serializers.ValidationError(
                {
                    "next_reevaluation": (
                        "Next reevaluation date cannot be earlier "
                        "than new complaint date."
                    )
                }
            )

        return data


class AssessmentNotesSerializer(serializers.ModelSerializer):
    section_1_2 = serializers.SerializerMethodField()
    section_3 = serializers.SerializerMethodField()
    section_4 = serializers.SerializerMethodField()
    treatment_plan = serializers.SerializerMethodField()

    soaps = SoapSerializer(many=True, read_only=True)
    reevaluations = serializers.SerializerMethodField()
    new_complaints = serializers.SerializerMethodField()

    class Meta:
        model = Assessments
        fields = [
            "id",
            "section_1_2",
            "section_3",
            "section_4",
            "treatment_plan",
            "soaps",
            "reevaluations",
            "new_complaints",
        ]

    def get_section_1_2(self, obj):
        return AssessmentSection1And2CreateSerializer(obj).data

    def get_section_3(self, obj):
        return AssessmentSection3Serializer(obj).data

    def get_section_4(self, obj):
        return AssessmentSection4Serializer(obj).data

    def get_treatment_plan(self, obj):
        return AssessmentTreatmentPlanSerializer(obj).data

    def get_reevaluations(self, obj):
        qs = PatientReevaluation.objects.filter(assessment=obj)
        return PatientReevaluationSerializer(qs, many=True).data

    def get_new_complaints(self, obj):
        qs = PatientNewComplaint.objects.filter(assessment=obj)
        return PatientNewComplaintSerializer(qs, many=True).data
