from decimal import Decimal

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AttendanceRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("time_in", models.DateTimeField()),
                ("time_out", models.DateTimeField(blank=True, null=True)),
                ("worked_hours", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=6)),
                (
                    "employee",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="attendance_records", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["-date", "-time_in"],
                "unique_together": {("employee", "date")},
            },
        ),
    ]
