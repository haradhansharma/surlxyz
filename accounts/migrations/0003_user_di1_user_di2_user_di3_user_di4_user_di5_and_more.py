# Generated by Django 4.2.3 on 2023-07-24 11:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_profile_id_alter_profile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='di1',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='user',
            name='di2',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='user',
            name='di3',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='user',
            name='di4',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='user',
            name='di5',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='user',
            name='di6',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='user',
            name='di7',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='user',
            name='di8',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
