# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rallybench', '0008_rallytask_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='rallytask',
            name='task_error_log',
            field=models.CharField(default=b'To be done!', max_length=4000),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rallytask',
            name='task_output_html',
            field=models.CharField(default=b'', max_length=256),
            preserve_default=True,
        ),
    ]
