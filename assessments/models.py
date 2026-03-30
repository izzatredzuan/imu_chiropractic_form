from django.db import models
from accounts.models import Profile

GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
)

DISCHARGE_CHOICES = (
    ("discharged_full_recovery", "Discharged - Full Recovery"),
    ("patient_discharged_against_advice", "Patient Discharged Against Advice"),
    ("lost_to_follow_up", "Lost to Follow-up"),
    ("referred_to_physician", "Referred to Physician"),
    ("transferred_to_another_Intern", "Transferred to Another Intern"),
    ("transferred_to_community_chiropractor", "Transferred to Community Chiropractor"),
    ("moved_away", "Moved Away"),
    ("deceased", "Deceased"),
)

MODALITIES_CHOICES = (
    ("ifc", "IFC"),
    ("pre_mod", "Pre Mod"),
    ("tens", "TENS"),
    ("micro_russ_us_combo", "Micro Russ US Combo"),
    ("laser", "Laser"),
    ("traction", "Traction"),
    ("fd", "FD"),
    ("shockwave", "Shockwave"),
)


class Assessments(models.Model):
    # =====================
    # Initial Patient Consent
    # =====================
    is_initial_patient_consent_signed = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)
    education_consent = models.BooleanField(default=False)
    research_consent = models.BooleanField(default=False)
    initial_patient_consent_signature = models.ImageField(
        upload_to="assessments/patient_signatures/", null=True, blank=True
    )
    initial_patient_consent_signed_at = models.DateTimeField(
        null=True, blank=True, default=None
    )

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
    file_number = models.CharField(max_length=50)
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()

    pulse = models.PositiveSmallIntegerField()
    respiratory = models.PositiveSmallIntegerField()

    systolic_bp = models.PositiveSmallIntegerField(help_text="Systolic BP (mmHg)")
    diastolic_bp = models.PositiveSmallIntegerField(help_text="Diastolic BP (mmHg)")

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

    first_chiropractic = models.TextField(blank=True, default="")

    cranial_nerves = models.TextField(blank=True, default="")
    cerebellar = models.TextField(blank=True, default="")
    spinal_cord = models.TextField(blank=True, default="")
    nerve_root = models.TextField(blank=True, default="")
    peripheral = models.TextField(blank=True, default="")
    pathological = models.TextField(blank=True, default="")

    orthopedic_assessment = models.TextField(blank=True, default="")
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
        related_name="section5_signed_assessments",
        limit_choices_to={"role": "clinician"},
        default=None,
    )
    treatment_plan_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    # =====================
    # Discharge
    # =====================
    reason_for_discharge = models.CharField(
        max_length=100, choices=DISCHARGE_CHOICES, blank=True, default=""
    )
    discharge_remarks = models.TextField(blank=True, default="")
    is_discharged = models.BooleanField(default=False)

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

    def __str__(self):
        return f"{self.patient_name} ({self.student})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
        indexes = [
            models.Index(fields=["file_number"]),
            models.Index(fields=["patient_name"]),
            models.Index(fields=["created_at"]),
        ]


class Soaps(models.Model):
    assessment = models.ForeignKey(
        Assessments, on_delete=models.CASCADE, related_name="soaps"
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

    mp_smt = models.ImageField(
        upload_to="assessments/soap_mp_smt/", null=True, blank=True
    )

    patient_tolerated_treatment_well = models.BooleanField(default=False)
    patient_improved_with_treatment = models.BooleanField(default=False)
    pain_after_treatment = models.BooleanField(default=False)
    adverse_reactions_to_treatment = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")

    next_appointment = models.DateField()

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

    modality = models.CharField(max_length=50, choices=MODALITIES_CHOICES)

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
