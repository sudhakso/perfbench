# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rallybench', '0002_auto_20150309_0801'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deployment',
            name='usersession',
        ),
        migrations.AddField(
            model_name='deployment',
            name='user',
            field=models.ForeignKey(default=1, to='rallybench.RallyUser'),
            preserve_default=False,
        ),
    ]
