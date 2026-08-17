import os
import requests
import logging


from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings

SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000")

logger = logging.getLogger("userprofile")


def generate_temp_password(length=12):
    return get_random_string(
        length=length,
        allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789@#$"
    )

def send_temp_password_email(user, full_name, temp_password):
    send_mail(
        subject="IMU Chiropractic Application Account Registration – Temporary Login Credentials",
        message=f"""
        Dear {full_name},

        Your IMU account has been successfully created.

        You may now log in using the following credentials:

        Login Page: {SITE_URL}

        Username: {user.username}
        Temporary Password: {temp_password}

        For security reasons, you are strongly advised to change your password immediately after your first login.

        If you encounter any issues accessing your account or require further assistance, please contact the IMU IT Support team.

        Thank you.

        Kind regards,

        IMU IT Services
        International Medical University
        """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


def send_reset_password_email(user, reset_link):
    send_mail(
            subject="IMU Chiropractic Application Account Password Reset",
            message=f"""
            Dear {user.profile.official_name},

            We received a request to reset the password for your IMU account.

            Please click the link below to set a new password:

            {reset_link}

            If you did not request this password reset, you may safely ignore this email.

            Kind regards,

            IMU IT Services
            International Medical University
            """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
    
# API Configuration
HEADERS = {
    "x-functions-key": settings.AZURE_FUNCTION_KEY
}

BASE_URL = settings.AZURE_BASE_URL

def _fetch_by_ids(all_endpoint, by_id_endpoint, ids):
    # Get all records
    if not ids:
        response = requests.get(
            f"{BASE_URL}/{all_endpoint}",
            headers=HEADERS,
        )

        response.raise_for_status()

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            logger.error(
                "IMU API returned invalid JSON. endpoint=%s status=%s response=%r",
                all_endpoint,
                response.status_code,
                response.text[:500],
            )
            raise

    results = []

    for item_id in ids:
        response = requests.get(
            f"{BASE_URL}/{by_id_endpoint}",
            headers=HEADERS,
            params={"EMPLID": item_id},
        )

        # Employee doesn't exist
        if response.status_code == 404:
            logger.warning(
                "Employee not found in IMU API - employee_id=%s",
                item_id,
            )
            continue

        # Other HTTP errors are real failures
        response.raise_for_status()

        # Some APIs return 200 with an empty body
        if not response.text.strip():
            logger.warning(
                "IMU API returned an empty response - employee_id=%s",
                item_id,
            )
            continue

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            logger.error(
                "IMU API returned invalid JSON - employee_id=%s status=%s response=%r",
                item_id,
                response.status_code,
                response.text[:500],
            )
            raise

        if isinstance(data, list):
            results.extend(data)
        elif data:
            results.append(data)

    return results


def get_imu_employee_details(employee_ids=None):
    return _fetch_by_ids(
        "EmployeeInfo",
        "EmployeeInfoById",
        employee_ids,
    )


def get_imu_student_details(student_ids=None):
    return _fetch_by_ids(
        "StudentProgramInfo",
        "StudentProgramInfoById",
        student_ids,
    )