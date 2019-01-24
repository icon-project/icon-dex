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
from typing import TYPE_CHECKING

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message

from contracts.score_registry.score_registry import ScoreRegistry
from contracts.utility.owned import Owned
from tests import patch_property, ScorePatcher, create_db

if TYPE_CHECKING:
    from iconservice.base.address import Address


# noinspection PyUnresolvedReferences
class TestScoreRegistry(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(ScoreRegistry)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.registry_score = ScoreRegistry(create_db(self.score_address))

        self.registry_owner = Address.from_string("hx" + "1" * 40)
        with patch_property(IconScoreBase, 'msg', Message(self.registry_owner)):
            self.registry_score.on_install()
            Owned.on_install.assert_called_with(self.registry_score)

            # success case: when deploy ScoreRegistry, score registry address should be registered by default
            self.assertEqual \
                (self.score_address,
                 self.registry_score._score_address[self.registry_score.SCORE_REGISTRY.encode()])

    def tearDown(self):
        self.patcher.stop()

    def test_getAddress(self):
        # success case: search the registered score address
        registered_score_name = self.registry_score.SCORE_REGISTRY
        actual_registered_address = self.registry_score.getAddress(registered_score_name)
        self.assertEqual(self.score_address, actual_registered_address)

        # success case: search the score address which has not been registered (should return zero score address)
        unregistered_score_name = self.registry_score.BANCOR_NETWORK
        actual_registered_address = self.registry_score.getAddress(unregistered_score_name)
        self.assertEqual(ZERO_SCORE_ADDRESS, actual_registered_address)

    def test_registerAddress(self):
        eoa_address = Address.from_string("hx" + "3" * 40)
        bancor_network_id = self.registry_score.BANCOR_NETWORK
        bancor_network_address = Address.from_string("cx" + "2" * 40)

        with patch_property(IconScoreBase, 'msg', Message(self.registry_owner)):
            # failure case: invalid register score address
            self.assertRaises(RevertException,
                              self.registry_score.registerAddress,
                              bancor_network_id, ZERO_SCORE_ADDRESS)

            # failure case: try to register eoa address
            self.assertRaises(RevertException,
                              self.registry_score.registerAddress,
                              bancor_network_id, eoa_address)

            # failure case: score name is not in the SCORE_KEYS
            non_listed_id = "NON_LISTED_SCORE_ID"
            self.assertRaises(RevertException,
                              self.registry_score.registerAddress,
                              non_listed_id, bancor_network_address)

            # success case: register bancor network
            self.registry_score.registerAddress(bancor_network_id, bancor_network_address)
            self.assertEqual(bancor_network_address,
                             self.registry_score._score_address[bancor_network_id])
            self.registry_score.AddressUpdate.assert_called_with(bancor_network_id, bancor_network_address)

    def test_unregisterAddress(self):
        bancor_network_id = self.registry_score.BANCOR_NETWORK
        bancor_network_address = Address.from_string("cx" + "2" * 40)

        # register bancor network
        self.registry_score._score_address[bancor_network_id] = bancor_network_address

        with patch_property(IconScoreBase, 'msg', Message(self.registry_owner)):
            # failure case: try to unregister not recorded score address
            non_registered_id = self.registry_score.BANCOR_FORMULA
            self.assertRaises(RevertException,
                              self.registry_score.unregisterAddress,
                              non_registered_id)

            # success case: unregister score address which has been registered
            self.registry_score.unregisterAddress(bancor_network_id)
            self.assertEqual(None, self.registry_score._score_address[bancor_network_id])

            self.registry_score.AddressUpdate.assert_called_with(bancor_network_id, ZERO_SCORE_ADDRESS)
