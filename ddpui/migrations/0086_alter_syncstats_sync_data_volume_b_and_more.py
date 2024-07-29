# Generated by Django 4.2 on 2024-07-14 09:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ddpui", "0085_syncstats"),
    ]

    operations = [
        migrations.AlterField(
            model_name="syncstats",
            name="sync_data_volume_b",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="syncstats",
            name="sync_duration_s",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="syncstats",
            name="sync_records",
            field=models.BigIntegerField(default=0),
        ),
    ]