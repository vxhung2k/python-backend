# Generated by Django 4.1.3 on 2022-12-26 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0002_product_type_time_guarantee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='options',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='API.optionsproduct'),
        ),
    ]
