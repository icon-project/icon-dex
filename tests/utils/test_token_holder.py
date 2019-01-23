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
from unittest.mock import PropertyMock

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message

from contracts.interfaces.abc_irc_token import ABCIRCToken
from contracts.utility.owned import Owned
from contracts.utility.proxy_score import ProxyScore
from contracts.utility.token_holder import TokenHolder
from tests import patch, ScorePatcher, create_db


class TestTokenHolder(unittest.TestCase):
    def setUp(self):
        self.patcher = ScorePatcher(TokenHolder)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.token_holder = TokenHolder(create_db(self.score_address))

        self.token_owner = Address.from_string("hx" + "2" * 40)
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            self.token_holder.on_install()
            Owned.on_install.assert_called_with(self.token_holder)

    def tearDown(self):
        self.patcher.stop()

    def test_withdrawTokens(self):
        token_address = Address.from_string("cx" + "2" * 40)
        token_receiver = Address.from_string("hx" + "3" * 40)
        irc_token_score_interface = \
            self.token_holder.create_interface_score(token_address, ProxyScore(ABCIRCToken))
        irc_token_score_interface.transfer = PropertyMock()

        with patch([(IconScoreBase, 'msg', Message(self.token_owner)),
                    (TokenHolder, 'create_interface_score', irc_token_score_interface)]):
            amount = 10
            # success case: withdraw 10 token
            self.token_holder.withdrawTokens(token_address, token_receiver, amount)
            self.token_holder.create_interface_score.assert_called_with(token_address, ProxyScore(ABCIRCToken))
            irc_token_score_interface.transfer.assert_called_with(token_receiver, amount)
            self.token_holder.create_interface_score.reset_mock()
            irc_token_score_interface.transfer.reset_mock()

            # failure case: amount is under 0
            invalid_amount = -1
            self.assertRaises(RevertException,
                              self.token_holder.withdrawTokens,
                              token_address, token_receiver, invalid_amount)
            self.token_holder.create_interface_score.assert_not_called()
            irc_token_score_interface.transfer.assert_not_called()
            self.token_holder.create_interface_score.reset_mock()
            irc_token_score_interface.transfer.reset_mock()

            # failure case: 'to' address is this
            self.assertRaises(RevertException,
                              self.token_holder.withdrawTokens,
                              token_address, self.score_address, amount)
            self.token_holder.create_interface_score.assert_not_called()
            irc_token_score_interface.transfer.assert_not_called()
            self.token_holder.create_interface_score.reset_mock()
            irc_token_score_interface.transfer.reset_mock()

            # failure case: 'to' address is invalid address
            self.assertRaises(RevertException,
                              self.token_holder.withdrawTokens,
                              token_address, ZERO_SCORE_ADDRESS, amount)
            self.token_holder.create_interface_score.assert_not_called()
            irc_token_score_interface.transfer.assert_not_called()
            self.token_holder.create_interface_score.reset_mock()
            irc_token_score_interface.transfer.reset_mock()
