# Generated by Django 4.2.3 on 2023-07-13 16:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exsite',
            name='site',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='extend', serialize=False, to='sites.site', verbose_name='site'),
        ),
    ]
