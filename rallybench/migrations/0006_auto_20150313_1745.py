# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rallybench', '0005_auto_20150313_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='rallytask',
            name='created_time',
            field=models.DateField(default=datetime.datetime(2015, 3, 13, 17, 45, 20, 276844, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rallytask',
            name='finished_time',
            field=models.DateField(default=datetime.datetime(2015, 3, 13, 17, 45, 40, 898224, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
