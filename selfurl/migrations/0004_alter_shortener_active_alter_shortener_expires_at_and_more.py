# Generated by Django 4.2.3 on 2023-07-16 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfurl', '0003_versions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortener',
            name='active',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='shortener',
            name='expires_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='shortener',
            name='long_url',
            field=models.URLField(db_index=True, max_length=2000),
        ),
    ]
