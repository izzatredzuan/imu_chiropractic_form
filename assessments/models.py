import hashlib
import os
import uuid

from django.db import models
from django.utils.text import slugify
from django.utils.deconstruct import deconstructible
from encrypted_fields.fields import EncryptedCharField

from . import choices
from accounts.models import Profile


@deconstructible
class AssessmentUploadPath:
    def __init__(self, category):
        self.category = category

    def __call__(self, instance, filename):
        # Extract extension safely
        ext = os.path.splitext(filename)[1].lower()

        # Remove dangerous characters from original filename
        original_name = os.path.splitext(filename)[0]
        clean_name = slugify(original_name)

        # Fallback if filename becomes empty
        if not clean_name:
            clean_name = "file"

        # Generate unique filename
        unique_name = f"{uuid.uuid4().hex[:8]}-{clean_name}{ext}"

        # Handle unsaved instance safely
        assessment_id = instance.pk or "temp"

        return f"assessments/" f"{assessment_id}/" f"{self.category}/" f"{unique_name}"


class Assessments(models.Model):
    # =====================
    # Assignment
    # =====================
    student = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_assessments",
        limit_choices_to={"role": "student"},
        default=None,
    )

    evaluator = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluator_assessments",
        limit_choices_to={"role": "clinician"},
        default=None,
    )

    # =====================
    # Section 1 – Initial Assessment
    # =====================
    patient_name = models.CharField(max_length=150)
    ic_passport_number = EncryptedCharField(max_length=255)
    # Store the hash of IC/Passport for indexing and lookup without exposing the actual value
    # for query reference: 
    # Assessments.objects.get(ic_passport_hash=hashlib.sha256("123456".strip().upper().encode()).hexdigest())
    ic_passport_hash = models.CharField(
        max_length=64,
        db_index=True,
        editable=False
    )
    mrn_number = models.CharField(max_length=50)
    gender = models.CharField(max_length=30, choices=choices.GENDER_CHOICES)
    date_of_birth = models.DateField()
    interpreter_name = models.CharField(max_length=150, blank=True, default="")

    pulse = models.PositiveSmallIntegerField()
    respiratory = models.PositiveSmallIntegerField()

    systolic_bp = models.PositiveSmallIntegerField(help_text="Systolic BP (mmHg)")
    diastolic_bp = models.PositiveSmallIntegerField(help_text="Diastolic BP (mmHg)")

    section_1_anatomy_markers = models.JSONField(default=list, blank=True)

    summary = models.TextField(blank=True, default="")
    special_direction = models.TextField(blank=True, default="")

    is_section_1_signed = models.BooleanField(default=False)
    section_1_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="section1_signed_assessments",
        limit_choices_to={"role": "clinician"},
        default=None,
    )
    section_1_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    # =====================
    # Section 2 – Presenting Complaint
    # =====================
    chief_complaint = models.TextField(blank=True, default="")
    history_of_condition = models.TextField(blank=True, default="")

    pain = models.TextField(blank=True, default="")
    aggravating_factors = models.TextField(blank=True, default="")
    relieving_factors = models.TextField(blank=True, default="")
    associated_symptoms = models.TextField(blank=True, default="")
    health_hx_review = models.TextField(blank=True, default="")
    past_illnesses = models.TextField(blank=True, default="")
    family_hx = models.TextField(blank=True, default="")
    psycho_social_hx = models.TextField(blank=True, default="")
    occupational = models.TextField(blank=True, default="")
    diet = models.TextField(blank=True, default="")
    system_review = models.TextField(blank=True, default="")
    differential_diagnosis = models.TextField(blank=True, default="")

    red_flags = models.TextField(blank=True, default="")
    yellow_flags = models.TextField(blank=True, default="")
    contraindications = models.TextField(blank=True, default="")

    is_section_2_signed = models.BooleanField(default=False)
    section_2_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="section2_signed_assessments",
        limit_choices_to={"role": "clinician"},
        default=None,
    )
    section_2_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    special_examination_instruction = models.TextField(blank=True, default="")

    # =====================
    # Section 3 – Physical Examination
    # =====================
    inspection_posture = models.TextField(blank=True, default="")
    inspection_gait = models.TextField(blank=True, default="")
    inspection_regional = models.TextField(blank=True, default="")

    palpation = models.TextField(blank=True, default="")
    percussion = models.TextField(blank=True, default="")
    instrumentation = models.TextField(blank=True, default="")

    rom_active = models.TextField(blank=True, default="")
    rom_passive = models.TextField(blank=True, default="")
    rom_resisted = models.TextField(blank=True, default="")
    rom_drawing = models.ImageField(
        upload_to=AssessmentUploadPath("rom_drawing"), null=True, blank=True
    )

    first_chiropractic = models.TextField(blank=True, default="")

    cranial_nerves = models.TextField(blank=True, default="")
    cerebellar = models.TextField(blank=True, default="")
    spinal_cord = models.TextField(blank=True, default="")
    nerve_root = models.TextField(blank=True, default="")
    peripheral = models.TextField(blank=True, default="")
    pathological = models.TextField(blank=True, default="")

    orthopaedic_assessment = models.TextField(blank=True, default="")
    second_chiropractic = models.TextField(blank=True, default="")
    imaging = models.TextField(blank=True, default="")
    lab = models.TextField(blank=True, default="")
    working_diagnosis = models.TextField(blank=True, default="")

    is_section_3_signed = models.BooleanField(default=False)
    section_3_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="section3_signed_assessments",
        limit_choices_to={"role": "clinician"},
        default=None,
    )
    section_3_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    # =====================
    # Section 4 – Problem and Interventions List
    # =====================
    diagnosis = models.TextField(blank=True, default="")
    intervention_approved = models.TextField(blank=True, default="")
    diagnosis_date = models.DateField(null=True, blank=True)

    is_section_4_signed = models.BooleanField(default=False)
    section_4_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="section4_signed_assessments",
        limit_choices_to={"role": "clinician"},
        default=None,
    )
    section_4_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    # =====================
    # Initial Patient Consent
    # =====================
    patient_record_review_consent = models.BooleanField(default=False)
    treatment_discontinuation_policy_consent = models.BooleanField(default=False)
    student_observation_consent = models.BooleanField(default=False)
    chiropractic_intern_treatment_consent = models.BooleanField(default=False)
    is_initial_patient_consent_signed = models.BooleanField(default=False)
    initial_patient_consent_signed_by = models.CharField(max_length=150)
    initial_patient_consent_signature = models.ImageField(
        upload_to=AssessmentUploadPath("patient_signatures"), null=True, blank=True
    )
    initial_patient_consent_signed_at = models.DateTimeField(
        null=True, blank=True, default=None
    )

    # =====================
    # Attending Consent
    # =====================
    is_attending_consent_signed = models.BooleanField(default=False)
    attending_consent_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attending_consent_signed_assessments",
        limit_choices_to={"role__in": ["clinician", "student"]},
        default=None,
    )
    attending_consent_signature = models.ImageField(
        upload_to=AssessmentUploadPath("attending_signatures"), null=True, blank=True
    )
    attending_consent_signed_at = models.DateTimeField(
        null=True, blank=True, default=None
    )

    # =====================
    # Witness Consent
    # =====================
    is_witness_consent_signed = models.BooleanField(default=False)
    witness_consent_signed_by = models.CharField(max_length=150)
    witness_relationship = models.CharField(
        max_length=30, choices=choices.WITNESS_RELATIONSHIP_CHOICES
    )
    witness_consent_signature = models.ImageField(
        upload_to=AssessmentUploadPath("witness_signatures"), null=True, blank=True
    )
    witness_consent_signed_at = models.DateTimeField(
        null=True, blank=True, default=None
    )

    # =====================
    # PDPA Consent
    # =====================
    marketing_consent = models.BooleanField(default=False, null=True, blank=True)
    education_consent = models.BooleanField(default=False, null=True, blank=True)
    research_consent = models.BooleanField(default=False, null=True, blank=True)
    is_pdpa_consent_signed = models.BooleanField(default=False, null=True, blank=True)
    pdpa_consent_signed_by = models.CharField(
        max_length=150, null=True, blank=True, default=""
    )
    pdpa_consent_signature = models.ImageField(
        upload_to=AssessmentUploadPath("pdpa_signatures"), null=True, blank=True
    )
    pdpa_consent_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    # =====================
    # Treatment Plan
    # =====================
    phase_1 = models.TextField(blank=True, default="")
    phase_2 = models.TextField(blank=True, default="")
    phase_3 = models.TextField(blank=True, default="")
    treatment_remarks = models.TextField(blank=True, default="")

    is_treatment_plan_signed = models.BooleanField(default=False)
    treatment_plan_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="treatment_plan_signed_assessments",
        limit_choices_to={"role": "clinician"},
        default=None,
    )
    treatment_plan_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    # =====================
    # Discharge
    # =====================
    reason_for_discharge = models.CharField(
        max_length=100, choices=choices.DISCHARGE_CHOICES, blank=True, default=""
    )
    discharge_remarks = models.TextField(blank=True, default="")
    is_discharged = models.BooleanField(default=False)
    discharge_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="discharge_signed_assessments",
        limit_choices_to={"role": "clinician"},
        default=None,
    )
    discharge_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    # =====================
    # Meta
    # =====================
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assessments",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_assessments",
    )

    def save(self, *args, **kwargs):
        if self.ic_passport_number:
            self.ic_passport_hash = hashlib.sha256(
                self.ic_passport_number.strip().upper().encode()
            ).hexdigest()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.mrn_number}] {self.patient_name} (ID: {self.id})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
        indexes = [
            models.Index(fields=["mrn_number"]),
            models.Index(fields=["patient_name"]),
            models.Index(fields=["created_at"]),
        ]


class AssessmentAttachment(models.Model):
    assessment = models.ForeignKey(
        Assessments, on_delete=models.CASCADE, related_name="attachments"
    )

    file = models.FileField(upload_to=AssessmentUploadPath("attachments"))

    uploaded_by = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, blank=True
    )

    label = models.CharField(max_length=100, blank=True, default="")

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assessment.mrn_number} - {self.file.name}"


class Soaps(models.Model):
    assessment = models.ForeignKey(
        Assessments, on_delete=models.CASCADE, related_name="soaps"
    )

    student = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name="student_soap",
        limit_choices_to={"role": "student"},
    )

    evaluator = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name="evaluator_soaps",
        limit_choices_to={"role": "clinician"},
    )

    soap_pulse = models.PositiveSmallIntegerField()
    soap_respiratory = models.PositiveSmallIntegerField()
    soap_systolic_bp = models.PositiveSmallIntegerField(
        help_text="S.O.A.P. Systolic BP (mmHg)"
    )
    soap_diastolic_bp = models.PositiveSmallIntegerField(
        help_text="S.O.A.P. Diastolic BP (mmHg)"
    )

    subjective = models.TextField(blank=True, default="")
    objective = models.TextField(blank=True, default="")
    soap_assessment = models.TextField(blank=True, default="")
    plan = models.TextField(blank=True, default="")

    markers = models.JSONField(default=list, blank=True)

    patient_tolerated_treatment_well = models.BooleanField(default=False)
    patient_improved_with_treatment = models.BooleanField(default=False)
    pain_after_treatment = models.BooleanField(default=False)
    adverse_reactions_to_treatment = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")

    next_appointment = models.DateField(null=True, blank=True, default=None)

    is_soap_signed = models.BooleanField(default=False)
    soap_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="soap_signed",
        limit_choices_to={"role": "clinician"},
        default=None,
    )
    soap_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_soaps",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_soaps",
    )

    def save(self, *args, **kwargs):
        if not isinstance(self.markers, list):
            self.markers = []
        else:
            cleaned = []
            for m in self.markers:
                if isinstance(m, dict) and "x" in m and "y" in m and "note" in m:
                    cleaned.append(
                        {
                            "id": m.get("id"),
                            "x": float(m["x"]),
                            "y": float(m["y"]),
                            "note": str(m["note"]),
                        }
                    )
            self.markers = cleaned
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SOAP #{self.id} - {self.assessment.patient_name}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "SOAP Note"
        verbose_name_plural = "SOAP Notes"
        indexes = [
            models.Index(fields=["assessment"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["next_appointment"]),
        ]


class SoapModality(models.Model):
    soap = models.ForeignKey(
        Soaps, on_delete=models.CASCADE, related_name="soap_modalities"
    )

    modality = models.CharField(max_length=50, choices=choices.MODALITIES_CHOICES)

    location = models.TextField(blank=True, default="")
    settings = models.TextField(blank=True, default="")
    duration_intensity = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.get_modality_display()} - SOAP #{self.soap.id}"

    class Meta:
        ordering = ["id"]
        verbose_name = "SOAP Modality"
        verbose_name_plural = "SOAP Modalities"
        indexes = [
            models.Index(fields=["soap"]),
            models.Index(fields=["modality"]),
        ]


class PatientReevaluation(models.Model):
    assessment = models.ForeignKey(
        Assessments, on_delete=models.CASCADE, related_name="patient_reevaluations"
    )

    student = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name="student_patient_reevaluations",
        limit_choices_to={"role": "student"},
    )

    evaluator = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name="evaluator_patient_reevaluations",
        limit_choices_to={"role": "clinician"},
    )

    date_of_reevaluation = models.DateField(null=True, blank=True, default=None)
    current_status = models.TextField(blank=True, default="")
    physical_examination = models.TextField(blank=True, default="")
    diagnosis = models.TextField(blank=True, default="")
    treatment_plan = models.TextField(blank=True, default="")
    outcome_measures = models.TextField(blank=True, default="")

    next_reevaluation = models.DateField(null=True, blank=True, default=None)

    is_reevaluation_signed = models.BooleanField(default=False)
    reevaluation_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reevaluation_signed",
        limit_choices_to={"role": "clinician"},
        default=None,
    )
    reevaluation_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_patient_reevaluations",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_patient_reevaluations",
    )

    def __str__(self):
        return f"Patient Reevaluation #{self.id} - {self.assessment.patient_name}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Patient Reevaluation"
        verbose_name_plural = "Patient Reevaluations"
        indexes = [
            models.Index(fields=["assessment"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["next_reevaluation"]),
        ]


class PatientNewComplaint(models.Model):
    assessment = models.ForeignKey(
        Assessments, on_delete=models.CASCADE, related_name="patient_new_complaints"
    )

    student = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name="student_patient_new_complaints",
        limit_choices_to={"role": "student"},
    )

    evaluator = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name="evaluator_patient_new_complaints",
        limit_choices_to={"role": "clinician"},
    )

    date_of_new_complaint = models.DateField(null=True, blank=True, default=None)
    new_complaint_history = models.TextField(blank=True, default="")
    physical_examination = models.TextField(blank=True, default="")
    different_diagnosis = models.TextField(blank=True, default="")
    diagnosis = models.TextField(blank=True, default="")
    treatment_plan = models.TextField(blank=True, default="")
    outcome_measures = models.TextField(blank=True, default="")

    next_reevaluation = models.DateField(null=True, blank=True, default=None)

    is_new_complaint_signed = models.BooleanField(default=False)
    new_complaint_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="new_complaint_signed",
        limit_choices_to={"role": "clinician"},
        default=None,
    )
    new_complaint_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_patient_new_complaints",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_patient_new_complaints",
    )

    def __str__(self):
        return f"Patient New Complaint #{self.id} - {self.assessment.patient_name}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Patient New Complaint"
        verbose_name_plural = "Patient New Complaints"
        indexes = [
            models.Index(fields=["assessment"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["next_reevaluation"]),
        ]
