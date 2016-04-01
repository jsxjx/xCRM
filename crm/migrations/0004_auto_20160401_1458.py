# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_auto_20160329_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changehistory',
            name='newKeyValue',
            field=models.TextField(null=True, verbose_name='\u5b57\u6bb5\u65b0\u952e\u503c', blank=True),
        ),
        migrations.AlterField(
            model_name='changehistory',
            name='newValue',
            field=models.TextField(null=True, verbose_name='\u5b57\u6bb5\u65b0\u503c', blank=True),
        ),
        migrations.AlterField(
            model_name='changehistory',
            name='oldKeyValue',
            field=models.TextField(null=True, verbose_name='\u5b57\u6bb5\u65e7\u952e\u503c', blank=True),
        ),
        migrations.AlterField(
            model_name='changehistory',
            name='oldValue',
            field=models.TextField(null=True, verbose_name='\u5b57\u6bb5\u65e7\u503c', blank=True),
        ),
    ]
