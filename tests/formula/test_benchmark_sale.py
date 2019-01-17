# -*- coding: utf-8 -*-
# Copyright 2017-2018 ICON Foundation
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

from contracts.formula import formula
from tests.formula import formula_native_python
from tests.formula import TEST_SIZE, WORST_ACCURACY


class TestBenchmarkSale(unittest.TestCase):

    @staticmethod
    def _formula_test(supply, balance, weight, amount):
        result_formula = formula.calculateSaleReturn(supply, balance, weight, amount)
        result_formula_native_python = formula_native_python.calculateSaleReturn(supply, balance, weight, amount)
        if result_formula > result_formula_native_python:
            error = ['Implementation Error:']
            error.append('supply             = {}'.format(supply))
            error.append('balance            = {}'.format(balance))
            error.append('weight             = {}'.format(weight))
            error.append('amount             = {}'.format(amount))
            error.append('result_formula = {}'.format(result_formula))
            error.append('result_formula_native_python = {}'.format(result_formula_native_python))
            raise BaseException('\n'.join(error))
        return result_formula / result_formula_native_python

    def test_benchmark_sale(self):
        bgn = 10 ** 17
        end = 10 ** 26
        gap = (end - bgn) // TEST_SIZE

        worst_accuracy = 1
        num_of_failures = 0

        for n in range(TEST_SIZE):
            supply = 10 ** 26
            balance = 10 ** 23
            weight = 100000
            amount = bgn + gap * n
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
            print('Test #{}: amount = {:26d}, accuracy = {:.12f}, worst accuracy = {:.12f}, num of failures = {}'.format(n, amount, accuracy, worst_accuracy, num_of_failures))

        if num_of_failures > 0:
            self.fail("TEST FAILED: num of failures is {} of {}".format(num_of_failures, TEST_SIZE))


