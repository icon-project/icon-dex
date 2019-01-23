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
from unittest.mock import Mock, patch

from iconservice import ABC, abstractmethod, Address, IconScoreBase
from iconservice.iconscore.internal_call import InternalCall

from contracts.utility.proxy_score import ProxyScore
from tests import assert_inter_call


class ABCToken1(ABC):

    @abstractmethod
    def transfer(self, _to: 'Address', _value: int, _data: bytes = None):
        pass


class ABCToken2(ABC):

    @abstractmethod
    def transfer(self, _to: 'Address', _value: int, _data: bytes = None):
        pass


class ABCToken3(ABCToken1):

    @abstractmethod
    def transfer_from(self, _from: Address, _to: 'Address', _value: int, _data: bytes = None):
        pass


ScoreInterface = ProxyScore(ABCToken1)


class TestProxyScore(unittest.TestCase):

    def test_proxy_creation(self):
        # tests the attributes are properly imported
        self.assertTrue(hasattr(ScoreInterface, 'transfer'))

        # tests the proxy class cache
        ScoreInterface0 = ProxyScore(ABCToken1)
        ScoreInterface1 = ProxyScore(ABCToken1)
        ScoreInterface2 = ProxyScore(ABCToken2)

        # If the ABC class names are same each other, the proxy class will be created once.
        self.assertEqual(ScoreInterface0, ScoreInterface1)
        # otherwise creates new one
        self.assertNotEqual(ScoreInterface0, ScoreInterface2)

    def test_proxy_creation_with_inheritance(self):
        InheritedScoreInterface = ProxyScore(ABCToken3)

        # asserts own function exists
        self.assertTrue(hasattr(InheritedScoreInterface, 'transfer_from'))

        # asserts parent function exists
        self.assertTrue(hasattr(InheritedScoreInterface, 'transfer'))

    def test_proxy_call(self):
        # tests the proxy call

        self_address = Mock(Address)
        score_address = Mock(Address)
        to_address = Mock(Address)

        value = 1

        icon_score_base = Mock(IconScoreBase)
        icon_score_base.address = self_address

        score = ScoreInterface(score_address, icon_score_base)

        with patch.object(InternalCall, 'other_external_call'):
            score.transfer(to_address, value)

            assert_inter_call(
                self,
                self_address,
                score_address,
                'transfer',
                [to_address, 1])
