from django.db import migrations, models
import django.db.models.deletion


def create_default_semesters(apps, schema_editor):
    Semester = apps.get_model("grades", "Semester")

    Semester.objects.get_or_create(
        name="Semester 1",
        defaults={"status": "Active"},
    )

    Semester.objects.get_or_create(
        name="Semester 2",
        defaults={"status": "Active"},
    )


class Migration(migrations.Migration):

    dependencies = [
        ("grades", "0003_semester_alter_grade_semester"),
    ]

    operations = [
        migrations.RunPython(
            create_default_semesters,
            migrations.RunPython.noop,
        ),
    ]
    