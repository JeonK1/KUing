# Generated by Django 3.1.3 on 2020-11-02 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('time_table', '0004_auto_20200928_0010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecturetime',
            name='day_of_the_week',
            field=models.CharField(max_length=1),
        ),
    ]
