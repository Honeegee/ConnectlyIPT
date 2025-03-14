# Generated by Django 5.1.5 on 2025-02-18 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_alter_post_author_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='metadata',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='post_type',
            field=models.CharField(choices=[('text', 'Text Post'), ('image', 'Image Post'), ('video', 'Video Post')], default='text', max_length=10),
        ),
        migrations.AddField(
            model_name='post',
            name='title',
            field=models.CharField(blank=True, default='Untitled Post', max_length=200, null=True),
        ),
    ]
