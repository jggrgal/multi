# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0002_pedidos_tmp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pedidos_tmp',
            old_name='v_session_key',
            new_name='session_key',
        ),
    ]
