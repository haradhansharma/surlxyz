# Generated by Django 4.2.3 on 2023-07-16 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfurl', '0004_alter_shortener_active_alter_shortener_expires_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitorlog',
            name='country',
        ),
        migrations.RemoveField(
            model_name='visitorlog',
            name='ip',
        ),
        migrations.RemoveField(
            model_name='visitorlog',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='visitorlog',
            name='long',
        ),
        migrations.AddField(
            model_name='visitorlog',
            name='geo_data',
            field=models.BinaryField(default=b''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='visitorlog',
            name='user_agent',
            field=models.BinaryField(default=b''),
        ),
    ]
