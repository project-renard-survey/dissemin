# Generated by Django 2.2.1 on 2019-05-27 07:51

from django.db import migrations
import positions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('deposit', '0012_licenses'),
    ]

    operations = [
        migrations.AddField(
            model_name='licensechooser',
            name='position',
            field=positions.fields.PositionField(default=-1),
        ),
    ]
