# Generated by Django 5.0.1 on 2024-12-09 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='insurance_type',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
    ]
