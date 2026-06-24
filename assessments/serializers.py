import base64
import uuid
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.utils import timezone
from accounts.models import Profile
from .models import (
    Assessments,
    AssessmentAttachment,
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
    CONSENTS_FIELDS,
    TREATMENT_PLAN_FIELDS,
    DISCHARGE_FIELDS,
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
    discharge_signed_by_name = serializers.CharField(
        source="discharge_signed_by.official_name",
        read_only=True,
    )
    discharge_signed_by_role = serializers.CharField(
        source="discharge_signed_by.role",
        read_only=True,
    )

    is_section_1_complete = serializers.SerializerMethodField()
    is_section_2_complete = serializers.SerializerMethodField()
    is_section_3_complete = serializers.SerializerMethodField()
    is_section_4_complete = serializers.SerializerMethodField()
    is_consents_complete = serializers.SerializerMethodField()
    is_treatment_plan_complete = serializers.SerializerMethodField()
    is_discharge_complete = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")

    class Meta:
        model = Assessments
        fields = [
            "id",
            "patient_name",
            "ic_passport_number",
            "mrn_number",
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
            "is_consent_section_signed",
            "consent_section_signed_at",
            "is_consents_complete",
            "is_treatment_plan_signed",
            "is_treatment_plan_complete",
            "is_discharged",
            "is_discharge_complete",
            "reason_for_discharge",
            "reason_for_discharge_text",
            "discharge_remarks",
            "discharge_signed_by_name",
            "discharge_signed_by_role",
            "discharge_signed_at",
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

    def get_is_consents_complete(self, obj):
        return is_section_complete(obj, CONSENTS_FIELDS)
    
    def get_is_treatment_plan_complete(self, obj):
        return is_section_complete(obj, TREATMENT_PLAN_FIELDS)

    def get_is_discharge_complete(self, obj):
        return is_section_complete(obj, DISCHARGE_FIELDS)


class AssessmentSection1And2Serializer(serializers.ModelSerializer):
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

    # signature_data = serializers.CharField(write_only=True, required=False)
    # initial_patient_consent_signed_by = serializers.CharField(
    #     required=True, allow_blank=False
    # )

    # attending_signature_data = serializers.CharField(write_only=True, required=False)
    # attending_consent_signed_by_name = serializers.CharField(
    #     source="attending_consent_signed_by.official_name",
    #     read_only=True,
    # )

    # attending_consent_signed_by_role = serializers.CharField(
    #     source="attending_consent_signed_by.role",
    #     read_only=True,
    # )

    # witness_signature_data = serializers.CharField(write_only=True, required=False)
    # witness_consent_signed_by = serializers.CharField(required=True, allow_blank=False)
    # witness_relationship_text = serializers.CharField(
    #     source="get_witness_relationship_display", read_only=True
    # )
    section_1_anatomy_markers = serializers.ListField(
        child=serializers.DictField(), required=False
    )

    # pdpa_signature_data = serializers.CharField(write_only=True, required=False)
    # pdpa_consent_signed_by = serializers.CharField(required=True, allow_blank=False)
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
    discharge_signed_by_name = serializers.CharField(
        source="discharge_signed_by.official_name",
        read_only=True,
    )
    discharge_signed_by_role = serializers.CharField(
        source="discharge_signed_by.role",
        read_only=True,
    )

    class Meta:
        model = Assessments
        fields = [
            "student",
            "evaluator",
            # Section 1 – Initial Assessment
            "patient_name",
            "ic_passport_number",
            "mrn_number",
            "gender",
            "gender_text",
            "date_of_birth",
            "interpreter_name",
            "pulse",
            "respiratory",
            "systolic_bp",
            "diastolic_bp",
            "summary",
            "special_direction",
            "section_1_anatomy_markers",
            # "is_initial_patient_consent_signed",
            # "patient_record_review_consent",
            # "treatment_discontinuation_policy_consent",
            # "student_observation_consent",
            # "chiropractic_intern_treatment_consent",
            # "initial_patient_consent_signature",
            # "signature_data",
            # "initial_patient_consent_signed_by",
            # "initial_patient_consent_signed_at",
            # "is_attending_consent_signed",
            # "attending_signature_data",
            # "attending_consent_signed_by",
            # "attending_consent_signature",
            # "attending_consent_signed_at",
            # "attending_consent_signed_by_name",
            # "attending_consent_signed_by_role",
            # "is_witness_consent_signed",
            # "witness_signature_data",
            # "witness_consent_signed_by",
            # "witness_relationship",
            # "witness_relationship_text",
            # "witness_consent_signature",
            # "witness_consent_signed_at",
            # "is_pdpa_consent_signed",
            # "education_consent",
            # "research_consent",
            # "marketing_consent",
            # "pdpa_signature_data",
            # "pdpa_consent_signed_by",
            # "pdpa_consent_signature",
            # "pdpa_consent_signed_at",
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
            "is_discharged",
            "reason_for_discharge",
            "reason_for_discharge_text",
            "discharge_remarks",
            "discharge_signed_by_name",
            "discharge_signed_by_role",
            "discharge_signed_at",
        ]
        read_only_fields = [
            "gender_text",
            # "witness_relationship_text",
            "is_section_1_signed",
            "section_1_signed_by_name",
            "section_1_signed_by_role",
            "section_1_signed_at",
            "is_section_2_signed",
            "section_2_signed_by_name",
            "section_2_signed_by_role",
            "section_2_signed_at",
            "reason_for_discharge_text",
            "discharge_signed_by_name",
            "discharge_signed_by_role",
            "discharge_signed_at",
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

        initial_signature = validated_data.pop("signature_data", None)
        patient_name = validated_data.pop("initial_patient_consent_signed_by", None)
        attending_signature = validated_data.pop("attending_signature_data", None)
        witness_signature = validated_data.pop("witness_signature_data", None)
        witness_name = validated_data.pop("witness_consent_signed_by", None)
        # pdpa_signature = validated_data.pop("pdpa_signature_data", None)
        # pdpa_name = validated_data.pop("pdpa_consent_signed_by", None)

        instance = super().create(validated_data)

        if initial_signature:
            self._save_signature(
                instance,
                initial_signature,
                "initial_patient_consent",
                extra_data={"initial_patient_consent_signed_by": patient_name},
            )

        if attending_signature:
            self._save_signature(
                instance,
                attending_signature,
                "attending_consent",
                extra_data={
                    "attending_consent_signed_by": validated_data.get(
                        "attending_consent_signed_by"
                    )
                },
            )

        if witness_signature:
            self._save_signature(
                instance,
                witness_signature,
                "witness_consent",
                extra_data={"witness_consent_signed_by": witness_name},
            )

        # if pdpa_signature:
        #     self._save_signature(
        #         instance,
        #         pdpa_signature,
        #         "pdpa_consent",
        #         extra_data={"pdpa_consent_signed_by": pdpa_name},
        #     )

        return instance

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user_profile = request.user.profile
        instance.updated_by = user_profile

        initial_signature = validated_data.pop("signature_data", None)
        patient_name = validated_data.pop("initial_patient_consent_signed_by", None)
        attending_signature = validated_data.pop("attending_signature_data", None)
        witness_signature = validated_data.pop("witness_signature_data", None)
        witness_name = validated_data.pop("witness_consent_signed_by", None)
        # pdpa_signature = validated_data.pop("pdpa_signature_data", None)
        # pdpa_name = validated_data.pop("pdpa_consent_signed_by", None)

        instance = super().update(instance, validated_data)

        if initial_signature:
            self._save_signature(
                instance,
                initial_signature,
                "initial_patient_consent",
                extra_data={"initial_patient_consent_signed_by": patient_name},
            )

        if attending_signature:
            self._save_signature(
                instance,
                attending_signature,
                "attending_consent",
                extra_data={
                    "attending_consent_signed_by": validated_data.get(
                        "attending_consent_signed_by"
                    )
                },
            )

        if witness_signature:
            self._save_signature(
                instance,
                witness_signature,
                "witness_consent",
                extra_data={"witness_consent_signed_by": witness_name},
            )

        # if pdpa_signature:
        #     self._save_signature(
        #         instance,
        #         pdpa_signature,
        #         "pdpa_consent",
        #         extra_data={"pdpa_consent_signed_by": pdpa_name},
        #     )

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

    def _save_signature(
        self, instance, signature_data, field_prefix, user_profile=None, extra_data=None
    ):
        if not signature_data:
            return

        try:
            format, imgstr = signature_data.split(";base64,")
            ext = format.split("/")[-1]

            file = ContentFile(
                base64.b64decode(imgstr),
                name=f"{uuid.uuid4()}.{ext}",
            )

            # -----------------------------
            # Explicit field mapping (FIX)
            # -----------------------------
            if field_prefix == "initial_patient_consent":
                instance.initial_patient_consent_signature = file
                instance.is_initial_patient_consent_signed = True
                instance.initial_patient_consent_signed_at = timezone.now()

                if extra_data:
                    name = extra_data.get("initial_patient_consent_signed_by")
                    if name:
                        instance.initial_patient_consent_signed_by = name

            elif field_prefix == "attending_consent":
                instance.attending_consent_signature = file
                instance.is_attending_consent_signed = True
                instance.attending_consent_signed_at = timezone.now()

                if extra_data:
                    instance.attending_consent_signed_by = extra_data.get(
                        "attending_consent_signed_by"
                    )

            elif field_prefix == "witness_consent":
                instance.witness_consent_signature = file
                instance.is_witness_consent_signed = True
                instance.witness_consent_signed_at = timezone.now()

                if extra_data:
                    name = extra_data.get("witness_consent_signed_by")
                    if name:
                        instance.witness_consent_signed_by = name

            # elif field_prefix == "pdpa_consent":
            #     instance.pdpa_consent_signature = file
            #     instance.is_pdpa_consent_signed = True
            #     instance.pdpa_consent_signed_at = timezone.now()

            #     if extra_data:
            #         name = extra_data.get("pdpa_consent_signed_by")
            #         if name:
            #             instance.pdpa_consent_signed_by = name

            instance.save()

        except Exception as e:
            raise serializers.ValidationError(
                {"signature_data": f"Invalid image data: {str(e)}"}
            )


class AssessmentSection3Serializer(serializers.ModelSerializer):
    # rom_drawing_data = serializers.CharField(
    #     write_only=True,
    #     required=False,
    # )
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
            # "rom_drawing_data",
            "first_chiropractic",
            "cranial_nerves",
            "cerebellar",
            "spinal_cord",
            "nerve_root",
            "peripheral",
            "pathological",
            "orthopaedic_assessment",
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

        instance = super().update(instance, validated_data)

        return instance

    def _save_rom_drawing(self, instance, rom_drawing_data):
        try:
            format, imgstr = rom_drawing_data.split(";base64,")
            ext = format.split("/")[-1]

            # delete previous file
            if instance.rom_drawing:
                instance.rom_drawing.delete(save=False)

            file = ContentFile(
                base64.b64decode(imgstr),
                name=f"{uuid.uuid4()}.{ext}",
            )

            instance.rom_drawing = file

            instance.save(update_fields=["rom_drawing"])

        except Exception as e:
            raise serializers.ValidationError(
                {"rom_drawing_data": f"Invalid image data: {str(e)}"}
            )


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
            "intervention_approved",
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


class AssessmentConsentSerializer(serializers.ModelSerializer):
    """
    Consent-only serializer:
    - Patient consent
    - Attending consent
    - Witness consent
    - PDPA (reserved for future use)
    """

    # =========================================================
    # WRITE-ONLY SIGNATURE INPUTS
    # =========================================================
    signature_data = serializers.CharField(write_only=True, required=False)
    attending_signature_data = serializers.CharField(write_only=True, required=False)
    witness_signature_data = serializers.CharField(write_only=True, required=False)
    # pdpa_signature_data = serializers.CharField(write_only=True, required=False)

    # =========================================================
    # DISPLAY FIELDS
    # =========================================================
    consent_section_signed_by_name = serializers.CharField(
        source="consent_section_signed_by.official_name", read_only=True
    )
    consent_section_signed_by_role = serializers.CharField(
        source="consent_section_signed_by.role", read_only=True
    )

    initial_patient_consent_signed_by = serializers.CharField(
        required=True, allow_blank=False
    )

    initial_patient_consent_relationship_text = serializers.CharField(
        source="get_initial_patient_consent__display",
        read_only=True,
    )

    attending_consent_signed_by_name = serializers.CharField(
        source="attending_consent_signed_by.official_name",
        read_only=True,
    )

    attending_consent_signed_by_role = serializers.CharField(
        source="attending_consent_signed_by.role",
        read_only=True,
    )

    # pdpa_consent_signed_by = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = Assessments
        fields = [
            # =====================================================
            # CONSENT CHECKBOXES
            # =====================================================
            "patient_record_review_consent",
            "treatment_discontinuation_policy_consent",
            "student_observation_consent",
            "chiropractic_intern_treatment_consent",
            # =====================================================
            # INITIAL PATIENT CONSENT
            # =====================================================
            "is_initial_patient_consent_signed",
            "initial_patient_consent_signed_by",
            "initial_patient_consent_relationship",
            "initial_patient_consent_relationship_text",
            "initial_patient_consent_signed_at",
            "initial_patient_consent_signature",
            "signature_data",
            # =====================================================
            # ATTENDING CONSENT
            # =====================================================
            "is_attending_consent_signed",
            "attending_consent_signed_by",
            "attending_consent_signed_at",
            "attending_consent_signature",
            "attending_signature_data",
            "attending_consent_signed_by_name",
            "attending_consent_signed_by_role",
            # =====================================================
            # WITNESS CONSENT
            # =====================================================
            "is_witness_consent_signed",
            "witness_consent_signed_by",
            "witness_consent_signed_at",
            "witness_consent_signature",
            "witness_signature_data",
            # =====================================================
            # PDPA (FUTURE USE - COMMENTED LOGIC)
            # =====================================================
            # "is_pdpa_consent_signed",
            # "education_consent",
            # "research_consent",
            # "marketing_consent",
            # "pdpa_signature_data",
            # "pdpa_consent_signed_by",
            # "pdpa_consent_signature",
            # "pdpa_consent_signed_at",

            # =====================================================
            # CONSENT SIGNED OFF
            # =====================================================
            "is_consent_section_signed",
            "consent_section_signed_by_name",
            "consent_section_signed_by_role",
            "consent_section_signed_at",
        ]

        read_only_fields = [
            "initial_patient_consent_relationship_text",
            "attending_consent_signed_by_name",
            "attending_consent_signed_by_role",
            # "is_pdpa_consent_signed",
            # "pdpa_consent_signed_at",
            "is_consent_section_signed",
            "consent_section_signed_by_name",
            "consent_section_signed_by_role",
            "consent_section_signed_at",
        ]

    # =========================================================
    # UPDATE
    # =========================================================
    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.updated_by = request.user.profile

        initial_signature = validated_data.pop("signature_data", None)
        attending_signature = validated_data.pop("attending_signature_data", None)
        witness_signature = validated_data.pop("witness_signature_data", None)

        # pdpa_signature = validated_data.pop("pdpa_signature_data", None)
        # pdpa_name = validated_data.pop("pdpa_consent_signed_by", None)

        instance = super().update(instance, validated_data)

        if initial_signature:
            self._save_signature(
                instance,
                initial_signature,
                "initial_patient_consent",
                extra_data={
                    "initial_patient_consent_signed_by": validated_data.get(
                        "initial_patient_consent_signed_by"
                    )
                },
            )

        if attending_signature:
            self._save_signature(
                instance,
                attending_signature,
                "attending_consent",
                extra_data={
                    "attending_consent_signed_by": validated_data.get(
                        "attending_consent_signed_by"
                    )
                },
            )

        if witness_signature:
            self._save_signature(
                instance,
                witness_signature,
                "witness_consent",
                extra_data={
                    "witness_consent_signed_by": validated_data.get(
                        "witness_consent_signed_by"
                    )
                },
            )

        # -------------------------
        # PDPA (FUTURE USE)
        # -------------------------
        # if pdpa_signature:
        #     self._save_signature(
        #         instance,
        #         pdpa_signature,
        #         "pdpa_consent",
        #         extra_data={
        #             "pdpa_consent_signed_by": pdpa_name
        #         },
        #     )

        return instance

    # =========================================================
    # SIGNATURE HANDLER
    # =========================================================
    def _save_signature(self, instance, signature_data, field_prefix, extra_data=None):
        if not signature_data:
            return

        try:
            format, imgstr = signature_data.split(";base64,")
            ext = format.split("/")[-1]

            file = ContentFile(
                base64.b64decode(imgstr),
                name=f"{uuid.uuid4()}.{ext}",
            )

            # =========================
            # INITIAL PATIENT
            # =========================
            if field_prefix == "initial_patient_consent":
                instance.initial_patient_consent_signature = file
                instance.is_initial_patient_consent_signed = True
                instance.initial_patient_consent_signed_at = timezone.now()

                if extra_data:
                    name = extra_data.get("initial_patient_consent_signed_by")
                    if name:
                        instance.initial_patient_consent_signed_by = name

            # =========================
            # ATTENDING
            # =========================
            elif field_prefix == "attending_consent":
                instance.attending_consent_signature = file
                instance.is_attending_consent_signed = True
                instance.attending_consent_signed_at = timezone.now()

                if extra_data:
                    instance.attending_consent_signed_by = extra_data.get(
                        "attending_consent_signed_by"
                    )

            # =========================
            # WITNESS
            # =========================
            elif field_prefix == "witness_consent":
                instance.witness_consent_signature = file
                instance.is_witness_consent_signed = True
                instance.witness_consent_signed_at = timezone.now()

                if extra_data:
                    name = extra_data.get("witness_consent_signed_by")
                    if name:
                        instance.witness_consent_signed_by = name

            # =========================
            # PDPA (FUTURE USE)
            # =========================
            # elif field_prefix == "pdpa_consent":
            #     instance.pdpa_consent_signature = file
            #     instance.is_pdpa_consent_signed = True
            #     instance.pdpa_consent_signed_at = timezone.now()
            #
            #     if extra_data:
            #         name = extra_data.get("pdpa_consent_signed_by")
            #         if name:
            #             instance.pdpa_consent_signed_by = name

            instance.save()

        except Exception as e:
            raise serializers.ValidationError(
                {"signature_data": f"Invalid image data: {str(e)}"}
            )


class AssessmentAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.official_name", read_only=True
    )

    class Meta:
        model = AssessmentAttachment
        fields = [
            "id",
            "file",
            "label",
            "uploaded_by_name",
            "uploaded_at",
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
    attachments = serializers.SerializerMethodField()
    consents = serializers.SerializerMethodField()
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
            "attachments",
            "consents",
            "treatment_plan",
            "soaps",
            "reevaluations",
            "new_complaints",
        ]

    def get_section_1_2(self, obj):
        return AssessmentSection1And2Serializer(obj).data

    def get_section_3(self, obj):
        return AssessmentSection3Serializer(obj).data

    def get_section_4(self, obj):
        return AssessmentSection4Serializer(obj).data

    def get_attachments(self, obj):
        qs = obj.attachments.all().order_by("-uploaded_at")
        return AssessmentAttachmentSerializer(qs, many=True, context=self.context).data

    def get_consents(self, obj):
        return AssessmentConsentSerializer(obj).data
    
    def get_treatment_plan(self, obj):
        return AssessmentTreatmentPlanSerializer(obj).data

    def get_reevaluations(self, obj):
        qs = PatientReevaluation.objects.filter(assessment=obj)
        return PatientReevaluationSerializer(qs, many=True).data

    def get_new_complaints(self, obj):
        qs = PatientNewComplaint.objects.filter(assessment=obj)
        return PatientNewComplaintSerializer(qs, many=True).data