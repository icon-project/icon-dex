import unittest
import random

from contracts.formula import formula
from tests.formula import formula_native_python
from tests.formula import TEST_SIZE, WORST_ACCURACY


class TestRandomPurchase(unittest.TestCase):

    @staticmethod
    def _formulaTest(supply, balance, weight, amount):
        result_formula = formula.calculate_purchase_return(supply, balance, weight, amount)
        result_native_python = formula_native_python.calculate_purchase_return(supply, balance, weight, amount)
        if result_formula > result_native_python:
            error = ['Implementation Error:']
            error.append('supply             = {}'.format(supply))
            error.append('balance            = {}'.format(balance))
            error.append('weight             = {}'.format(weight))
            error.append('amount             = {}'.format(amount))
            error.append('result_formula = {}'.format(result_formula))
            error.append('resultNativePython = {}'.format(result_native_python))
            raise BaseException('\n'.join(error))
        return result_formula / result_native_python

    def test_random_purchase(self):
        worst_accuracy = 1
        num_of_failures = 0

        for n in range(TEST_SIZE):
            supply = random.randrange(2, 10 ** 26)
            balance = random.randrange(1, 10 ** 23)
            weight = random.randrange(1, 1000000)
            amount = random.randrange(1, supply)
            try:
                accuracy = self._formulaTest(supply, balance, weight, amount)
                worst_accuracy = min(worst_accuracy, accuracy)
                if worst_accuracy < WORST_ACCURACY:
                    raise BaseException("worst accuracy is  {} less than {}".format(worst_accuracy, WORST_ACCURACY))
            except Exception as error:
                print("TEST FAILED:", error)
                accuracy = 0
                num_of_failures += 1
            except BaseException as error:
                self.fail("TEST FAILED: {}".format(error))
            print('Test #{}: accuracy = {:.12f}, worst accuracy = {:.12f}, num of failures = {}'.format(n, accuracy,
                                                                                                        worst_accuracy,
                                                                                                        num_of_failures))
        if num_of_failures > 0:
            self.fail("TEST FAILED: num of failures is {} of {}".format(num_of_failures, TEST_SIZE))
