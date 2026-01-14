def clinician_is_readonly(profile, assessment):
    """
    A clinician is read-only if they are NOT the assigned evaluator.
    """
    return (
        profile.role == "clinician"
        and assessment is not None
        and assessment.evaluator != profile
    )