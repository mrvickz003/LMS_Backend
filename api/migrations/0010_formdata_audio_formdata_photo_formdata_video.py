# Generated by Django 5.1.2 on 2024-11-29 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_formdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='formdata',
            name='audio',
            field=models.FileField(blank=True, null=True, upload_to='uploads/audios/'),
        ),
        migrations.AddField(
            model_name='formdata',
            name='photo',
            field=models.FileField(blank=True, null=True, upload_to='uploads/photos/'),
        ),
        migrations.AddField(
            model_name='formdata',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='uploads/videos/'),
        ),
    ]
