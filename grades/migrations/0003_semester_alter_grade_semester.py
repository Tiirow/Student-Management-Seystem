from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grades", "0002_alter_grade_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Semester",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Active", "Active"),
                            ("Inactive", "Inactive"),
                        ],
                        default="Active",
                        max_length=10,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Semester",
                "verbose_name_plural": "Semesters",
                "ordering": ["name"],
            },
        ),
    ]
    