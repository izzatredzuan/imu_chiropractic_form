SECTION_1_FIELDS = [
    # Assignment
    "student",
    "evaluator",
    # Patient Details
    "patient_name",
    "file_number",
    "gender",
    "date_of_birth",
    # Vitals
    "pulse",
    "respiratory",
    "systolic_bp",
    "diastolic_bp",
    # Consent checkboxes
    "education_consent",
    "research_consent",
    # Attending consent
    "attending_consent_signed_by",
    # Witness consent
    "witness_consent_signed_by",
]

SECTION_2_FIELDS = [
    # Assignment
    "student",
    "evaluator",
    # Presenting Complaint
    "chief_complaint",
    "history_of_condition",
    # Pain & Symptom Details
    "pain",
    "aggravating_factors",
    "relieving_factors",
    "associated_symptoms",
    # Medical History
    "health_hx_review",
    "past_illnesses",
    "family_hx",
    # Lifestyle & Social History
    "psycho_social_hx",
    "occupational",
    "diet",
    # Clinical Assessment
    "system_review",
    "differential_diagnosis",
    # Risk Screening
    "red_flags",
    "yellow_flags",
    "contraindications",
]

SECTION_3_FIELDS = [
    # Assignment
    "student",
    "evaluator",
    # Inspection
    "inspection_posture",
    "inspection_gait",
    "inspection_regional",
    # Palpation / Percussion
    "palpation",
    "percussion",
    "instrumentation",
    # ROM
    "rom_active",
    "rom_passive",
    "rom_resisted",
    # Additional Notes & Diagnostic Procedures
    "first_chiropractic",
    # Neurological Examination
    "cranial_nerves",
    "cerebellar",
    "spinal_cord",
    "nerve_root",
    "peripheral",
    "pathological",
    # Diagnosis
    "orthopaedic_assessment",
    "second_chiropractic",
    "imaging",
    "lab",
    "working_diagnosis",
]

SECTION_4_FIELDS = [
    # Assignment
    "student",
    "evaluator",
    # Diagnosis
    "diagnosis",
    "intervention_approved",
    "diagnosis_date",
]

TREATMENT_PLAN_FIELDS = [
    "student",
    "evaluator",
]

DISCHARGE_FIELDS = [
    "student",
    "evaluator",
    "reason_for_discharge",
    "discharge_remarks",
]
