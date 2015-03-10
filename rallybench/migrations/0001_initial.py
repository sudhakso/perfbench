# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('uniqueid', models.CharField(max_length=256, serialize=False, primary_key=True)),
                ('osc_name_ip', models.CharField(max_length=256)),
                ('osc_tenant_name', models.CharField(max_length=256)),
                ('osc_username', models.CharField(max_length=50)),
                ('osc_password', models.CharField(max_length=50)),
                ('osc_auth_url', models.CharField(max_length=256)),
                ('osc_type', models.CharField(max_length=24)),
                ('osc_region_name', models.CharField(max_length=50)),
                ('in_use', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RallyTask',
            fields=[
                ('task_id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('is_running', models.BooleanField(default=False)),
                ('output_folder', models.CharField(max_length=256)),
                ('deployment_id', models.ForeignKey(to='rallybench.Deployment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RallyUser',
            fields=[
                ('username', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('password', models.CharField(max_length=50)),
                ('userwd', models.CharField(max_length=256)),
                ('created', models.DateField()),
                ('isAdmin', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RallyUserSession',
            fields=[
                ('session_id', models.CharField(max_length=256, serialize=False, primary_key=True)),
                ('last_activity', models.DateField()),
                ('taskId', models.CharField(max_length=256)),
                ('user', models.ForeignKey(to='rallybench.RallyUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('scenario_file_name', models.CharField(max_length=256, serialize=False, primary_key=True)),
                ('scenario_type', models.CharField(max_length=16)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='deployment',
            name='usersession',
            field=models.ForeignKey(to='rallybench.RallyUserSession'),
            preserve_default=True,
        ),
    ]
