# Generated by Django 3.1.3 on 2021-01-04 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('time_table', '0007_reservation'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='username',
            field=models.CharField(default='', max_length=5),
            preserve_default=False,
        ),
    ]