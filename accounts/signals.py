import logging
import re

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

logger = logging.getLogger("userprofile")


def generate_admin_member_id():
    """
    Generate the next AdminXXX member ID.
    Example: Admin001, Admin002, Admin003...
    """
    admin_profiles = Profile.objects.filter(
        member_id__regex=r"^Admin\d{3}$"
    ).values_list("member_id", flat=True)

    max_number = 0

    for member_id in admin_profiles:
        match = re.match(r"^Admin(\d{3})$", member_id)
        if match:
            max_number = max(max_number, int(match.group(1)))

    return f"Admin{max_number + 1:03d}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.is_superuser:
        member_id = generate_admin_member_id()

        Profile.objects.create(
            user=instance,
            member_id=member_id,
            official_name=member_id,
            role="admin",
            is_admin=True,
            gender="male",
            first_time_password_change=False,
        )

        logger.info(
            "Admin profile created: username=%s member_id=%s",
            instance.username,
            member_id,
        )

        print(
            f"[create_profile] Superuser '{instance.username}' assigned member_id '{member_id}'"
        )

    else:
        Profile.objects.create(
            user=instance,
            member_id=f"AUTO-{instance.id}",
            official_name=instance.get_full_name() or instance.username,
            role="student",
            gender="male",
        )


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()