import unittest
import random
from decimal import Decimal, getcontext

from contracts.formula import formula
from tests.formula import formula_native_python
from tests.formula import TEST_SIZE, WORST_ACCURACY

getcontext().prec = 80  # 78 digits for a maximum of 2^256-1, and 2 more digits for after the decimal point


class TestRandomCrossConnector(unittest.TestCase):

    @staticmethod
    def _singleHopTestFixed(balance1, weight1, balance2, weight2, amount):
        try:
            return formula.calculateCrossConnectorReturn(balance1, weight1, balance2, weight2, amount)
        except:
            return -1

    @staticmethod
    def _doubleHopTestFixed(supply, balance1, weight1, balance2, weight2, amount):
        try:
            amount = formula.calculatePurchaseReturn(supply, balance1, weight1, amount)
            return formula.calculateSaleReturn(supply + amount, balance2, weight2, amount)
        except:
            return -1

    @staticmethod
    def _doubleHopTestFloat(supply, balance1, weight1, balance2, weight2, amount):
        try:
            amount = formula_native_python.calculatePurchaseReturn(supply, balance1, weight1, amount)
            return formula_native_python.calculateSaleReturn(supply + amount, balance2, weight2, amount)
        except:
            return -1

    def test_random_cross_connector(self):
        min_ratio = Decimal('+inf')

        for n in range(TEST_SIZE):
            supply = random.randrange(2, 10 ** 26)
            balance1 = random.randrange(1, 10 ** 23)
            weight1 = random.randrange(1, 1000000)
            balance2 = random.randrange(1, 10 ** 23)
            weight2 = random.randrange(1, 1000000)
            amount = random.randrange(1, supply)
            single_hop_fixed = self._singleHopTestFixed(balance1, weight1, balance2, weight2, amount)
            double_hop_fixed = self._doubleHopTestFixed(supply, balance1, weight1, balance2, weight2, amount)
            double_hop_float = self._doubleHopTestFloat(supply, balance1, weight1, balance2, weight2, amount)
            if 0 <= double_hop_fixed <= single_hop_fixed <= double_hop_float:
                ratio = Decimal(single_hop_fixed) / Decimal(double_hop_float)
                min_ratio = min(min_ratio, ratio)
                print('Test #{}: ratio = {:.24f}, min_ratio = {:.24f}'.format(n, ratio, min_ratio))
            elif single_hop_fixed < 0 and double_hop_fixed < 0:
                ratio = Decimal(0)
                print('Test #{}: ratio = {:.24f}, min_ratio = {:.24f}'.format(n, ratio, min_ratio))
            else:
                error = ['Implementation Error:']
                error.append('supply         = {}'.format(supply))
                error.append('balance1       = {}'.format(balance1))
                error.append('weight1        = {}'.format(weight1))
                error.append('balance2       = {}'.format(balance2))
                error.append('weight2        = {}'.format(weight2))
                error.append('amount         = {}'.format(amount))
                error.append('single_hop_fixed = {}'.format(single_hop_fixed))
                error.append('double_hop_fixed = {}'.format(double_hop_fixed))
                error.append('double_hop_float = {}'.format(double_hop_float))
                self.fail("TEST FAILED: {}".format(error))

            if min_ratio < WORST_ACCURACY:
                self.fail("min ratio is  {} less than {}".format(min_ratio, WORST_ACCURACY))


