import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Department, Profile
from accounts.services import (
    generate_temp_password,
    send_temp_password_email,
    get_imu_employee_details,
)

logger = logging.getLogger("userprofile")


# Sync all employees
# python manage.py sync_employee_profile

# Sync one employee
# python manage.py sync_employee_profile 003834


# Sync multiple employees
# python manage.py sync_employee_profile 003834 003835 003836
class Command(BaseCommand):
    help = "Sync IMU employees into User and Profile models"

    def add_arguments(self, parser):
        parser.add_argument(
            "employee_ids",
            nargs="*",  # zero or more IDs
            type=str,
            help="One or more employee IDs to sync.",
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
        employee_ids = options.get("employee_ids") or []
        employee_ids_set = set(employee_ids)
        role = options["role"]

        create_only = options["create_only"]
        update_only = options["update_only"]
        dry_run = options["dry_run"]

        if create_only and update_only:
            raise CommandError(
                "--create-only and --update-only cannot be used together."
            )

        logger.info(
            "Employee sync started. Filter=%s",
            ", ".join(employee_ids) if employee_ids else "ALL",
        )

        # Get data
        employees = get_imu_employee_details(employee_ids)

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

            if employee_ids and emp_code not in employee_ids_set:
                continue

            try:
                with transaction.atomic():
                    department = Department.objects.filter(
                        department_code=emp.get("DEPT_CODE")
                    ).first()

                    profile = (
                        Profile.objects.filter(member_id=emp_code)
                        .select_related("user")
                        .first()
                    )

                    # Existing user
                    if profile:
                        if create_only:
                            skipped_count += 1
                            logger.info(
                                "SKIPPED (already exists) - member_id=%s",
                                emp_code,
                            )
                            continue

                        user = profile.user
                        created = False

                    # New user
                    else:
                        if update_only:
                            skipped_count += 1
                            logger.info(
                                "SKIPPED (user does not exist) - member_id=%s",
                                emp_code,
                            )
                            continue

                        temp_password = generate_temp_password()

                        user = User(
                            username=emp_code,
                            email=emp.get("EMAIL") or "",
                        )
                        user.set_password(temp_password)

                        if not dry_run:
                            user.save()
                            send_temp_password_email(
                                user,
                                emp["EMP_NAME"],
                                temp_password,
                            )
                        created = True

                    user.email = emp.get("EMAIL") or ""

                    if not dry_run:
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
                        if not dry_run:
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
