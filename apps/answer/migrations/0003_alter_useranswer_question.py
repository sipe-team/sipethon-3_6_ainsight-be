# Generated by Django 5.1.5 on 2025-01-18 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('answer', '0002_rename_model_name_modelanswer_model_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useranswer',
            name='question',
            field=models.CharField(max_length=200),
        ),
    ]
