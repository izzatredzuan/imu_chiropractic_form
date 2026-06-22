ROLE_CHOICES = (
        ("student", "Student"),
        ("clinician", "Clinician"),
        ("admin", "Admin"),
    )

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

WITNESS_RELATIONSHIP_CHOICES = (
    ("supervising_clinician", "Supervising Clinician"),

    ("staff_nurse", "Staff Nurse"),
    ("healthcare_professional", "Healthcare Professional"),

    ("colleague", "Colleague"),
    ("student_peer", "Student Peer"),

    ("administrative_staff", "Administrative Staff"),

    ("other", "Other"),
)
