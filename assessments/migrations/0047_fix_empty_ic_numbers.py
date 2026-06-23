from django.db import migrations


def populate_fake_ic_numbers(apps, schema_editor):
    Assessments = apps.get_model("assessments", "Assessments")

    assessments = Assessments.objects.filter(
        ic_passport_number__isnull=True
    ) | Assessments.objects.filter(
        ic_passport_number=""
    )

    for assessment in assessments:
        assessment.ic_passport_number = f"FAKE-IC-{assessment.id:06d}"
        assessment.save(update_fields=["ic_passport_number"])


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0046_populate_fake_ic_numbers"),
    ]

    operations = [
        migrations.RunPython(
            populate_fake_ic_numbers,
            migrations.RunPython.noop,
        ),
    ]