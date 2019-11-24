# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedidos_tmp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('v_session_key', models.CharField(max_length=50)),
                ('idproveedor', models.IntegerField()),
                ('idproducto', models.CharField(max_length=16)),
                ('catalogo', models.CharField(max_length=12)),
                ('precio', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
            ],
        ),
    ]
