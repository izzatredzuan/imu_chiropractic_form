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
    ("self", "Self"),
    ("spouse", "Spouse"),
    ("parent", "Parent"),
    ("child", "Child"),
    ("sibling", "Sibling"),

    ("guardian", "Legal Guardian"),
    ("caregiver", "Caregiver"),
    ("next_of_kin", "Next of Kin"),

    ("relative", "Other Relative"),
    ("friend", "Friend"),

    ("employer", "Employer"),
    ("colleague", "Colleague"),

    ("legal_representative", "Legal Representative"),
    ("power_of_attorney", "Power of Attorney"),
    ("healthcare_proxy", "Healthcare Proxy"),

    ("other", "Other"),
    ("unknown", "Unknown"),
)
