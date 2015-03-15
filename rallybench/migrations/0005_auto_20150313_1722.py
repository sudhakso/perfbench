# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rallybench', '0004_deployment_validated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rallytask',
            name='deployment_id',
        ),
        migrations.AddField(
            model_name='rallytask',
            name='scenarios',
            field=models.ManyToManyField(to='rallybench.Scenario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rallytask',
            name='user_id',
            field=models.ForeignKey(default=datetime.datetime(2015, 3, 13, 17, 22, 14, 614500, tzinfo=utc), to='rallybench.RallyUser'),
            preserve_default=False,
        ),
    ]
