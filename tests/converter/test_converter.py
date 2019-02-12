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

import os
import unittest
from unittest.mock import Mock, patch

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message
from iconservice.iconscore.internal_call import InternalCall

from contracts.converter.converter import Converter, TRANSFER_DATA
from contracts.formula import FixedMapFormula
from contracts.score_registry.score_registry import ScoreRegistry
from contracts.utility.flexible_token_controller import FlexibleTokenController
from tests import MultiPatch, patch_property, ScorePatcher, create_db, assert_inter_call


# noinspection PyUnresolvedReferences
class TestConverter(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(Converter)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + os.urandom(20).hex())
        self.score = Converter(create_db(self.score_address))

        self.owner = Address.from_string("hx" + os.urandom(20).hex())
        self.token = Address.from_string("cx" + os.urandom(20).hex())
        registry = Address.from_string("cx" + os.urandom(20).hex())
        max_conversion_fee = 1000000
        self.initial_connector_token = Address.from_string("cx" + os.urandom(20).hex())
        self.initial_connector_weight = 500000

        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.on_install(self.token, registry, max_conversion_fee,
                                  self.initial_connector_token, self.initial_connector_weight)
            FlexibleTokenController.on_install.assert_called_with(self.score, self.token)
            self.score._token.set(self.token)

            self.assertEqual(registry, self.score._registry.get())
            self.assertEqual(registry, self.score._prev_registry.get())
            self.assertEqual(max_conversion_fee, self.score._max_conversion_fee.get())

            self.assertEqual(True, self.score._connectors[self.initial_connector_token].is_set.get())
            self.assertEqual(self.initial_connector_weight,
                             self.score._connectors[self.initial_connector_token].weight.get())

    def tearDown(self):
        self.patcher.stop()

    def test_tokenFallback_deposit(self):
        # Mocks parent functions
        self.score.getOwner.return_value = self.owner
        self.score._is_active.return_value = False

        network_address = Address.from_string("cx" + os.urandom(20).hex())

        # success case
        token = self.initial_connector_token
        sender = self.owner
        value = 100
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(token)),
            patch.object(InternalCall, 'other_external_call', return_value=network_address)
        ]):
            self.score.tokenFallback(sender, value, b'None')

        # the value is less than zero
        token = self.initial_connector_token
        sender = self.owner
        value = -100
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(token)),
            patch.object(InternalCall, 'other_external_call', return_value=network_address)
        ]):
            self.assertRaises(RevertException, self.score.tokenFallback, sender, value, b'None')

        # the sender is not owner
        token = self.initial_connector_token
        sender = Address.from_string("hx" + os.urandom(20).hex())
        value = 100
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(token)),
            patch.object(InternalCall, 'other_external_call', return_value=network_address)
        ]):
            self.assertRaises(RevertException, self.score.tokenFallback, sender, value, b'None')

        # the token is not connector token
        token = Address.from_string("cx" + os.urandom(20).hex())
        sender = self.owner
        value = 100
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(token)),
            patch.object(InternalCall, 'other_external_call', return_value=network_address)
        ]):
            self.assertRaises(RevertException, self.score.tokenFallback, sender, value, b'None')

        # the converter is active
        self.score._is_active.return_value = True
        token = self.initial_connector_token
        sender = self.owner
        value = 100
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(token)),
            patch.object(InternalCall, 'other_external_call', return_value=network_address)
        ]):
            self.assertRaises(RevertException, self.score.tokenFallback, sender, value, b'None')

    def test_tokenFallback_convert_called_wrong_params(self):
        # Mocks parent functions
        self.score.getOwner.return_value = self.owner
        self.score._is_active.return_value = True
        self.score._convert = Mock()

        network_address = Address.from_string("cx" + os.urandom(20).hex())

        to_token = Address.from_string("cx" + os.urandom(20).hex())

        # missing param `minReturn`
        data = {
            'toToken': str(to_token),
        }

        token = self.initial_connector_token
        value = 100
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(token)),
            patch.object(InternalCall, 'other_external_call', return_value=network_address)
        ]):

            self.assertRaises(RevertException, self.score.tokenFallback,
                              network_address, value, json_dumps(data).encode())

            self.score._convert.assert_not_called()

    def test_tokenFallback_buy_called(self):
        # Mocks parent functions
        self.score.getOwner.return_value = self.owner
        self.score._is_active.return_value = True
        self.score._buy = Mock()

        network_address = Address.from_string("cx" + os.urandom(20).hex())

        to_token = self.token
        min_return = 10

        data = {
            'toToken': str(to_token),
            'minReturn': min_return
        }

        # success case
        token = self.initial_connector_token
        value = 100
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(token)),
            patch.object(InternalCall, 'other_external_call', return_value=network_address)
        ]):
            self.score.tokenFallback(network_address, value, json_dumps(data).encode())
            assert_inter_call(self,
                              self.score.address,
                              self.score._registry.get(),
                              'getAddress',
                              [ScoreRegistry.NETWORK])
            self.score._buy.assert_called_with(
                network_address, token, value, min_return)

    def test_tokenFallback_sell_called(self):
        # Mocks parent functions
        self.score.getOwner.return_value = self.owner
        self.score._is_active.return_value = True
        self.score._sell = Mock()

        network_address = Address.from_string("cx" + os.urandom(20).hex())

        to_token = self.initial_connector_token
        min_return = 10

        data = {
            'toToken': str(to_token),
            'minReturn': min_return
        }

        # success case
        token = self.token
        value = 100
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(token)),
            patch.object(InternalCall, 'other_external_call', return_value=network_address)
        ]):
            self.score.tokenFallback(network_address, value, json_dumps(data).encode())
            assert_inter_call(self,
                              self.score.address,
                              self.score._registry.get(),
                              'getAddress',
                              [ScoreRegistry.NETWORK])
            self.score._sell.assert_called_with(
                network_address, to_token, value, min_return)

    def test_tokenFallback_cross_convert_called(self):
        # Mocks parent functions
        self.score.getOwner.return_value = self.owner
        self.score._is_active.return_value = True
        self.score._convert_cross_connector = Mock()

        network_address = Address.from_string("cx" + os.urandom(20).hex())

        to_token = Address.from_string("cx" + os.urandom(20).hex())
        to_token_weight = 500000
        self.score.addConnector(to_token, to_token_weight, False)

        min_return = 10

        data = {
            'toToken': str(to_token),
            'minReturn': min_return
        }

        # success case
        token = self.initial_connector_token
        value = 100
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(token)),
            patch.object(InternalCall, 'other_external_call', return_value=network_address)
        ]):
            self.score.tokenFallback(network_address, value, json_dumps(data).encode())
            assert_inter_call(self,
                              self.score.address,
                              self.score._registry.get(),
                              'getAddress',
                              [ScoreRegistry.NETWORK])
            self.score._convert_cross_connector.assert_called_with(
                network_address, token, to_token, value, min_return)

    def test_buy(self):
        connector_token2 = Address.from_string("cx" + os.urandom(20).hex())
        connector_token2_weight = 500000
        self.score.addConnector(connector_token2, connector_token2_weight, False)

        return_amount = 100
        return_fee = 1
        connector_balance = 100
        trader = Address.from_string("cx" + os.urandom(20).hex())
        amount = 100
        min_return = 100

        purchase_return = {'amount': return_amount, 'fee': return_fee}
        self.score.getPurchaseReturn = Mock(return_value=purchase_return)
        self.score.getConnectorBalance = Mock(return_value=connector_balance)
        inter_call_return = Mock()

        with patch.object(InternalCall, 'other_external_call', return_value=inter_call_return):
            result = self.score._buy(trader, connector_token2, amount, min_return)
            assert_inter_call(self,
                              self.score.address,
                              self.score._token.get(),
                              'issue',
                              [trader, return_amount])
            self.score.Conversion.assert_called_with(
                connector_token2,
                self.score._token.get(),
                trader,
                amount,
                return_amount,
                return_fee
            )
            self.score.PriceDataUpdate.assert_called_with(
                connector_token2,
                inter_call_return,
                connector_balance,
                connector_token2_weight
            )
            self.assertEqual(return_amount, result)

    def test_sell(self):
        connector_token2 = Address.from_string("cx" + os.urandom(20).hex())
        connector_token2_weight = 500000
        self.score.addConnector(connector_token2, connector_token2_weight, False)

        return_amount = 100
        return_fee = 1
        connector_balance = 1000
        trader = Address.from_string("cx" + os.urandom(20).hex())
        amount = 100
        min_return = 100

        sale_return = {'amount': return_amount, 'fee': return_fee}
        self.score.getSaleReturn = Mock(return_value=sale_return)
        self.score.getConnectorBalance = Mock(return_value=connector_balance)
        inter_call_return = Mock()

        with patch.object(InternalCall, 'other_external_call', return_value=inter_call_return):
            result = self.score._sell(trader, connector_token2, amount, min_return)
            assert_inter_call(self,
                              self.score.address,
                              self.score._token.get(),
                              'destroy',
                              [self.score.address, return_amount])
            self.score.Conversion.assert_called_with(
                self.score._token.get(),
                connector_token2,
                trader,
                amount,
                return_amount,
                return_fee
            )
            self.score.PriceDataUpdate.assert_called_with(
                connector_token2,
                inter_call_return,
                connector_balance,
                connector_token2_weight
            )
            self.assertEqual(return_amount, result)

    def test_convert_cross_connector(self):
        connector_token2 = Address.from_string("cx" + os.urandom(20).hex())
        connector_token2_weight = 500000
        self.score.addConnector(connector_token2, connector_token2_weight, False)

        return_amount = 100
        return_fee = 1
        connector_balance = 1000
        trader = Address.from_string("cx" + os.urandom(20).hex())
        amount = 100
        min_return = 100

        convert_return = {'amount': return_amount, 'fee': return_fee}
        self.score.getCrossConnectorReturn = Mock(return_value=convert_return)
        self.score.getConnectorBalance = Mock(return_value=connector_balance)
        inter_call_return = Mock()

        with patch.object(InternalCall, 'other_external_call', return_value=inter_call_return):
            self.score._convert_cross_connector(
                trader,
                self.initial_connector_token,
                connector_token2,
                amount, min_return)
            assert_inter_call(self,
                              self.score.address,
                              connector_token2,
                              'transfer',
                              [trader, return_amount, TRANSFER_DATA])

            self.score.Conversion.assert_called_with(
                self.initial_connector_token,
                connector_token2,
                trader,
                amount,
                return_amount,
                return_fee
            )

            first_price_update_event = self.score.PriceDataUpdate.call_args_list[0]
            self.assertEqual(first_price_update_event[0][0], self.initial_connector_token)
            self.assertEqual(first_price_update_event[0][1], inter_call_return)
            self.assertEqual(first_price_update_event[0][2], connector_balance)
            self.assertEqual(first_price_update_event[0][3], self.initial_connector_weight)

            second_price_update_event = self.score.PriceDataUpdate.call_args_list[1]
            self.assertEqual(second_price_update_event[0][0], connector_token2)
            self.assertEqual(second_price_update_event[0][1], inter_call_return)
            self.assertEqual(second_price_update_event[0][2], connector_balance)
            self.assertEqual(second_price_update_event[0][3], connector_token2_weight)

    def test_addConnector(self):
        self.score.require_owner_only.reset_mock()

        connector_token = Address.from_string("cx" + os.urandom(20).hex())
        connector_weight = 500000

        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.addConnector(connector_token, connector_weight, False)
            self.score.require_owner_only.assert_called()

            self.assertEqual(connector_weight, self.score._connectors[connector_token].weight.get())
            self.assertEqual(
                False, self.score._connectors[connector_token].is_virtual_balance_enabled.get())
            self.assertEqual(True, self.score._connectors[connector_token].is_set.get())

    def test_updateConnector(self):
        self.score.require_owner_only.reset_mock()

        connector_token = self.initial_connector_token
        connector_weight = 100000

        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.updateConnector(connector_token, connector_weight, True, 10000)
            self.score.require_owner_only.assert_called()

            self.assertEqual(connector_weight, self.score._connectors[connector_token].weight.get())
            self.assertEqual(
                True, self.score._connectors[connector_token].is_virtual_balance_enabled.get())
            self.assertEqual(True, self.score._connectors[connector_token].is_set.get())

    def test_updateConnector_wrong_max_weight(self):
        self.score.require_owner_only.reset_mock()

        connector_token = self.initial_connector_token
        connector_weight = 1000001

        self.assertRaises(RevertException,
                          self.score.updateConnector,
                          connector_token, connector_weight, True, 10000)

    def test_disableConnectorPurchases(self):
        self.score.require_owner_or_manager_only.reset_mock()

        self.score._conversions_enabled.set(True)

        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.disableConnectorPurchases(self.initial_connector_token, True)
            self.score.require_owner_only.assert_called()

            connector_token = self.score._connectors[self.initial_connector_token]
            self.assertEqual(False, connector_token.is_purchase_enabled.get())
            self.score.disableConnectorPurchases(self.initial_connector_token, False)
            self.assertEqual(True, connector_token.is_purchase_enabled.get())

    def test_updateRegistry(self):
        self.score._allow_registry_update.set(True)

        old_registry = self.score._registry.get()
        new_registry = Address.from_string("cx" + os.urandom(20).hex())

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call', return_value=new_registry)
        ]):
            self.score.updateRegistry()

            assert_inter_call(
                self,
                self.score.address,
                old_registry,
                'getAddress',
                [ScoreRegistry.SCORE_REGISTRY])

            self.assertEqual(old_registry, self.score._prev_registry.get())
            self.assertEqual(new_registry, self.score._registry.get())

    def test_restoreRegistry(self):
        self.score.require_owner_or_manager_only.reset_mock()

        prev_registry = self.score._prev_registry.get()

        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.restoreRegistry()
            self.score.require_owner_or_manager_only.assert_called()

            self.assertEqual(prev_registry, self.score._prev_registry.get())
            self.assertEqual(prev_registry, self.score._registry.get())

    def test_disableRegistryUpdate(self):
        self.score.require_owner_or_manager_only.reset_mock()

        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.disableRegistryUpdate(True)
            self.score.require_owner_or_manager_only.assert_called()

            self.assertEqual(False, self.score._allow_registry_update.get())
            self.score.disableRegistryUpdate(False)
            self.assertEqual(True, self.score._allow_registry_update.get())

    def test_disableConversions(self):
        self.score.require_owner_or_manager_only.reset_mock()

        self.score._conversions_enabled.set(True)

        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.disableConversions(True)
            self.score.require_owner_or_manager_only.assert_called()
            self.score.ConversionsEnable.assert_called_with(False)

            self.assertEqual(False, self.score._conversions_enabled.get())
            self.score.disableConversions(False)
            self.assertEqual(True, self.score._conversions_enabled.get())

    def test_setConversionFee(self):
        self.score.require_owner_or_manager_only.reset_mock()

        old_conversion_fee = self.score._conversion_fee.get()
        conversion_fee = 10000

        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.setConversionFee(conversion_fee)
            self.score.require_owner_or_manager_only.assert_called()
            self.score.ConversionFeeUpdate.assert_called_with(old_conversion_fee, conversion_fee)

            self.assertEqual(self.score._conversion_fee.get(), conversion_fee)

    def test_withdrawTokens(self):
        to = Address.from_string("hx" + os.urandom(20).hex())
        amount = 100

        self.score._is_active.return_value = True
        self.score._connectors[self.initial_connector_token].is_set.set(False)
        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.withdrawTokens(self.initial_connector_token, to, amount)
            self.score._is_active.assert_called()
            FlexibleTokenController.withdrawTokens.assert_called_with(
                self.initial_connector_token, to, amount)

        self.score._is_active.reset_mock()
        self.score._is_active.return_value = False
        self.score._connectors[self.initial_connector_token].is_set.set(True)
        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.withdrawTokens(self.initial_connector_token, to, amount)
            self.score._is_active.assert_called()
            FlexibleTokenController.withdrawTokens.assert_called_with(
                self.initial_connector_token, to, amount)

        self.score._is_active.reset_mock()
        self.score._is_active.return_value = False
        self.score._connectors[self.initial_connector_token].is_set.set(False)
        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.score.withdrawTokens(self.initial_connector_token, to, amount)
            self.score._is_active.assert_called()
            FlexibleTokenController.withdrawTokens.assert_called_with(
                self.initial_connector_token, to, amount)

    def test_withdrawTokens_failure(self):
        to = Address.from_string("hx" + os.urandom(20).hex())
        amount = 100

        self.score._is_active.return_value = True
        self.score._connectors[self.initial_connector_token].is_set.set(True)
        with patch_property(IconScoreBase, 'msg', Message(self.owner)):
            self.assertRaises(RevertException,
                              self.score.withdrawTokens,
                              self.initial_connector_token, to, amount)
            self.score._is_active.assert_called()

    def test_getConnectorTokenCount(self):
        size_by_db = len(self.score._connector_tokens)
        self.assertEqual(size_by_db, self.score.getConnectorTokenCount())

    def test_getConversionFee(self):
        fee_by_db = self.score._conversion_fee.get()
        self.assertEqual(fee_by_db, self.score.getConversionFee())

    def test_getConnector(self):
        result_dict = self.score.getConnector(self.initial_connector_token)
        self.assertIn('virtualBalance', result_dict)
        self.assertIn('weight', result_dict)
        self.assertIn('isVirtualBalanceEnabled', result_dict)
        self.assertIn('isPurchaseEnabled', result_dict)
        self.assertIn('isSet', result_dict)

        result_dict = self.score.getConnector(ZERO_SCORE_ADDRESS)
        self.assertNotIn('virtualBalance', result_dict)
        self.assertNotIn('weight', result_dict)
        self.assertNotIn('isVirtualBalanceEnabled', result_dict)
        self.assertNotIn('isPurchaseEnabled', result_dict)
        self.assertNotIn('isSet', result_dict)

    def test_getConnectorBalance(self):
        balance = 100

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call', return_value=balance)
        ]):
            result_balance = self.score.getConnectorBalance(self.initial_connector_token)

            assert_inter_call(
                self,
                self.score.address,
                self.initial_connector_token,
                'balanceOf',
                [self.score.address])

            self.assertEqual(result_balance, balance)

    def test_getReturn(self):
        amount = 1000

        self.score.getPurchaseReturn = Mock()
        self.score.getSaleReturn = Mock()
        self.score.getCrossConnectorReturn = Mock()

        from_token = Address.from_string("cx" + os.urandom(20).hex())
        to_token = Address.from_string("cx" + os.urandom(20).hex())

        with patch.object(IconScoreBase, 'msg', Message(self.owner)):
            self.score.getReturn(from_token, to_token, amount)
            self.score.getCrossConnectorReturn.assert_called_with(from_token, to_token, amount)

        from_token = self.token
        to_token = Address.from_string("cx" + os.urandom(20).hex())
        with patch.object(IconScoreBase, 'msg', Message(self.owner)):
            self.score.getReturn(from_token, to_token, amount)
            self.score.getSaleReturn.assert_called_with(to_token, amount)

        from_token = Address.from_string("cx" + os.urandom(20).hex())
        to_token = self.token
        with patch.object(IconScoreBase, 'msg', Message(self.owner)):
            self.score.getReturn(from_token, to_token, amount)
            self.score.getPurchaseReturn.assert_called_with(from_token, amount)

    def test_getPurchaseReturn(self):
        amount = 1000

        self.score.getConnectorBalance = Mock(return_value=10000)

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call', return_value=10000),
            patch.object(FixedMapFormula, 'calculate_purchase_return', return_value=1000)
        ]):
            result = self.score.getPurchaseReturn(self.initial_connector_token, amount)
            self.assertEqual(1000, result['amount'])
            self.assertEqual(0, result['fee'])

        # sets the fee to 1%
        self.score._max_conversion_fee.set(1000000)
        self.score._conversion_fee.set(10000)

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call', return_value=10000),
            patch.object(FixedMapFormula, 'calculate_purchase_return', return_value=1000)
        ]):
            result = self.score.getPurchaseReturn(self.initial_connector_token, amount)
            self.assertEqual(990, result['amount'])
            self.assertEqual(10, result['fee'])

    def test_getSaleReturn(self):
        amount = 1000

        self.score.getConnectorBalance = Mock(return_value=10000)

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call', return_value=10000),
            patch.object(FixedMapFormula, 'calculate_sale_return', return_value=1000)
        ]):
            result = self.score.getSaleReturn(self.initial_connector_token, amount)
            self.assertEqual(1000, result['amount'])
            self.assertEqual(0, result['fee'])

        # sets the fee to 1%
        self.score._max_conversion_fee.set(1000000)
        self.score._conversion_fee.set(10000)

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call', return_value=10000),
            patch.object(FixedMapFormula, 'calculate_sale_return', return_value=1000)
        ]):
            result = self.score.getSaleReturn(self.initial_connector_token, amount)
            self.assertEqual(990, result['amount'])
            self.assertEqual(10, result['fee'])

    def test_getCrossConnectorReturn(self):
        connector_token2 = Address.from_string("cx" + os.urandom(20).hex())
        connector_token2_weight = 500000
        self.score.addConnector(connector_token2, connector_token2_weight, False)

        amount = 1000

        self.score.getConnectorBalance = Mock(return_value=10000)

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(FixedMapFormula, 'calculate_cross_connector_return', return_value=1000)
        ]):
            result = self.score.getCrossConnectorReturn(
                self.initial_connector_token,
                connector_token2,
                amount)
            self.assertEqual(1000, result['amount'])
            self.assertEqual(0, result['fee'])

        # sets the fee to 1%
        self.score._max_conversion_fee.set(1000000)
        self.score._conversion_fee.set(10000)

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(FixedMapFormula, 'calculate_cross_connector_return', return_value=1000)
        ]):
            result = self.score.getCrossConnectorReturn(
                self.initial_connector_token,
                connector_token2,
                amount)
            self.assertEqual(980, result['amount'])
            self.assertEqual(20, result['fee'])
