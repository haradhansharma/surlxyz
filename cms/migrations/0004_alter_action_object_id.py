# Generated by Django 4.2.3 on 2023-07-16 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_alter_page_top_tagline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='object_id',
            field=models.PositiveIntegerField(db_index=True),
        ),
    ]
