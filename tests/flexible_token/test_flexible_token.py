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

import unittest
from unittest.mock import Mock

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message

from contracts.irc_token.irc_token import IRCToken
from contracts.flexible_token.flexible_token import FlexibleToken
from contracts.utility.token_holder import TokenHolder
from tests import patch_property, ScorePatcher, create_db


# noinspection PyUnresolvedReferences
class TestFlexibleToken(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(FlexibleToken)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.flexible_token = FlexibleToken(create_db(self.score_address))
        token_name = "test_token"
        token_symbol = "TST"
        token_supply = 100
        token_decimals = 18

        self.token_owner = Address.from_string("hx" + "2" * 40)

        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            self.flexible_token.on_install(token_name, token_symbol, token_supply, token_decimals)

            IRCToken.on_install.assert_called_with(self.flexible_token, token_name, token_symbol, token_supply, token_decimals)
            TokenHolder.on_install.assert_called_with(self.flexible_token)
            self.assertEqual(self.flexible_token._VERSION, self.flexible_token._version.get())
            self.assertEqual(True, self.flexible_token._transfer_possibility.get())
            self.flexible_token.NewFlexibleToken.assert_called_with(self.score_address)

    def tearDown(self):
        self.patcher.stop()

    def test_check_transfer_possibility(self):
        self.flexible_token._transfer_possibility.set(True)
        self.flexible_token.require_transfer_allowed()

        self.flexible_token._transfer_possibility.set(False)
        self.assertRaises(RevertException, self.flexible_token.require_transfer_allowed)

    def test_disableTransfer(self):
        self.flexible_token._transfer_possibility.set(True)
        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            self.flexible_token.require_owner_only = Mock()

            self.flexible_token.disableTransfer(True)
            self.flexible_token.require_owner_only.assert_called()
            self.assertEqual(False, self.flexible_token._transfer_possibility.get())

            self.flexible_token.disableTransfer(False)
            self.flexible_token.require_owner_only.assert_called()
            self.assertEqual(True, self.flexible_token._transfer_possibility.get())

    def test_issue(self):
        token_receiver = Address.from_string("hx" + "3" * 40)

        # success_case: issue 10 token to public
        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            before_balance = self.flexible_token._balances[token_receiver]
            before_total_supply = self.flexible_token._total_supply.get()

            self.flexible_token.issue(token_receiver, 10)
            self.flexible_token.require_owner_only.assert_called()
            self.assertEqual(before_balance + 10, self.flexible_token._balances[token_receiver])
            self.assertEqual(before_total_supply + 10, self.flexible_token._total_supply.get())

            self.flexible_token.Issuance.assert_called_with(10)
            self.flexible_token.Transfer.assert_called_with(self.score_address, token_receiver, 10, b'None')

        # failure_case: amount is under 0
        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            minus_amount = -10
            self.assertRaises(RevertException, self.flexible_token.issue, token_receiver, minus_amount)

        # failure_case: 'to' address is invalid
        to_address = ZERO_SCORE_ADDRESS
        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            self.assertRaises(RevertException, self.flexible_token.issue, to_address, 10)

    def test_destroy(self):
        token_holder = Address.from_string("hx" + "3" * 40)

        # owner setting
        self.flexible_token._owner.set(self.token_owner)

        # increase 10 token to holder's balance
        self.flexible_token._balances[token_holder] += 10
        # increase total supply according to token holder's balance
        self.flexible_token._total_supply.set(self.flexible_token._total_supply.get() + 10)

        before_balance = self.flexible_token._balances[token_holder]
        before_total_supply = self.flexible_token._total_supply.get()

        # failure case: amount is under 0
        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            self.assertRaises(RevertException, self.flexible_token.destroy, token_holder, -10)

        # failure case: amount is higher than token_holder's balance
        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            self.assertRaises(RevertException, self.flexible_token.destroy, token_holder, 20)

        # failure case: msg.sender is not 'from' nor the owner
        eoa_address = Address.from_string("hx" + "4" * 40)
        with patch_property(IconScoreBase, 'msg', Message(eoa_address)):
            self.assertRaises(RevertException, self.flexible_token.destroy, token_holder, 10)

        # success case: token_owner destroy 5 tokens from token_holder
        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            destroy_amount = 5
            self.flexible_token.destroy(token_holder, destroy_amount)

            self.assertEqual(before_balance - destroy_amount, self.flexible_token._balances[token_holder])
            self.assertEqual(before_total_supply - destroy_amount, self.flexible_token._total_supply.get())

            self.flexible_token.Destruction.assert_called_with(destroy_amount)
            self.flexible_token.Transfer.assert_called_with(token_holder, self.score_address, destroy_amount, b'None')

        # success case: token_holder destroy 5 their own token
        with patch_property(IconScoreBase, 'msg', Message(token_holder)):
            destroy_amount = 5
            before_balance = self.flexible_token._balances[token_holder]
            before_total_supply = self.flexible_token._total_supply.get()

            self.flexible_token.destroy(token_holder, destroy_amount)

            self.assertEqual(before_balance - destroy_amount, self.flexible_token._balances[token_holder])
            self.assertEqual(before_total_supply - destroy_amount, self.flexible_token._total_supply.get())

            self.flexible_token.Destruction.assert_called_with(destroy_amount)
            self.flexible_token.Transfer.assert_called_with(token_holder, self.score_address, destroy_amount, b'None')

    def test_transfer(self):
        sender = Address.from_string("hx" + "2" * 40)
        token_receiver = Address.from_string("hx" + "3" * 40)

        # failure case: transfer tokens when transfer possibility is False
        with patch_property(IconScoreBase, 'msg', Message(sender)):
            self.flexible_token._transfer_possibility.set(False)
            self.assertRaises(RevertException, self.flexible_token.transfer, token_receiver, 10)
            IRCToken.transfer.assert_not_called()

        # success case: transfer tokens when transfer possibility is True
        self.flexible_token._transfer_possibility.set(True)

        self.flexible_token.transfer(token_receiver, 10)
        IRCToken.transfer.assert_called_with(self.flexible_token, token_receiver, 10, None)
