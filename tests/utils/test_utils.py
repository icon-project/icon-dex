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

from contracts.utility.utils import Utils


class TestUtils(unittest.TestCase):
    def test_check_positive_value(self):
        self.assertRaises(RevertException, Utils.check_positive_value, -1)
        self.assertRaises(RevertException, Utils.check_positive_value, 0)
        Utils.check_positive_value(0.1)
        Utils.check_positive_value(10)

    def test_check_valid_address(self):
        self.assertRaises(RevertException, Utils.check_valid_address, ZERO_SCORE_ADDRESS)

        valid_eoa_address = Address.from_string("hx" + "1" * 40)
        valid_score_address = Address.from_string("cx" + "1" * 40)
        Utils.check_valid_address(valid_eoa_address)
        Utils.check_valid_address(valid_score_address)

    def test_check_not_this(self):
        score_address = Address.from_string("cx" + "1" * 40)
        eoa_address = Address.from_string("hx" + "1" * 40)

        self.assertRaises(RevertException, Utils.check_not_this, score_address, score_address)
        Utils.check_not_this(score_address, eoa_address)

    def test_safe_sub(self):
        # verifies successful subtraction
        x = 2957
        y = 1740
        z = Utils.safe_sub(x, y)
        self.assertEqual(z, x-y)

        # should throw on subtraction with negative result
        x = 10
        y = 11
        self.assertRaises(RevertException, Utils.safe_sub, x, y)
