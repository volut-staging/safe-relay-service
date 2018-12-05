# Generated by Django 2.1.3 on 2018-12-05 10:24

from django.db import migrations


def create_price_oracles(apps, schema_editor):
    PriceOracle = apps.get_model('tokens', 'PriceOracle')
    PriceOracle.objects.bulk_create([
        PriceOracle(name='Kraken'),
        PriceOracle(name='Binance'),
        PriceOracle(name='DutchX'),
        PriceOracle(name='Huobi'),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('tokens', '0006_auto_20181205_1226'),
    ]

    operations = [
        migrations.RunPython(create_price_oracles)
    ]
