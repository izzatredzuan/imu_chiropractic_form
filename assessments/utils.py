# Check if a clinician is read-only for a given assessment
def clinician_is_readonly(profile, assessment):
    """
    A clinician is read-only if they are NOT the assigned evaluator.
    """
    return (
        profile.role == "clinician"
        and assessment is not None
        and assessment.evaluator != profile
    )


# Check if assessment section has all required fields filled
def is_section_complete(obj, fields):
    for field in fields:
        value = getattr(obj, field)

        if value is None:
            return False

        if isinstance(value, str) and value.strip() == "":
            return False

    return True
