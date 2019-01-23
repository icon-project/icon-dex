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

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message

from contracts.icx_token.icx_token import IcxToken
from contracts.irc_token.irc_token import IRCToken
from contracts.utility.token_holder import TokenHolder
from tests import patch, ScorePatcher, create_db


# noinspection PyUnresolvedReferences
class TestIcxToken(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(IcxToken)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.icx_token = IcxToken(create_db(self.score_address))

        self.token_owner = Address.from_string("hx" + "2" * 40)
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            self.icx_token.on_install()
            IRCToken.on_install.assert_called_with(self.icx_token, 'icx_token', 'ICX', 0, 18)
            TokenHolder.on_install.assert_called_with(self.icx_token)

    def tearDown(self):
        self.patcher.stop()

    def test_deposit(self):
        value = 10

        with patch([(IconScoreBase, 'msg', Message(self.token_owner, value=value))]):
            before_balance = self.icx_token._balances[self.token_owner]
            before_total_supply = self.icx_token._total_supply.get()

            self.icx_token.deposit()
            self.assertEqual(value, self.icx_token._balances[self.token_owner] - before_balance)
            self.assertEqual(value, self.icx_token._total_supply.get() - before_total_supply)

            self.icx_token.Issuance.assert_called_with(value)
            self.icx_token.Transfer.assert_called_with(self.icx_token.address, self.token_owner, value, b'None')

    def test_withdrawTo(self):
        to = Address.from_string("hx" + "3" * 40)

        self.icx_token._balances[self.token_owner] = 10
        self.icx_token._total_supply.set(10)

        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            # failure case: amount is under 0
            self.assertRaises(RevertException, self.icx_token.withdrawTo, -1, to)

            # failure case: amount is higher than token holders' total balance
            self.assertRaises(RevertException, self.icx_token.withdrawTo, 20, to)

            # success case: withdraw 10 token to 'to'
            self.icx_token.withdrawTo(10, to)
            self.icx_token.icx.transfer.assert_called_with(to, 10)

            self.assertEqual(0, self.icx_token._balances[self.token_owner])
            self.assertEqual(0, self.icx_token._total_supply.get())
            self.icx_token.Destruction.assert_called_with(10)

    def test_transfer(self):
        # failure case: transfer token to this score (should raise error)
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            self.assertRaises(RevertException, self.icx_token.transfer, self.score_address, 10)
            IRCToken.transfer.assert_not_called()

        # success case: send 10 token to other
        token_receiver = Address.from_string("hx" + "4" * 40)
        self.icx_token.transfer(token_receiver, 10)

        IRCToken.transfer.assert_called_with(self.icx_token, token_receiver, 10, None)

