# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-22 22:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockscreener', '0004_auto_20181123_0302'),
    ]

    operations = [
        migrations.AddField(
            model_name='summaryreport',
            name='avg_volume',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='is_buy',
            field=models.CharField(default='False', max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='is_sell',
            field=models.CharField(default='False', max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='last_cob',
            field=models.CharField(default='', max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='lookback_period',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='macd',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='macd_buy_sell',
            field=models.CharField(default='False', max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='macd_sig_diff_days',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='macd_sig_diff_peak_perc',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='macd_sig_diff_peak_val',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='macd_sig_diff_val',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='macd_signal',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='smoothing_period',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='std_deviation',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='summaryreport',
            name='william_buy_sell',
            field=models.CharField(default='False', max_length=4, null=True),
        ),
    ]
