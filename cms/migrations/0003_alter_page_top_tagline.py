# Generated by Django 4.2.3 on 2023-07-13 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0002_alter_page_top_banenr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='top_tagline',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
