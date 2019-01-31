# -*- coding: utf-8 -*-

# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from iconsdk.wallet.wallet import KeyWallet
from iconservice import Address, ZERO_SCORE_ADDRESS
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, Account

from contracts.interfaces.abc_score_registry import ABCScoreRegistry
from tests.integration_tests.utils import deploy_score, get_content_as_bytes, transaction_call, \
    icx_call, update_governance, setup_import_whitelist


class TestConverter(IconIntegrateTestBase):

    def setUp(self, **kwargs):
        # noinspection PyUnusedLocal
        self.keys = [KeyWallet.create() for i in range(10)]
        accounts = [Account(key.address, Address.from_string(key.address), 10000 * 10 ** 18) for key
                    in self.keys]
        super().setUp(accounts)

        # Update governance and setup import whitelist
        update_governance(icon_integrate_test_base=super(), from_=self._test1, params={})
        setup_import_whitelist(self, self._test1)

        self.network_address = self.setup_network()

        self.registry_address = self.setup_registry(self.network_address)

        self.token_address = self.setup_smart_token('Token1', 'TKN1', 2, 18)

        self.connector_token1_address = self.setup_irc_token('IRC Token 1', 'IRC1', 1000000000, 18)
        self.connector_token2_address = self.setup_irc_token('IRC Token 2', 'IRC2', 2000000000, 18)
        self.connector_token3_address = self.setup_irc_token('IRC Token 3', 'IRC3', 1500000000, 18)

    def setup_registry(self, network_address):
        tx_result = deploy_score(self, get_content_as_bytes("score_registry"), self.keys[0],
                                 params={})
        self.assertEqual(tx_result['status'], int(True))
        score_address = tx_result['scoreAddress']

        transaction_call(self, self.keys[0], score_address, 'registerAddress',
                         {
                             '_scoreName': ABCScoreRegistry.BANCOR_NETWORK,
                             '_scoreAddress': network_address
                         })

        return score_address

    def setup_network(self):
        tx_result = deploy_score(self, get_content_as_bytes("network"), self.keys[0], params={})

        self.assertEqual(tx_result['status'], int(True))

        return tx_result['scoreAddress']

    def setup_smart_token(self, name: str, symbol: str, initial_supply: int, decimals: int):
        tx_result = deploy_score(self, get_content_as_bytes("smart_token"), self.keys[0],
                                 params={
                                     '_name': name,
                                     '_symbol': symbol,
                                     '_initialSupply': initial_supply,
                                     '_decimals': decimals
                                 })

        self.assertEqual(tx_result['status'], int(True))

        return tx_result['scoreAddress']

    def setup_irc_token(self, name: str, symbol: str, initial_supply: int, decimals: int):
        tx_result = deploy_score(self, get_content_as_bytes("irc_token"), self.keys[0],
                                 params={
                                     '_name': name,
                                     '_symbol': symbol,
                                     '_initialSupply': initial_supply,
                                     '_decimals': decimals
                                 })

        self.assertEqual(tx_result['status'], int(True))

        return tx_result['scoreAddress']

    def setup_converter(self,
                        smart_token: Address,
                        registry: Address,
                        max_conversion_fee: int,
                        connector_token: Address,
                        connector_wight: int):
        tx_result = deploy_score(self, get_content_as_bytes("converter"), self.keys[0],
                                 params={
                                     '_token': str(smart_token),
                                     '_registry': str(registry),
                                     '_maxConversionFee': max_conversion_fee,
                                     '_connectorToken': str(connector_token),
                                     '_connectorWeight': connector_wight
                                 })
        self.assertEqual(tx_result['status'], int(True))
        return tx_result['scoreAddress']

    def init_converter(self, activate: bool, max_conversion_fee: int = 0):
        converter_address = self.setup_converter(
            self.token_address,
            self.registry_address,
            max_conversion_fee,
            self.connector_token1_address,
            250000
        )

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token2_address,
                             '_weight': 150000,
                             '_enableVirtualBalance': 0
                         })

        transaction_call(self, self.keys[0], self.token_address,
                         'issue', {'_to': str(self.keys[0].address), '_amount': 20000})

        transaction_call(self, self.keys[0], self.connector_token1_address,
                         'transfer', {'_to': converter_address, '_value': 5000})

        transaction_call(self, self.keys[0], self.connector_token2_address,
                         'transfer', {'_to': converter_address, '_value': 8000})

        if activate:
            transaction_call(self, self.keys[0], self.token_address,
                             'transferOwnerShip', {'_newOwner': converter_address})

            transaction_call(self, self.keys[0], converter_address, 'acceptTokenOwnership', {})

        return converter_address

    def verify_connector(
            self, connector: dict,
            virtual_balance, weight, is_virtual_balance_enabled, is_purchase_enabled, is_set):
        self.assertEqual(virtual_balance, connector['virtualBalance'])
        self.assertEqual(weight, connector['weight'])
        self.assertEqual(is_virtual_balance_enabled, connector['isVirtualBalanceEnabled'])
        self.assertEqual(is_purchase_enabled, connector['isPurchaseEnabled'])
        self.assertEqual(is_set, connector['isSet'])

    def test_converter_initialize(self):
        """
        verifies the converter data after construction
        """
        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        token_address = icx_call(self, self.keys[0].address, converter_address, 'getToken', {})
        self.assertEqual(self.token_address, token_address)

        registry_address = icx_call(
            self, self.keys[0].address, converter_address, 'getRegistry', {})
        self.assertEqual(self.registry_address, registry_address)

        max_conversion_fee = icx_call(
            self, self.keys[0].address, converter_address, 'getMaxConversionFee', {})
        self.assertEqual(0, int(max_conversion_fee, 16))

        is_conversion_enabled = icx_call(
            self, self.keys[0].address, converter_address, 'isConversionsEnabled', {})
        self.assertEqual(1, int(is_conversion_enabled, 16))

    def test_converter_initialize_with_no_token(self):
        """
        should throw when attempting to construct a converter with no token
        """

        with self.assertRaises(AssertionError):
            self.setup_converter(
                ZERO_SCORE_ADDRESS, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

    def test_converter_initialize_with_no_registry(self):
        """
        should throw when attempting to construct a converter with no contract registry
        """

        with self.assertRaises(AssertionError):
            self.setup_converter(
                self.token_address, ZERO_SCORE_ADDRESS, 0, ZERO_SCORE_ADDRESS, 0)

    def test_converter_initialize_with_invalid_max_fee(self):
        """
        should throw when attempting to construct a converter with invalid max fee
        """

        with self.assertRaises(AssertionError):
            self.setup_converter(
                self.token_address, self.registry_address, 1000000000, ZERO_SCORE_ADDRESS, 0)

    def test_converter_initialize_with_connector(self):
        """
        verifies the first connector when provided at construction time
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, self.connector_token1_address, 200000)

        first_connector_address = icx_call(
            self, self.keys[0].address, converter_address, 'getConnectorAt', {'_index': 0})

        self.assertEqual(self.connector_token1_address, first_connector_address)

        first_connector = icx_call(self, self.keys[0].address, converter_address,
                                   'getConnector', {'_address': first_connector_address})
        self.verify_connector(first_connector, 0, 200000, False, True, True)

    def test_converter_initialize_with_connector_invalid_weight(self):
        """
        should throw when attempting to construct a converter with a connector with invalid weight
        """

        with self.assertRaises(AssertionError):
            self.setup_converter(
                self.token_address, self.registry_address, 0, self.connector_token1_address,
                1000001)

    def test_add_connector(self):
        """
        verifies the connector token count before / after adding a connector
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        connector_count = icx_call(
            self, self.keys[0].address, converter_address, 'getConnectorTokenCount', {})
        self.assertEqual(0, int(connector_count, 16))

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token1_address,
                             '_weight': 100000,
                             '_enableVirtualBalance': 0
                         })

        connector_count = icx_call(
            self, self.keys[0].address, converter_address, 'getConnectorTokenCount', {})
        self.assertEqual(1, int(connector_count, 16))

    def test_update_conversion_fee(self):
        """
        verifies the owner can update the fee
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 200000, ZERO_SCORE_ADDRESS, 0)

        new_conversion_fee = 30000
        transaction_call(self, self.keys[0], converter_address,
                         'setConversionFee', {'_conversionFee': new_conversion_fee})

        conversion_fee = icx_call(
            self, self.keys[0].address, converter_address, 'getConversionFee', {})

        self.assertEqual(new_conversion_fee, int(conversion_fee, 16))

    def test_update_conversion_fee_by_manager(self):
        """
        verifies the manager can update the fee
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 200000, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address,
                         'transferManagement', {'_newManager': self.keys[1].address})

        transaction_call(self, self.keys[1], converter_address,
                         'acceptManagement', {})

        new_conversion_fee = 30000
        transaction_call(self, self.keys[1], converter_address,
                         'setConversionFee', {'_conversionFee': new_conversion_fee})

        conversion_fee = icx_call(self, self.keys[1].address, converter_address,
                                  'getConversionFee', {})

        self.assertEqual(new_conversion_fee, int(conversion_fee, 16))

    def test_update_conversion_fee_invalid_value(self):
        """
        should throw when attempting to update the fee to an invalid value
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 200000, ZERO_SCORE_ADDRESS, 0)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address,
                             'setConversionFee', {'_conversionFee': 200001})

    def test_update_conversion_fee_invalid_sender(self):
        """
        should throw when a non owner and non manager attempts to update the fee
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 200000, ZERO_SCORE_ADDRESS, 0)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[1], converter_address,
                             'setConversionFee', {'_conversionFee': 30000})

    def test_get_final_amount(self):
        """
        verifies that getFinalAmount returns the correct amount
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 200000, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address,
                         'setConversionFee', {'_conversionFee': 10000})

        final_amount = icx_call(self, self.keys[1].address, converter_address,
                                'getFinalAmount', {'_amount': 500000, '_magnitude': 1})
        self.assertEqual(495000, int(final_amount, 16))

        final_amount = icx_call(self, self.keys[1].address, converter_address,
                                'getFinalAmount', {'_amount': 500000, '_magnitude': 2})
        self.assertEqual(490050, int(final_amount, 16))

    def test_disable_conversion(self):
        """
        verifies that an event is fired when an owner/manager disables conversions
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 200000, ZERO_SCORE_ADDRESS, 0)

        tx_result = transaction_call(self, self.keys[0], converter_address,
                                     'disableConversions', {'_disable': 1})

        event_log = tx_result['eventLogs'][0]
        self.assertEqual('ConversionsEnable(bool)', event_log['indexed'][0])
        self.assertEqual(False, int(event_log['data'][0], 16))

    def test_disable_conversion_non_change(self):
        """
        verifies that the conversionsEnabled event doesn't fire when
        passing identical value to conversionEnabled
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 200000, ZERO_SCORE_ADDRESS, 0)

        tx_result = transaction_call(self, self.keys[0], converter_address,
                                     'disableConversions', {'_disable': 0})

        self.assertEqual(0, len(tx_result['eventLogs']))

    def test_update_conversion_fee_event_log(self):
        """
        verifies that an event is fired when the owner updates the fee
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 200000, ZERO_SCORE_ADDRESS, 0)

        new_conversion_fee = 30000
        tx_result = transaction_call(self, self.keys[0], converter_address,
                                     'setConversionFee', {'_conversionFee': new_conversion_fee})

        event_log = tx_result['eventLogs'][0]
        self.assertEqual('ConversionFeeUpdate(int,int)', event_log['indexed'][0])
        self.assertEqual(0, int(event_log['data'][0], 16))
        self.assertEqual(new_conversion_fee, int(event_log['data'][1], 16))

    def test_update_conversion_fee_event_log_multiple(self):
        """
        verifies that an event is fired when the owner updates the fee multiple times
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 200000, ZERO_SCORE_ADDRESS, 0)

        prev_conversion_fee = 0
        new_conversion_fee = 30000

        for i in range(10):
            tx_result = transaction_call(self, self.keys[0], converter_address,
                                         'setConversionFee', {'_conversionFee': new_conversion_fee})

            event_log = tx_result['eventLogs'][0]
            self.assertEqual('ConversionFeeUpdate(int,int)', event_log['indexed'][0])
            self.assertEqual(prev_conversion_fee, int(event_log['data'][0], 16))
            self.assertEqual(new_conversion_fee, int(event_log['data'][1], 16))
            prev_conversion_fee = new_conversion_fee
            new_conversion_fee = new_conversion_fee - i * 100

    def test_add_two_connectors(self):
        """
        verifies that 2 connectors are added correctly
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token1_address,
                             '_weight': 100000,
                             '_enableVirtualBalance': 0
                         })

        connector = icx_call(self, self.keys[0].address, converter_address,
                             'getConnector', {'_address': self.connector_token1_address})
        self.verify_connector(connector, 0, 100000, False, True, True)

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token2_address,
                             '_weight': 200000,
                             '_enableVirtualBalance': 0
                         })

        connector = icx_call(self, self.keys[0].address, converter_address,
                             'getConnector', {'_address': self.connector_token2_address})
        self.verify_connector(connector, 0, 200000, False, True, True)

    def test_add_connector_by_non_owner(self):
        """
        should throw when a non owner attempts to add a connector
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[1], converter_address, 'addConnector',
                             {
                                 '_token': self.connector_token1_address,
                                 '_weight': 100000,
                                 '_enableVirtualBalance': 0
                             })

    def test_add_connector_when_active(self):
        """
        should throw when attempting to add a connector when the converter is active
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], self.token_address,
                         'transferOwnerShip', {'_newOwner': converter_address})

        transaction_call(self, self.keys[0], converter_address, 'acceptTokenOwnership', {})

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'addConnector',
                             {
                                 '_token': self.connector_token1_address,
                                 '_weight': 100000,
                                 '_enableVirtualBalance': 0
                             })

    def test_add_connector_invalid_address(self):
        """
        should throw when attempting to add a connector with invalid address
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'addConnector',
                             {
                                 '_token': str(ZERO_SCORE_ADDRESS),
                                 '_weight': 100000,
                                 '_enableVirtualBalance': 0
                             })

    def test_add_connector_weight_zero(self):
        """
        should throw when attempting to add a connector with weight = 0
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'addConnector',
                             {
                                 '_token': self.connector_token1_address,
                                 '_weight': 0,
                                 '_enableVirtualBalance': 0
                             })

    def test_add_connector_invalid_weight(self):
        """
        should throw when attempting to add a connector with weight greater than 100%
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'addConnector',
                             {
                                 '_token': self.connector_token1_address,
                                 '_weight': 1000001,
                                 '_enableVirtualBalance': 0
                             })

    def test_add_connector_with_token_address(self):
        """
        should throw when attempting to add the token as a connector
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'addConnector',
                             {
                                 '_token': self.token_address,
                                 '_weight': 100000,
                                 '_enableVirtualBalance': 0
                             })

    def test_add_connector_with_converter_address(self):
        """
        should throw when attempting to add the converter as a connector
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'addConnector',
                             {
                                 '_token': converter_address,
                                 '_weight': 100000,
                                 '_enableVirtualBalance': 0
                             })

    def test_add_connector_with_exist_connector(self):
        """
        should throw when attempting to add a connector that already exists
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token1_address,
                             '_weight': 100000,
                             '_enableVirtualBalance': 0
                         })

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'addConnector',
                             {
                                 '_token': self.connector_token1_address,
                                 '_weight': 100000,
                                 '_enableVirtualBalance': 0
                             })

    def test_add_two_connectors_over_weight(self):
        """
        should throw when attempting to add multiple connectors with total weight greater than 100%
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token1_address,
                             '_weight': 500000,
                             '_enableVirtualBalance': 0
                         })

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'addConnector',
                             {
                                 '_token': self.connector_token2_address,
                                 '_weight': 500001,
                                 '_enableVirtualBalance': 0
                             })

    def test_update_connector(self):
        """
        verifies that the owner can update a connector
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token1_address,
                             '_weight': 100000,
                             '_enableVirtualBalance': 0
                         })

        connector = icx_call(self, self.keys[0].address, converter_address,
                             'getConnector', {'_address': self.connector_token1_address})
        self.verify_connector(connector, 0, 100000, False, True, True)

        transaction_call(self, self.keys[0], converter_address, 'updateConnector',
                         {
                             '_connectorToken': self.connector_token1_address,
                             '_weight': 200000,
                             '_enableVirtualBalance': 1,
                             '_virtualBalance': 50
                         })

        connector = icx_call(self, self.keys[0].address, converter_address,
                             'getConnector', {'_address': self.connector_token1_address})
        self.verify_connector(connector, 50, 200000, True, True, True)

    def test_update_connector_by_non_owner(self):
        """
        should throw when a non owner attempts to update a connector
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token1_address,
                             '_weight': 100000,
                             '_enableVirtualBalance': 0
                         })

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[1], converter_address, 'updateConnector',
                             {
                                 '_connectorToken': self.connector_token1_address,
                                 '_weight': 200000,
                                 '_enableVirtualBalance': 1,
                                 '_virtualBalance': 50
                             })

    def test_update_non_exist_connector(self):
        """
        should throw when attempting to update a connector that does not exist
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token1_address,
                             '_weight': 100000,
                             '_enableVirtualBalance': 0
                         })

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'updateConnector',
                             {
                                 '_connectorToken': self.connector_token2_address,
                                 '_weight': 200000,
                                 '_enableVirtualBalance': 1,
                                 '_virtualBalance': 50
                             })

    def test_update_connector_with_zero_weight(self):
        """
        should throw when attempting to update a connector with weight = 0
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token1_address,
                             '_weight': 100000,
                             '_enableVirtualBalance': 0
                         })

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'updateConnector',
                             {
                                 '_connectorToken': self.connector_token1_address,
                                 '_weight': 0,
                                 '_enableVirtualBalance': 0,
                                 '_virtualBalance': 0
                             })

    def test_update_connector_with_over_weight(self):
        """
        should throw when attempting to update a connector with weight greater than 100%
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token1_address,
                             '_weight': 100000,
                             '_enableVirtualBalance': 0
                         })

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'updateConnector',
                             {
                                 '_connectorToken': self.connector_token1_address,
                                 '_weight': 1000001,
                                 '_enableVirtualBalance': 0,
                                 '_virtualBalance': 0
                             })

    def test_update_connector_total_over_weight(self):
        """
        should throw when attempting to update a connector that will result in total weight greater than 100%
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token1_address,
                             '_weight': 500000,
                             '_enableVirtualBalance': 0
                         })

        transaction_call(self, self.keys[0], converter_address, 'addConnector',
                         {
                             '_token': self.connector_token2_address,
                             '_weight': 400000,
                             '_enableVirtualBalance': 0
                         })

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address, 'updateConnector',
                             {
                                 '_connectorToken': self.connector_token2_address,
                                 '_weight': 500001,
                                 '_enableVirtualBalance': 0,
                                 '_virtualBalance': 0
                             })

    def test_disable_enable_conversions(self):
        """
        verifies that the owner can disable / re-enable conversions
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        is_conversion_enabled = icx_call(self, self.keys[0].address, converter_address,
                                         'isConversionsEnabled', {})
        self.assertEqual(True, int(is_conversion_enabled, 16))

        transaction_call(self, self.keys[0], converter_address,
                         'disableConversions', {'_disable': 1})

        is_conversion_enabled = icx_call(self, self.keys[0].address, converter_address,
                                         'isConversionsEnabled', {})
        self.assertEqual(False, int(is_conversion_enabled, 16))

        transaction_call(self, self.keys[0], converter_address,
                         'disableConversions', {'_disable': 0})

        is_conversion_enabled = icx_call(self, self.keys[0].address, converter_address,
                                         'isConversionsEnabled', {})
        self.assertEqual(True, int(is_conversion_enabled, 16))

    def test_disable_enable_conversions_by_manager(self):
        """
        verifies that the owner can disable / re-enable conversions
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        transaction_call(self, self.keys[0], converter_address,
                         'transferManagement', {'_newManager': self.keys[1].address})

        transaction_call(self, self.keys[1], converter_address,
                         'acceptManagement', {})

        is_conversion_enabled = icx_call(self, self.keys[1].address, converter_address,
                                         'isConversionsEnabled', {})
        self.assertEqual(True, int(is_conversion_enabled, 16))

        transaction_call(self, self.keys[1], converter_address,
                         'disableConversions', {'_disable': 1})

        is_conversion_enabled = icx_call(self, self.keys[1].address, converter_address,
                                         'isConversionsEnabled', {})
        self.assertEqual(False, int(is_conversion_enabled, 16))

        transaction_call(self, self.keys[1], converter_address,
                         'disableConversions', {'_disable': 0})

        is_conversion_enabled = icx_call(self, self.keys[1].address, converter_address,
                                         'isConversionsEnabled', {})
        self.assertEqual(True, int(is_conversion_enabled, 16))

    def test_disable_conversions_by_non_owner(self):
        """
        verifies that the owner can disable / re-enable conversions
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, ZERO_SCORE_ADDRESS, 0)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[1], converter_address,
                             'disableConversions', {'_disable': 1})

    def test_disable_enable_purchase(self):
        """
        verifies that the owner can disable / re-enable connector purchases
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, self.connector_token1_address, 100000)

        connector = icx_call(self, self.keys[0].address, converter_address,
                             'getConnector', {'_address': self.connector_token1_address})
        self.verify_connector(connector, 0, 100000, False, True, True)

        transaction_call(self, self.keys[0], converter_address, 'disableConnectorPurchases',
                         {'_connectorToken': self.connector_token1_address, '_disable': 1})

        connector = icx_call(self, self.keys[0].address, converter_address,
                             'getConnector', {'_address': self.connector_token1_address})
        self.verify_connector(connector, 0, 100000, False, False, True)

        transaction_call(self, self.keys[0], converter_address, 'disableConnectorPurchases',
                         {'_connectorToken': self.connector_token1_address, '_disable': 0})

        connector = icx_call(self, self.keys[0].address, converter_address,
                             'getConnector', {'_address': self.connector_token1_address})
        self.verify_connector(connector, 0, 100000, False, True, True)

    def test_disable_purchase_by_non_owner(self):
        """
        should throw when a non owner attempts to disable connector purchases
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, self.connector_token1_address, 100000)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[1], converter_address,
                             'disableConnectorPurchases',
                             {'_connectorToken': self.connector_token1_address, '_disable': 1})

    def test_disable_purchase_for_non_exist_connector(self):
        """
        should throw when attempting to disable connector purchases for a connector that does not exist
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, self.connector_token1_address, 100000)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address,
                             'disableConnectorPurchases',
                             {'_connectorToken': self.connector_token2_address, '_disable': 1})

    def test_connector_balance(self):
        """
        verifies that the correct connector balance is returned regardless of whether virtual balance is set or not
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, self.connector_token1_address, 100000)

        balance = icx_call(self, self.keys[0].address, converter_address,
                           'getConnectorBalance',
                           {'_connectorToken': self.connector_token1_address})
        self.assertEqual(0, int(balance, 16))

        transaction_call(self, self.keys[0], self.connector_token1_address,
                         'transfer', {'_to': converter_address, '_value': 1000})

        balance = icx_call(self, self.keys[0].address, converter_address,
                           'getConnectorBalance',
                           {'_connectorToken': self.connector_token1_address})
        self.assertEqual(1000, int(balance, 16))

        transaction_call(self, self.keys[0], converter_address,
                         'updateConnector',
                         {
                             '_connectorToken': self.connector_token1_address,
                             '_weight': 200000,
                             '_enableVirtualBalance': 1,
                             '_virtualBalance': 5000
                         })

        balance = icx_call(self, self.keys[0].address, converter_address,
                           'getConnectorBalance',
                           {'_connectorToken': self.connector_token1_address})
        self.assertEqual(5000, int(balance, 16))

        transaction_call(self, self.keys[0], converter_address,
                         'updateConnector',
                         {
                             '_connectorToken': self.connector_token1_address,
                             '_weight': 200000,
                             '_enableVirtualBalance': 0,
                             '_virtualBalance': 5000
                         })

        balance = icx_call(self, self.keys[0].address, converter_address,
                           'getConnectorBalance',
                           {'_connectorToken': self.connector_token1_address})
        self.assertEqual(1000, int(balance, 16))

    def test_connector_balance_for_non_exist_connector(self):
        """
        should throw when attempting to retrieve the balance for a connector that does not exist
        """

        converter_address = self.setup_converter(
            self.token_address, self.registry_address, 0, self.connector_token1_address, 100000)

        # noinspection PyTypeChecker
        with self.assertRaises(BaseException):
            icx_call(self, self.keys[0].address, converter_address, 'getConnectorBalance',
                     {'_connectorToken': self.connector_token2_address})

    def test_transfer_ownership(self):
        """
        should throw when the owner attempts to transfer the token ownership
        """

        converter_address = self.init_converter(True)

        transaction_call(self, self.keys[0], converter_address,
                         'transferTokenOwnership',
                         {
                             '_newOwner': str(self.keys[1].address),
                         })

        token_address = icx_call(self, self.keys[0].address, converter_address, 'getToken', {})

        new_owner = icx_call(self, self.keys[0].address, token_address, 'getNewOwner', {})

        self.assertEqual(str(self.keys[1].address), new_owner)

    def test_transfer_ownership_by_non_owner(self):
        """
        should throw when a non owner attempts to transfer the token ownership
        """

        converter_address = self.init_converter(True)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[1], converter_address,
                             'transferTokenOwnership',
                             {
                                 '_newOwner': str(self.keys[2].address),
                             })

    def test_withdraw_connector_token(self):
        """
        verifies that the owner can withdraw a non connector token from the converter while the converter is not active
        """

        converter_address = self.init_converter(False)

        transaction_call(self, self.keys[0], converter_address,
                         'withdrawTokens',
                         {
                             '_token': self.connector_token1_address,
                             '_to': str(self.keys[1].address),
                             '_amount': 50,
                         })

        balance = icx_call(self, self.keys[0].address, self.connector_token1_address,
                           'balanceOf', {'_owner': str(self.keys[1].address)})
        self.assertEqual(50, int(balance, 16))

    def test_withdraw_connector_token_when_active(self):
        """
        should throw when the owner attempts to withdraw a connector token while the converter is active
        """

        converter_address = self.init_converter(True)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[0], converter_address,
                             'withdrawTokens',
                             {
                                 '_token': self.connector_token1_address,
                                 '_to': str(self.keys[1].address),
                                 '_amount': 50,
                             })

    def test_withdraw_connector_token_by_non_owner(self):
        """
        should throw when a non owner attempts to withdraw a connector token while the converter is not active
        """

        converter_address = self.init_converter(False)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[1], converter_address,
                             'withdrawTokens',
                             {
                                 '_token': self.connector_token1_address,
                                 '_to': str(self.keys[1].address),
                                 '_amount': 50,
                             })

    def test_withdraw_connector_token_by_non_owner_when_active(self):
        """
        should throw when a non owner attempts to withdraw a connector token while the converter is active
        """

        converter_address = self.init_converter(True)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[1], converter_address,
                             'withdrawTokens',
                             {
                                 '_token': self.connector_token1_address,
                                 '_to': str(self.keys[1].address),
                                 '_amount': 50,
                             })

    def test_return_amount(self):
        """
        verifies that getReturn returns a valid amount
        """

        converter_address = self.init_converter(True)

        return_value = icx_call(self, self.keys[0].address, converter_address,
                                'getReturn',
                                {
                                    '_fromToken': self.connector_token1_address,
                                    '_toToken': self.token_address,
                                    '_amount': 500,
                                })

        self.assertGreater(return_value['amount'], 0)

    def test_return_and_purchase_return(self):
        """
        verifies that getReturn returns a valid amount
        """

        converter_address = self.init_converter(True)

        return_value = icx_call(self, self.keys[0].address, converter_address,
                                'getReturn',
                                {
                                    '_fromToken': self.connector_token1_address,
                                    '_toToken': self.token_address,
                                    '_amount': 500,
                                })

        purchase_return_value = icx_call(self, self.keys[0].address, converter_address,
                                         'getPurchaseReturn',
                                         {
                                             '_connectorToken': self.connector_token1_address,
                                             '_amount': 500,
                                         })

        self.assertEqual(return_value['amount'], purchase_return_value['amount'])

    def test_return_and_sale_return(self):
        """
        verifies that getReturn returns the same amount as getSaleReturn when converting from the token to a connector
        """

        converter_address = self.init_converter(True)

        return_value = icx_call(self, self.keys[0].address, converter_address,
                                'getReturn',
                                {
                                    '_fromToken': self.token_address,
                                    '_toToken': self.connector_token1_address,
                                    '_amount': 500,
                                })

        purchase_return_value = icx_call(self, self.keys[0].address, converter_address,
                                         'getSaleReturn',
                                         {
                                             '_connectorToken': self.connector_token1_address,
                                             '_amount': 500,
                                         })

        self.assertEqual(return_value['amount'], purchase_return_value['amount'])

    def test_return_with_invalid_from_token(self):
        """
        should throw when attempting to get the return with an invalid from token address
        """
        converter_address = self.init_converter(True)

        # noinspection PyTypeChecker
        with self.assertRaises(BaseException):
            icx_call(self, self.keys[0].address, converter_address,
                     'getReturn',
                     {
                         '_fromToken': str(ZERO_SCORE_ADDRESS),
                         '_toToken': self.connector_token2_address,
                         '_amount': 500,
                     })

    def test_return_with_invalid_to_token(self):
        """
        should throw when attempting to get the return with an invalid to token address
        """
        converter_address = self.init_converter(True)

        # noinspection PyTypeChecker
        with self.assertRaises(BaseException):
            icx_call(self, self.keys[0].address, converter_address,
                     'getReturn',
                     {
                         '_fromToken': self.connector_token1_address,
                         '_toToken': str(ZERO_SCORE_ADDRESS),
                         '_amount': 500,
                     })

    def test_return_with_identical_from_to_token(self):
        """
        should throw when attempting to get the return with identical from/to addresses
        """
        converter_address = self.init_converter(True)

        # noinspection PyTypeChecker
        with self.assertRaises(BaseException):
            icx_call(self, self.keys[0].address, converter_address,
                     'getReturn',
                     {
                         '_fromToken': self.connector_token1_address,
                         '_toToken': self.connector_token1_address,
                         '_amount': 500,
                     })

    def test_purchase_return_when_inactive(self):
        """
        should throw when attempting to get the purchase return while the converter is not active
        """
        converter_address = self.init_converter(False)

        # noinspection PyTypeChecker
        with self.assertRaises(BaseException):
            icx_call(self, self.keys[0].address, converter_address,
                     'getPurchaseReturn',
                     {
                         '_connectorToken': self.connector_token1_address,
                         '_amount': 500,
                     })

    def test_purchase_return_for_non_connector_token(self):
        """
        should throw when attempting to get the purchase return with a non connector address
        """
        converter_address = self.init_converter(True)

        # noinspection PyTypeChecker
        with self.assertRaises(BaseException):
            icx_call(self, self.keys[0].address, converter_address,
                     'getPurchaseReturn',
                     {
                         '_connectorToken': self.token_address,
                         '_amount': 500,
                     })

    def test_purchase_return_when_disabled(self):
        """
        should throw when attempting to get the purchase return while purchasing with the connector is disabled
        """
        converter_address = self.init_converter(True)

        transaction_call(self, self.keys[0], converter_address,
                         'disableConnectorPurchases',
                         {
                             '_connectorToken': self.connector_token1_address,
                             '_disable': 1,
                         })

        # noinspection PyTypeChecker
        with self.assertRaises(BaseException):
            icx_call(self, self.keys[0].address, converter_address,
                     'getPurchaseReturn',
                     {
                         '_connectorToken': self.connector_token1_address,
                         '_amount': 500,
                     })

    def test_sale_return_when_inactive(self):
        """
        should throw when attempting to get the sale return while the converter is not active
        """
        converter_address = self.init_converter(False)

        # noinspection PyTypeChecker
        with self.assertRaises(BaseException):
            icx_call(self, self.keys[0].address, converter_address,
                     'getSaleReturn',
                     {
                         '_connectorToken': self.connector_token1_address,
                         '_amount': 500,
                     })

    def test_sale_return_for_non_connector_token(self):
        """
        should throw when attempting to get the sale return with a non connector address
        """
        converter_address = self.init_converter(True)

        # noinspection PyTypeChecker
        with self.assertRaises(BaseException):
            icx_call(self, self.keys[0].address, converter_address,
                     'getSaleReturn',
                     {
                         '_connectorToken': self.token_address,
                         '_amount': 500,
                     })

    def test_return_and_cross_connector_return(self):
        """
        verifies that getReturn returns the same amount as getCrossConnectorReturn when converting between 2 connectors
        """

        converter_address = self.init_converter(True)

        return_value = icx_call(self, self.keys[0].address, converter_address,
                                'getReturn',
                                {
                                    '_fromToken': self.connector_token1_address,
                                    '_toToken': self.connector_token2_address,
                                    '_amount': 500,
                                })

        cross_return_value = icx_call(self, self.keys[0].address, converter_address,
                                      'getCrossConnectorReturn',
                                      {
                                          '_fromToken': self.connector_token1_address,
                                          '_toToken': self.connector_token2_address,
                                          '_amount': 500,
                                      })

        self.assertEqual(return_value['amount'], cross_return_value['amount'])

    def test_update_registry(self):
        """
        should allow anyone to update the registry address
        """
        converter_address = self.init_converter(True)

        new_registry_address = self.setup_registry(self.network_address)

        transaction_call(self, self.keys[0], self.registry_address,
                         'registerAddress',
                         {
                             '_scoreName': 'ScoreRegistry',
                             '_scoreAddress': new_registry_address,
                         })

        transaction_call(self, self.keys[1], converter_address, 'updateRegistry', {})

        registry_address = icx_call(self, self.keys[0].address, converter_address,
                                    'getRegistry', {})
        prev_registry_address = icx_call(self, self.keys[0].address, converter_address,
                                         'getPreviousRegistry', {})

        self.assertEqual(new_registry_address, registry_address)
        self.assertEqual(self.registry_address, prev_registry_address)

    def test_update_registry_with_no_new_registry_registered(self):
        """
        should throw when attempting to update the registry when no new registry is set
        """
        converter_address = self.init_converter(True)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[1], converter_address, 'updateRegistry', {})

    def test_update_restore_registry(self):
        """
        should allow the owner to restore the previous registry and disable updates
        """
        converter_address = self.init_converter(True)

        new_registry_address = self.setup_registry(self.network_address)

        transaction_call(self, self.keys[0], self.registry_address,
                         'registerAddress',
                         {
                             '_scoreName': 'ScoreRegistry',
                             '_scoreAddress': new_registry_address,
                         })

        transaction_call(self, self.keys[1], converter_address, 'updateRegistry', {})

        transaction_call(self, self.keys[0], converter_address, 'restoreRegistry', {})

        registry_address = icx_call(self, self.keys[0].address, converter_address,
                                    'getRegistry', {})
        prev_registry_address = icx_call(self, self.keys[0].address, converter_address,
                                         'getPreviousRegistry', {})

        self.assertEqual(self.registry_address, registry_address)
        self.assertEqual(self.registry_address, prev_registry_address)

        with self.assertRaises(AssertionError):
            transaction_call(self, self.keys[1], converter_address, 'updateRegistry', {})

        transaction_call(self, self.keys[0], converter_address, 'updateRegistry', {})

        registry_address = icx_call(self, self.keys[0].address, converter_address,
                                    'getRegistry', {})
        prev_registry_address = icx_call(self, self.keys[0].address, converter_address,
                                         'getPreviousRegistry', {})
        self.assertEqual(new_registry_address, registry_address)
        self.assertEqual(self.registry_address, prev_registry_address)
