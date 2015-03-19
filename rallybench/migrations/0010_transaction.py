# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rallybench', '0009_auto_20150316_1729'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('trans_id', models.IntegerField(serialize=False, primary_key=True)),
                ('type', models.CharField(default=b'Deployment Add', max_length=50)),
                ('time', models.DateTimeField()),
                ('msg', models.CharField(default=b'', max_length=256)),
                ('user_id', models.ForeignKey(to='rallybench.RallyUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
