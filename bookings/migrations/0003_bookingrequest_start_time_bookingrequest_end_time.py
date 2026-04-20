from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_bookingrequest_booking_date_bookingrequest_service_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingrequest',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bookingrequest',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
