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
from iconservice.base.message import Message
from iconservice.iconscore.internal_call import InternalCall

from contracts.icx_token.icx_token import IcxToken
from contracts.utility.smart_token_controller import SmartTokenController
from contracts.utility.token_holder import TokenHolder
from contracts.utility.utils import Utils
from tests import patch, ScorePatcher, create_db, assert_inter_call


# noinspection PyUnresolvedReferences
class TestSmartTokenController(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(IcxToken)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.smart_token_address = Address.from_string("cx" + "2" * 40)
        self.score = SmartTokenController(create_db(self.score_address))

        self.owner = Address.from_string("hx" + "2" * 40)
        with patch([
            (IconScoreBase, 'msg', Message(self.owner)),
            (Utils, 'check_valid_address', None),
        ]):
            self.score.on_install(self.smart_token_address)
            TokenHolder.on_install.assert_called_with(self.score)
            Utils.check_valid_address.assert_called_with(self.smart_token_address)

    def tearDown(self):
        self.patcher.stop()

    def test_transferTokenOwnership(self):
        new_owner = Address.from_string("hx" + "3" * 40)

        with patch([
            (IconScoreBase, 'msg', Message(self.owner)),
            (InternalCall, 'other_external_call', None),
        ]):
            self.score.transferTokenOwnership(new_owner)
            self.score.owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score._token.get(),
                'transferOwnerShip',
                [new_owner])

    def test_acceptTokenOwnership(self):
        with patch([
            (IconScoreBase, 'msg', Message(self.owner)),
            (InternalCall, 'other_external_call', None),
        ]):
            self.score.acceptTokenOwnership()
            self.score.owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score._token.get(),
                'acceptOwnerShip',
                []
            )

    def test_disableTokenTransfers(self):
        disable = True
        with patch([
            (IconScoreBase, 'msg', Message(self.owner)),
            (InternalCall, 'other_external_call', None),
        ]):
            self.score.disableTokenTransfers(disable)
            self.score.owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score._token.get(),
                'disableTransfer',
                [disable]
            )

    def test_withdrawFromToken(self):
        token = Address.from_string("cx" + "3" * 40)
        to = Address.from_string("hx" + "3" * 40)
        amount = 100
        with patch([
            (IconScoreBase, 'msg', Message(self.owner)),
            (InternalCall, 'other_external_call', None),
        ]):
            self.score.withdrawFromToken(token, to, amount)
            self.score.owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score._token.get(),
                'withdrawTokens',
                [token, to, amount]
            )
