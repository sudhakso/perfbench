# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rallybench', '0006_auto_20150313_1745'),
    ]

    operations = [
        migrations.AddField(
            model_name='rallytask',
            name='deployment_name',
            field=models.CharField(default=b'default', max_length=50),
            preserve_default=True,
        ),
    ]
