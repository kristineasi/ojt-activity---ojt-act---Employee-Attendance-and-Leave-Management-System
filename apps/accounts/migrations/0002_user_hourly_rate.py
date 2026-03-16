from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="hourly_rate",
            field=models.DecimalField(decimal_places=2, default=Decimal("100.00"), max_digits=10),
        ),
    ]
