# Generated by Django 3.2.15 on 2022-09-17 21:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Corporate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True)),
                ('location', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True)),
                ('total_interest', models.IntegerField(default=0)),
                ('corporate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobapp.corporate')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('interest_jobs', models.ManyToManyField(blank=True, to='jobapp.Job')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='corporate',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]