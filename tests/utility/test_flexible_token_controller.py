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

from iconservice.base.message import Message
from iconservice.iconscore.internal_call import InternalCall

from contracts.icx_token.icx_token import IcxToken
from contracts.utility.flexible_token_controller import FlexibleTokenController
from contracts.utility.token_holder import TokenHolder
from contracts.utility.utils import *
from tests import MultiPatch, patch_property, ScorePatcher, create_db, assert_inter_call


# noinspection PyUnresolvedReferences
class TestFlexibleTokenController(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(IcxToken)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.flexible_token_address = Address.from_string("cx" + "2" * 40)
        self.score = FlexibleTokenController(create_db(self.score_address))

        self.owner = Address.from_string("hx" + "2" * 40)
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch('contracts.utility.flexible_token_controller.require_valid_address')
        ]) as mocks:
            self.score.on_install(self.flexible_token_address)
            TokenHolder.on_install.assert_called_with(self.score)
            mocks[1].assert_called()

    def tearDown(self):
        self.patcher.stop()

    def test_transferTokenOwnership(self):
        new_owner = Address.from_string("hx" + "3" * 40)

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call'),
        ]):
            self.score.transferTokenOwnership(new_owner)
            self.score.require_owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score._token.get(),
                'transferOwnerShip',
                [new_owner])

    def test_acceptTokenOwnership(self):
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call'),
        ]):
            self.score.acceptTokenOwnership()
            self.score.require_owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score._token.get(),
                'acceptOwnerShip',
                []
            )

    def test_disableTokenTransfers(self):
        disable = True
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call'),
        ]):
            self.score.disableTokenTransfers(disable)
            self.score.require_owner_only.assert_called()

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
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call'),
        ]):
            self.score.withdrawFromToken(token, to, amount)
            self.score.require_owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score._token.get(),
                'withdrawTokens',
                [token, to, amount]
            )

    def test_isActive(self):
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call'),
        ]) as mocks:
            mocks[1].return_value = self.score.address
            is_active = self.score.isActive()

            self.assertEqual(True, is_active)

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.owner)),
            patch.object(InternalCall, 'other_external_call'),
        ]) as mocks:
            mocks[1].return_value = ZERO_SCORE_ADDRESS
            is_active = self.score.isActive()

            self.assertEqual(False, is_active)

    def test_getToken(self):
        with patch.object(IconScoreBase, 'msg', Message(self.owner)):
            token = self.score.getToken()

            self.assertEqual(self.score._token.get(), token)
