# Generated by Django 4.2.3 on 2023-07-13 20:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('selfurl', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=152)),
                ('user_agent', models.TextField()),
                ('country', models.CharField(max_length=150)),
                ('lat', models.CharField(max_length=150)),
                ('long', models.CharField(max_length=150)),
                ('visited', models.DateTimeField(auto_now_add=True)),
                ('shortener', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='selfurl.shortener')),
            ],
            options={
                'ordering': ['-visited'],
            },
        ),
        migrations.CreateModel(
            name='ReportMalicious',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reporturl', to='selfurl.shortener')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reportuser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
