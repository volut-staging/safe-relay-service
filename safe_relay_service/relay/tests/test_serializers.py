from django.test import TestCase

from ethereum.transactions import secpk1n
from faker import Faker
from hexbytes import HexBytes

from gnosis.eth.constants import NULL_ADDRESS
from gnosis.eth.utils import get_eth_address_with_key
from gnosis.safe import SafeService

from ..models import SafeContract, SafeFunding
from ..serializers import (SafeCreationSerializer,
                           SafeFundingResponseSerializer,
                           SafeRelayMultisigTxSerializer)
from ..services.safe_creation_service import SafeCreationServiceProvider

faker = Faker()


class TestSerializers(TestCase):

    def test_generic_serializer(self):
        owner1, _ = get_eth_address_with_key()
        owner2, _ = get_eth_address_with_key()
        owner3, _ = get_eth_address_with_key()
        invalid_checksumed_address = '0xb299182d99e65703f0076e4812653aab85fca0f0'

        owners = [owner1, owner2, owner3]
        data = {'s': secpk1n // 2,
                'owners': owners,
                'threshold': len(owners)}
        self.assertTrue(SafeCreationSerializer(data=data).is_valid())

        data = {'s': secpk1n // 2,
                'owners': owners,
                'threshold': len(owners) + 1}
        self.assertFalse(SafeCreationSerializer(data=data).is_valid())

        data = {'s': secpk1n // 2,
                'owners': owners + [invalid_checksumed_address],
                'threshold': len(owners)}
        self.assertFalse(SafeCreationSerializer(data=data).is_valid())

        data = {'s': secpk1n // 2,
                'owners': [],
                'threshold': len(owners)}
        self.assertFalse(SafeCreationSerializer(data=data).is_valid())

    def test_funding_serializer(self):
        owner1, _ = get_eth_address_with_key()
        safe_contract = SafeContract.objects.create(address=owner1, master_copy='0x' + '0' * 40)
        safe_funding = SafeFunding.objects.create(safe=safe_contract)

        s = SafeFundingResponseSerializer(safe_funding)

        self.assertTrue(s.data)

    def test_safe_multisig_tx_serializer(self):
        relay_service = SafeCreationServiceProvider()
        w3 = relay_service.safe_service.w3

        safe = get_eth_address_with_key()[0]
        to = None
        value = int(10e18)
        tx_data = None
        operation = 0
        safe_tx_gas = 1
        data_gas = 1
        gas_price = 1
        gas_token = None
        refund_receiver = None
        nonce = 0

        data = {
            "safe": safe,
            "to": to,
            "value": value,  # 1 ether
            "data": tx_data,
            "operation": operation,
            "safe_tx_gas": safe_tx_gas,
            "data_gas": data_gas,
            "gas_price": gas_price,
            "gas_token": gas_token,
            "nonce": nonce,
            "signatures": [
                {
                    'r': 5,
                    's': 7,
                    'v': 27
                },
                {
                    'r': 17,
                    's': 29,
                    'v': 28
                }]}
        serializer = SafeRelayMultisigTxSerializer(data=data)
        self.assertFalse(serializer.is_valid())  # Less signatures than threshold

        owners_with_keys = [get_eth_address_with_key(), get_eth_address_with_key()]
        # Signatures must be sorted!
        owners_with_keys.sort(key=lambda x: x[0].lower())
        owners = [x[0] for x in owners_with_keys]
        keys = [x[1] for x in owners_with_keys]

        safe = get_eth_address_with_key()[0]
        data['safe'] = safe

        serializer = SafeRelayMultisigTxSerializer(data=data)
        self.assertFalse(serializer.is_valid())  # To and data cannot both be null

        tx_data = HexBytes('0xabcd')
        data['data'] = tx_data.hex()
        serializer = SafeRelayMultisigTxSerializer(data=data)
        self.assertFalse(serializer.is_valid())  # Operation is not create, but no to provided

        # Now we fix the signatures
        to = owners[-1]
        data['to'] = to
        multisig_tx_hash = SafeService.get_hash_for_safe_tx(
            safe,
            to,
            value,
            tx_data,
            operation,
            safe_tx_gas,
            data_gas,
            gas_price,
            gas_token,
            refund_receiver,
            nonce
        )
        signatures = [w3.eth.account.signHash(multisig_tx_hash, private_key) for private_key in keys]
        data['signatures'] = signatures
        serializer = SafeRelayMultisigTxSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        data = {
            "safe": safe,
            "to": to,
            "value": value,  # 1 ether
            "data": tx_data,
            "operation": operation,
            "safe_tx_gas": safe_tx_gas,
            "data_gas": data_gas,
            "gas_price": gas_price,
            "gas_token": gas_token,
            "nonce": nonce,
            "refund_receiver": owners[0],  # Refund must be empty or NULL_ADDRESS
            "signatures": [
                {
                    'r': 5,
                    's': 7,
                    'v': 27
                }]
        }
        serializer = SafeRelayMultisigTxSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        data['refund_receiver'] = NULL_ADDRESS
        serializer = SafeRelayMultisigTxSerializer(data=data)
        self.assertTrue(serializer.is_valid())
