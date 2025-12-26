from django.db import models
from accounts.models import Profile


class Assessments(models.Model):

    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
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
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()

    pulse = models.PositiveSmallIntegerField()
    respiratory = models.PositiveSmallIntegerField()

    systolic_bp = models.PositiveSmallIntegerField(help_text="Systolic BP (mmHg)")
    diastolic_bp = models.PositiveSmallIntegerField(help_text="Diastolic BP (mmHg)")

    summary = models.TextField(blank=True, default="")
    special_direction = models.TextField(blank=True, default="")

    # Presenting Complaint
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

    # Student digital sign-off
    is_student_signed = models.BooleanField(default=False)
    student_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_signed_assessments",
        default=None,
    )
    student_signed_at = models.DateTimeField(null=True, blank=True, default=None)

    # Clinician sign-off (Section 1)
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

    special_examination_instruction = models.TextField(blank=True, default="")

    # =====================
    # Section 2 – Physical Examination
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

    second_chiropractic_notes = models.TextField(blank=True, default="")

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

    further_diagnostic_procedures = models.TextField(blank=True, default="")
    ptt = models.CharField(max_length=150, blank=True, default="")
    procedures_signed_at = models.DateTimeField(null=True, blank=True, default=None)
    procedures_signed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="second_signed_sections",
        limit_choices_to={"role": "clinician"},
        default=None,
    )

    # =====================
    # Section 3 – Neurological & Final
    # =====================
    cranial_nerves = models.TextField(blank=True, default="")
    cerebellar = models.TextField(blank=True, default="")
    spinal_cord = models.TextField(blank=True, default="")
    nerve_root = models.TextField(blank=True, default="")
    peripheral = models.TextField(blank=True, default="")
    pathological = models.TextField(blank=True, default="")

    orthopedic_assessment = models.TextField(blank=True, default="")
    third_chiropractic_notes = models.TextField(blank=True, default="")
    imaging = models.TextField(blank=True, default="")
    lab = models.TextField(blank=True, default="")

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
    # Meta
    # =====================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient_name} ({self.student})"

    # =====================
    # Progress & Stage Logic
    # =====================

    def current_stage(self):
        if not self.is_section_1_signed:
            return "section_1"

        if not self.is_section_2_signed:
            return "section_2"

        if not self.is_section_3_signed:
            return "section_3"

        return "completed"

    def progress_percent(self):
        total = 3
        signed = sum(
            [
                self.is_section_1_signed,
                self.is_section_2_signed,
                self.is_section_3_signed,
            ]
        )
        return int((signed / total) * 100)
