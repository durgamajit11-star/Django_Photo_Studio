from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studios', '0006_studio_price_per_hour_studio_rating_studioimage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='category',
            field=models.CharField(
                choices=[('wedding', 'Wedding'), ('product', 'Product'), ('fashion', 'Fashion'), ('other', 'Other')],
                default='other',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='tags',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
