# Generated by Django 2.0.6 on 2018-06-22 09:03

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import safe_relay_service.safe.models


class Migration(migrations.Migration):

    dependencies = [
        ('safe', '0005_safecontract_master_copy'),
    ]

    operations = [
        migrations.CreateModel(
            name='SafeMultisigTx',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('to', safe_relay_service.safe.models.EthereumAddressField(null=True)),
                ('value', models.BigIntegerField()),
                ('data', models.BinaryField(null=True)),
                ('operation', models.PositiveSmallIntegerField()),
                ('safe_tx_gas', models.PositiveIntegerField()),
                ('data_gas', models.PositiveIntegerField()),
                ('gas_price', models.BigIntegerField()),
                ('gas_token', safe_relay_service.safe.models.EthereumAddressField(null=True)),
                ('signatures', models.BinaryField()),
                ('gas', models.PositiveIntegerField()),
                ('nonce', models.PositiveIntegerField()),
                ('tx_hash', models.CharField(max_length=64, unique=True)),
                ('tx_mined', models.BooleanField(default=False)),
                ('safe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='safe.SafeContract')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
