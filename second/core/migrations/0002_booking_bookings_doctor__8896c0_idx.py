# Generated by Django 5.1.6 on 2025-03-20 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['doctor_id', 'date', 'time_slot'], name='bookings_doctor__8896c0_idx'),
        ),
    ]
