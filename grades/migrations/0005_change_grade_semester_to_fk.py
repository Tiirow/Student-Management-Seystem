from django.db import migrations, models
import django.db.models.deletion


# ============================================================
# CONVERT OLD SEMESTER TEXT TO SEMESTER IDs
# ============================================================

def convert_semester_values(apps, schema_editor):

    Grade = apps.get_model("grades", "Grade")
    Semester = apps.get_model("grades", "Semester")

    semester1, _ = Semester.objects.get_or_create(
        name="Semester 1",
        defaults={
            "status": "Active",
        },
    )

    semester2, _ = Semester.objects.get_or_create(
        name="Semester 2",
        defaults={
            "status": "Active",
        },
    )

    for grade in Grade.objects.all():

        old_value = str(grade.semester).strip()

        if old_value == "Semester 1":
            grade.semester = str(semester1.id)

        elif old_value == "Semester 2":
            grade.semester = str(semester2.id)

        grade.save()


# ============================================================
# MIGRATION
# ============================================================

class Migration(migrations.Migration):

    dependencies = [
        ("grades", "0004_convert_semester"),
    ]

    operations = [

        # ----------------------------------------------------
        # STEP 1
        # Make semester a temporary text field first
        # ----------------------------------------------------

        migrations.AlterField(
            model_name="grade",
            name="semester",
            field=models.CharField(
                max_length=100,
            ),
        ),

        # ----------------------------------------------------
        # STEP 2
        # Convert Semester 1 / Semester 2 into IDs
        # ----------------------------------------------------

        migrations.RunPython(
            convert_semester_values,
            migrations.RunPython.noop,
        ),

        # ----------------------------------------------------
        # STEP 3
        # Convert the field to ForeignKey
        # ----------------------------------------------------

        migrations.AlterField(
            model_name="grade",
            name="semester",
            field=models.ForeignKey(
                to="grades.semester",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="grades",
            ),
        ),

    ]
    