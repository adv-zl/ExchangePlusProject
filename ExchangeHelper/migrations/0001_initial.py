# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-13 11:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdministratorCashCosts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('waste_author', models.CharField(max_length=20)),
                ('waste_reason', models.CharField(max_length=300)),
                ('waste_summ', models.FloatField()),
                ('waste_currency', models.CharField(max_length=4)),
                ('waste_comment', models.CharField(max_length=600)),
                ('waste_date', models.DateField()),
                ('waste_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeActions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation_date', models.DateField()),
                ('operation_time', models.TimeField()),
                ('person_surname', models.CharField(max_length=20)),
                ('money_balance', models.CharField(max_length=200)),
                ('action', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='OrdinaryCashier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cashier_description_full', models.CharField(max_length=600)),
                ('cashier_description_short', models.CharField(max_length=100)),
                ('exchange_rate', models.CharField(max_length=400)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='exchangeactions',
            name='person_data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ExchangeHelper.OrdinaryCashier'),
        ),
        migrations.AddField(
            model_name='administratorcashcosts',
            name='waste_cashbox',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ExchangeHelper.OrdinaryCashier'),
        ),
    ]
