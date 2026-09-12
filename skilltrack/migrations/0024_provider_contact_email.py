from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("skilltrack", "0023_employment_uan_verified_on")]

    operations = [
        migrations.AddField(
            model_name="provider",
            name="contact_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
