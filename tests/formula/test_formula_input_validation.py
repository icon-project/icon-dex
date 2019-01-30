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

from iconservice import *
from iconservice.base.exception import RevertException

from contracts.formula import formula


class TestFormulaInputValidation(unittest.TestCase):

    def test_input_validation_for_calculate_purchase_return(self):
        # checks if supply should be more than 0 (supply > 0)
        self.assertRaises(RevertException, formula.calculate_purchase_return, 0, 10, 10, 10)
        # checks if connector balance should be more than 0
        self.assertRaises(RevertException, formula.calculate_purchase_return, 10, 0, 10, 10)
        # checks if connector weight should be more than 0
        self.assertRaises(RevertException, formula.calculate_purchase_return, 10, 10, 0, 10)
        # checks if connector weight <= MAX WEIGHT
        self.assertRaises(RevertException, formula.calculate_purchase_return, 10, 10, formula._MAX_WEIGHT + 1, 10)

    def test_input_validation_for_calculate_sale_return(self):
        # checks if supply should be more than 0
        self.assertRaises(RevertException, formula.calculate_sale_return, 0, 10, 10, 10)
        # checks if connector balance should be more than 0
        self.assertRaises(RevertException, formula.calculate_sale_return, 10, 0, 10, 10)
        # checks if connector weight should be more than 0
        self.assertRaises(RevertException, formula.calculate_sale_return, 10, 10, 0, 10)
        # checks if connector weight <= MAX WEIGHT
        self.assertRaises(RevertException, formula.calculate_sale_return, 10, 10, formula._MAX_WEIGHT + 1, 10)
        # checks if sell amount <= supply
        self.assertRaises(RevertException, formula.calculate_sale_return, 10, 10, 10, 10 + 1)

    def test_input_validation_for_calculate_cross_connector_return(self):
        # checks if from connector balance should be more than 0
        self.assertRaises(RevertException, formula.calculate_cross_connector_return, 0, 10, 10, 10, 10)
        # checks if from connector weight should be more than 0
        self.assertRaises(RevertException, formula.calculate_cross_connector_return, 10, 0, 10, 10, 10)
        # checks if from connector weight <= MAX WEIGHT
        self.assertRaises(RevertException, formula.calculate_cross_connector_return, 10, formula._MAX_WEIGHT + 1, 10, 10, 10)

        # checks if to connector balance should be more than 0
        self.assertRaises(RevertException, formula.calculate_cross_connector_return, 10, 10, 0, 10, 10)
        # checks if to connector weight should be more than 0
        self.assertRaises(RevertException, formula.calculate_cross_connector_return, 10, 10, 10, 0, 10)
        # checks if to connector weight <= MAX WEIGHT
        self.assertRaises(RevertException, formula.calculate_cross_connector_return, 10, 10, 10, formula._MAX_WEIGHT + 1, 10)



