# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_delete_sltaccountmapping'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderMultipleValueField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('charValue1', models.CharField(max_length=255, null=True, verbose_name='\u503c1', blank=True)),
                ('charValue2', models.CharField(max_length=255, null=True, verbose_name='\u503c2', blank=True)),
                ('field', models.ForeignKey(verbose_name='\u5b57\u6bb5\u5b9a\u4e49', to='crm.OrderFieldDef')),
                ('order', models.ForeignKey(verbose_name='\u5355\u636e', to='crm.Order')),
            ],
            options={
                'verbose_name': '\u5355\u636e\u591a\u503c\u5b57\u6bb5\u8868',
                'verbose_name_plural': '\u5355\u636e\u591a\u503c\u5b57\u6bb5\u8868',
            },
        ),
        migrations.AddField(
            model_name='stdviewlayoutconf',
            name='multipleValue1PhraseId',
            field=models.CharField(max_length=20, null=True, verbose_name='\u591a\u503c1\u6807\u7b7e\u77ed\u8bed\u4e3b\u952e', blank=True),
        ),
        migrations.AddField(
            model_name='stdviewlayoutconf',
            name='multipleValue1Required',
            field=models.BooleanField(default=False, verbose_name='\u4f7f\u7528\u591a\u503c1'),
        ),
        migrations.AddField(
            model_name='stdviewlayoutconf',
            name='multipleValue2PhraseId',
            field=models.CharField(max_length=20, null=True, verbose_name='\u591a\u503c2\u6807\u7b7e\u77ed\u8bed\u4e3b\u952e', blank=True),
        ),
        migrations.AddField(
            model_name='stdviewlayoutconf',
            name='multipleValue2Required',
            field=models.BooleanField(default=False, verbose_name='\u4f7f\u7528\u591a\u503c2'),
        ),
    ]
