# Generated by Django 5.1.2 on 2024-12-02 05:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_remove_formdata_audio_remove_formdata_photo_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='form',
            old_name='create_at',
            new_name='create_by',
        ),
        migrations.RenameField(
            model_name='form',
            old_name='update_at',
            new_name='update_by',
        ),
        migrations.RenameField(
            model_name='formdata',
            old_name='create_at',
            new_name='create_by',
        ),
        migrations.RenameField(
            model_name='formdata',
            old_name='update_at',
            new_name='update_by',
        ),
    ]