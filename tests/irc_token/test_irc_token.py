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
from unittest.mock import patch

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message

from contracts.irc_token.irc_token import IRCToken, TokenFallbackInterface
from tests import ScorePatcher, create_db, MultiPatch, patch_property


# noinspection PyUnresolvedReferences
class TestIRCToken(unittest.TestCase):
    def setUp(self):
        self.patcher = ScorePatcher(IRCToken)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.irc_token = IRCToken(create_db(self.score_address))
        token_name = "test_token"
        token_symbol = "TST"
        token_supply = 100
        token_decimals = 18

        self.token_owner = Address.from_string("hx" + "2" * 40)

        # failure case: total supply is under 0
        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            invalid_token_supply = - 1
            self.assertRaises(RevertException,
                              self.irc_token.on_install,
                              token_name,
                              token_symbol,
                              invalid_token_supply,
                              token_decimals)

        # failure case: decimal is under 0
        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            invalid_token_decimals = - 1
            self.assertRaises(RevertException,
                              self.irc_token.on_install,
                              token_name,
                              token_symbol,
                              token_supply,
                              invalid_token_decimals)

        # success case: deploy IRCToken with valid parameters
        with patch_property(IconScoreBase, 'msg', Message(self.token_owner)):
            self.irc_token.on_install(token_name, token_symbol, token_supply, token_decimals)
            self.assertEqual(token_name, self.irc_token._name.get())
            self.assertEqual(token_symbol, self.irc_token._symbol.get())
            self.assertEqual(token_decimals, self.irc_token._decimals.get())
            self.assertEqual(token_supply * 10 ** token_decimals, self.irc_token._total_supply.get())
            self.assertEqual(token_supply * 10 ** token_decimals, self.irc_token._balances[self.token_owner])

    def tearDown(self):
        self.patcher.stop()

    def test_external_transfer(self):
        token_receiver = Address.from_string("hx" + "3" * 40)
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.token_owner)),
            patch.object(IRCToken, '_transfer')
        ]):
            self.irc_token.transfer(token_receiver, 10)
            IRCToken._transfer.assert_called_with(self.token_owner, token_receiver, 10, b'None')

            self.irc_token.transfer(token_receiver, 10, b'test')
            IRCToken._transfer.assert_called_with(self.token_owner, token_receiver, 10, b'test')

    def test_transfer(self):
        eoa_token_receiver = Address.from_string("hx" + "3" * 40)
        score_token_receiver = Address.from_string("cx" + "3" * 40)

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.token_owner)),
            patch.object(TokenFallbackInterface, 'tokenFallback')
        ]):
            # failure case: value is under 0
            invalid_value = -1
            self.assertRaises(RevertException,
                              self.irc_token._transfer,
                              self.token_owner, eoa_token_receiver, invalid_value, b'None')

            # failure case: value is higher than senders' total balance
            value = self.irc_token._balances[self.token_owner] + 1
            self.assertRaises(RevertException,
                              self.irc_token._transfer,
                              self.token_owner, eoa_token_receiver, value, b'None')

        # success cass: transfer 10 token to token_receiver (EOA)
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.token_owner)),
            patch.object(TokenFallbackInterface, 'tokenFallback')
        ]):
            value = 10
            before_owner_balance = self.irc_token._balances[self.token_owner]
            before_eoa_receiver_balance = self.irc_token._balances[eoa_token_receiver]
            self.irc_token._transfer(self.token_owner, eoa_token_receiver, value, b'None')
            self.assertEqual(before_owner_balance - value, self.irc_token._balances[self.token_owner])
            self.assertEqual(before_eoa_receiver_balance + value, self.irc_token._balances[eoa_token_receiver])
            TokenFallbackInterface.tokenFallback.assert_not_called()

            self.irc_token.Transfer.assert_called_with(self.token_owner, eoa_token_receiver, value, b'None')

        # success cass: transfer 10 token to token_receiver (SCORE)
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.token_owner)),
            patch.object(TokenFallbackInterface, 'tokenFallback')
        ]):
            value = 10
            before_owner_balance = self.irc_token._balances[self.token_owner]
            before_score_receiver_balance = self.irc_token._balances[score_token_receiver]
            self.irc_token._transfer(self.token_owner, score_token_receiver, value, b'None')
            self.assertEqual(before_owner_balance - value, self.irc_token._balances[self.token_owner])
            self.assertEqual(before_score_receiver_balance + value, self.irc_token._balances[score_token_receiver])
            TokenFallbackInterface.tokenFallback.assert_called_with(self.token_owner, value, b'None')

            self.irc_token.Transfer.assert_called_with(self.token_owner, score_token_receiver, value, b'None')
