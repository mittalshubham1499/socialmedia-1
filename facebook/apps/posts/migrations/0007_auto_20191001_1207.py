# Generated by Django 2.2.5 on 2019-10-01 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20191001_0706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='description',
            field=models.TextField(default='this is des'),
            preserve_default=False,
        ),
    ]
