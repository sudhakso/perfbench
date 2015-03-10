# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rallybench', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deployment',
            old_name='osc_name_ip',
            new_name='osc_friendly_name',
        ),
        migrations.AddField(
            model_name='deployment',
            name='osc_endpoint_type',
            field=models.CharField(default=b'public', max_length=24),
            preserve_default=True,
        ),
    ]
