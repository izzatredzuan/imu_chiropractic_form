import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Department, Profile
from accounts.services import generate_temp_password, send_temp_password_email, get_imu_employee_details

logger = logging.getLogger("userprofile")


class Command(BaseCommand):
    help = "Sync IMU employees into User and Profile models"

    def add_arguments(self, parser):
        parser.add_argument(
            "employee_id",
            nargs="?",  # optional
            type=str,
            help="Sync only the specified employee.",
        )
        parser.add_argument(
            "--role",
            choices=["clinician", "student", "admin"],
            default="clinician",
            help="Role to assign to imported users",
        )
        parser.add_argument(
            "--create-only",
            action="store_true",
            help="Create new users only. Existing users are skipped.",
        )

        parser.add_argument(
            "--update-only",
            action="store_true",
            help="Update existing users only. New users are skipped.",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run the sync without saving changes.",
        )

    def handle(self, *args, **options):
        employee_id = options.get("employee_id")
        role = options["role"]

        logger.info("Employee sync started. Filter=%s", employee_id or "ALL")

        # Get data
        if employee_id:
            employees = get_imu_employee_details(employee_id)  # you'll adjust service
        else:
            employees = get_imu_employee_details()

        created_count = 0
        updated_count = 0
        skipped_count = 0

        logger.info("Retrieved %s employee records from IMU API.", len(employees))

        for emp in employees:
            emp_code = emp.get("EMPLOYEE_CODE")

            if not emp_code:
                skipped_count += 1
                logger.warning("Skipping record with missing EMPLOYEE_CODE")
                continue

            if employee_id and emp_code != employee_id:
                continue

            try:
                with transaction.atomic():

                    department = Department.objects.filter(
                        department_code=emp.get("DEPT_CODE")
                    ).first()

                    profile = Profile.objects.filter(
                        member_id=emp_code
                    ).select_related("user").first()

                    if profile:
                        user = profile.user
                        created = False
                    else:
                        temp_password = generate_temp_password()
                        user = User.objects.create_user(
                            username=emp_code,
                            email=emp.get("EMAIL") or "",
                        )
                        user.set_password(temp_password)
                        user.save()
                        created = True

                        send_temp_password_email(user, emp["EMP_NAME"], temp_password)

                    user.email = emp.get("EMAIL") or ""
                    user.save()

                    profile, _ = Profile.objects.update_or_create(
                        user=user,
                        defaults={
                            "member_id": emp_code,
                            "official_name": emp.get("EMP_NAME", ""),
                            "role": role,
                            "personal_email": emp.get("EMAIL", ""),
                            "address_1": emp.get("ADDRESS1"),
                            "address_2": emp.get("ADDRESS2"),
                            "address_3": emp.get("ADDRESS3"),
                            "postal_code": emp.get("ZIP"),
                            "city": emp.get("CITY"),
                            "state": emp.get("STATE_NAME"),
                            "country": emp.get("COUNTRY"),
                            "location": emp.get("ULOCATION"),
                            "position": emp.get("POSITION"),
                            "department": department,
                            "business_unit": emp.get("BU_NAME"),
                        },
                    )

                    if created:
                        profile.first_time_password_change = True
                        profile.save(update_fields=["first_time_password_change"])
                        created_count += 1
                        logger.info(
                            "USER CREATED - username=%s member_id=%s",
                            user.username,
                            emp_code,
                        )
                    else:
                        updated_count += 1
                        logger.info(
                            "USER UPDATED - username=%s member_id=%s",
                            user.username,
                            emp_code,
                        )

            except Exception:
                skipped_count += 1
                logger.exception("Failed to sync employee %s", emp_code)

        logger.info(
            "Employee sync completed. Created=%s Updated=%s Skipped=%s",
            created_count,
            updated_count,
            skipped_count,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created={created_count}, Updated={updated_count}, Skipped={skipped_count}"
            )
        )