# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rallybench', '0007_rallytask_deployment_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='rallytask',
            name='task_status',
            field=models.CharField(default=b'Build', max_length=50),
            preserve_default=True,
        ),
    ]
