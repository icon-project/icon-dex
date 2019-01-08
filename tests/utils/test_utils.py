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
