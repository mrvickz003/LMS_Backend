# Generated by Django 5.1.3 on 2024-12-10 18:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_customuser_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='owner',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='ownerOfCompany', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
