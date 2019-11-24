# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0002_auto_20150625_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='domicilio',
            field=models.CharField(max_length=200, verbose_name=b'Domicilio'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='email',
            field=models.EmailField(max_length=200, verbose_name=b'email'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='nombre',
            field=models.CharField(max_length=100, verbose_name=b'Nombre'),
        ),
    ]
