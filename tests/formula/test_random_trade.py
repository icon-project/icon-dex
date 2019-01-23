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

# original source
# https://github.com/bancorprotocol/contracts

import unittest
import random
from decimal import Decimal, getcontext

from contracts.formula import formula
from tests.formula import TEST_SIZE, WORST_ACCURACY

getcontext().prec = 80 # 78 digits for a maximum of 2^256-1, and 2 more digits for after the decimal point


class TestRandomTrade(unittest.TestCase):

    @staticmethod
    def _formula_test(supply, balance, weight, amount):
        new_amount = formula.calculate_purchase_return(supply, balance, weight, amount)
        old_amount = formula.calculate_sale_return(supply + new_amount, balance + amount, weight, new_amount)
        if old_amount > amount:
            error = ['Implementation Error:']
            error.append('supply    = {}'.format(supply))
            error.append('balance   = {}'.format(balance))
            error.append('weight    = {}'.format(weight))
            error.append('amount    = {}'.format(amount))
            error.append('new_amount = {}'.format(new_amount))
            error.append('old_amount = {}'.format(old_amount))
            raise BaseException('\n'.join(error))
        return Decimal(old_amount) / Decimal(amount)

    def test_random_trade(self):
        worst_accuracy = 1
        num_of_failures = 0
        for n in range(TEST_SIZE):
            supply = random.randrange(2, 10 ** 26)
            balance = random.randrange(1, 10 ** 23)
            weight = random.randrange(1, 1000000)
            amount = random.randrange(1, supply)
            try:
                accuracy = self._formula_test(supply, balance, weight, amount)
                worst_accuracy = min(worst_accuracy, accuracy)
                if worst_accuracy < WORST_ACCURACY:
                    raise BaseException("worst accuracy is  {} less than {}".format(worst_accuracy, WORST_ACCURACY))
            except Exception as error:
                print("TEST FAILED:", error)
                accuracy = 0
                num_of_failures += 1
            except BaseException as error:
                self.fail("TEST FAILED: {}".format(error))
            print('Test #{}: accuracy = {:.12f}, worst accuracy = {:.12f}, num of failures = {}'.format(n, accuracy, worst_accuracy, num_of_failures))

        if num_of_failures > 0:
            self.fail("TEST FAILED: num of failures is {} of {}".format(num_of_failures, TEST_SIZE))

