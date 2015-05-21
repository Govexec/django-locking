# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_locked_at', models.DateTimeField(null=True, editable=False, db_column=b'locked_at')),
                ('app', models.CharField(max_length=255, null=True)),
                ('model', models.CharField(max_length=255, null=True)),
                ('entry_id', models.PositiveIntegerField(db_index=True)),
                ('_hard_lock', models.BooleanField(default=False, editable=False, db_column=b'hard_lock')),
                ('_locked_by', models.ForeignKey(related_name='working_on_lock', db_column=b'locked_by', editable=False, to='account.User', null=True)),
            ],
        ),
    ]
