from iconservice import *

from ..interfaces.abc_formula import ABCFormula


TAG = 'Formula'


class Formula(IconScoreBase, ABCFormula):

    _VERSION = '0.3'
    _ONE = 1
    _MAX_WEIGHT = 1000000
    _MIN_PRECISION = 32
    _MAX_PRECISION = 127

    # Auto-generated via 'print_int_scaling_factors'
    _FIXED_1 = 0x080000000000000000000000000000000
    _FIXED_2 = 0x100000000000000000000000000000000
    _MAX_NUM = 0x200000000000000000000000000000000

    # Auto-generated via 'print_ln2_scaling_factors'
    _LN2_NUMERATOR = 0x3f80fe03f80fe03f80fe03f80fe03f8
    _LN2_DENOMINATOR = 0x5b9de1d10bf4103d647b0955897ba80

    # Auto-generated via 'print_function_optimal_log' and 'print_function_optimal_exp'
    _OPT_LOG_MAX_VAL = 0x15bf0a8b1457695355fb8ac404e7a79e3
    _OPT_EXP_MAX_VAL = 0x800000000000000000000000000000000

    # Auto-generated via 'print_function_constructor'
    _max_exp_array = [None] * 128
    # _max_exp_array[0] = 0x6bffffffffffffffffffffffffffffffff
    # _max_exp_array[1] = 0x67ffffffffffffffffffffffffffffffff
    # _max_exp_array[2] = 0x637fffffffffffffffffffffffffffffff
    # _max_exp_array[3] = 0x5f6fffffffffffffffffffffffffffffff
    # _max_exp_array[4] = 0x5b77ffffffffffffffffffffffffffffff
    # _max_exp_array[5] = 0x57b3ffffffffffffffffffffffffffffff
    # _max_exp_array[6] = 0x5419ffffffffffffffffffffffffffffff
    # _max_exp_array[7] = 0x50a2ffffffffffffffffffffffffffffff
    # _max_exp_array[8] = 0x4d517fffffffffffffffffffffffffffff
    # _max_exp_array[9] = 0x4a233fffffffffffffffffffffffffffff
    # _max_exp_array[10] = 0x47165fffffffffffffffffffffffffffff
    # _max_exp_array[11] = 0x4429afffffffffffffffffffffffffffff
    # _max_exp_array[12] = 0x415bc7ffffffffffffffffffffffffffff
    # _max_exp_array[13] = 0x3eab73ffffffffffffffffffffffffffff
    # _max_exp_array[14] = 0x3c1771ffffffffffffffffffffffffffff
    # _max_exp_array[15] = 0x399e96ffffffffffffffffffffffffffff
    # _max_exp_array[16] = 0x373fc47fffffffffffffffffffffffffff
    # _max_exp_array[17] = 0x34f9e8ffffffffffffffffffffffffffff
    # _max_exp_array[18] = 0x32cbfd5fffffffffffffffffffffffffff
    # _max_exp_array[19] = 0x30b5057fffffffffffffffffffffffffff
    # _max_exp_array[20] = 0x2eb40f9fffffffffffffffffffffffffff
    # _max_exp_array[21] = 0x2cc8340fffffffffffffffffffffffffff
    # _max_exp_array[22] = 0x2af09481ffffffffffffffffffffffffff
    # _max_exp_array[23] = 0x292c5bddffffffffffffffffffffffffff
    # _max_exp_array[24] = 0x277abdcdffffffffffffffffffffffffff
    # _max_exp_array[25] = 0x25daf6657fffffffffffffffffffffffff
    # _max_exp_array[26] = 0x244c49c65fffffffffffffffffffffffff
    # _max_exp_array[27] = 0x22ce03cd5fffffffffffffffffffffffff
    # _max_exp_array[28] = 0x215f77c047ffffffffffffffffffffffff
    # _max_exp_array[29] = 0x1fffffffffffffffffffffffffffffffff
    # _max_exp_array[30] = 0x1eaefdbdabffffffffffffffffffffffff
    # _max_exp_array[31] = 0x1d6bd8b2ebffffffffffffffffffffffff
    _max_exp_array[32] = 0x1c35fedd14ffffffffffffffffffffffff
    _max_exp_array[33] = 0x1b0ce43b323fffffffffffffffffffffff
    _max_exp_array[34] = 0x19f0028ec1ffffffffffffffffffffffff
    _max_exp_array[35] = 0x18ded91f0e7fffffffffffffffffffffff
    _max_exp_array[36] = 0x17d8ec7f0417ffffffffffffffffffffff
    _max_exp_array[37] = 0x16ddc6556cdbffffffffffffffffffffff
    _max_exp_array[38] = 0x15ecf52776a1ffffffffffffffffffffff
    _max_exp_array[39] = 0x15060c256cb2ffffffffffffffffffffff
    _max_exp_array[40] = 0x1428a2f98d72ffffffffffffffffffffff
    _max_exp_array[41] = 0x13545598e5c23fffffffffffffffffffff
    _max_exp_array[42] = 0x1288c4161ce1dfffffffffffffffffffff
    _max_exp_array[43] = 0x11c592761c666fffffffffffffffffffff
    _max_exp_array[44] = 0x110a688680a757ffffffffffffffffffff
    _max_exp_array[45] = 0x1056f1b5bedf77ffffffffffffffffffff
    _max_exp_array[46] = 0x0faadceceeff8bffffffffffffffffffff
    _max_exp_array[47] = 0x0f05dc6b27edadffffffffffffffffffff
    _max_exp_array[48] = 0x0e67a5a25da4107fffffffffffffffffff
    _max_exp_array[49] = 0x0dcff115b14eedffffffffffffffffffff
    _max_exp_array[50] = 0x0d3e7a392431239fffffffffffffffffff
    _max_exp_array[51] = 0x0cb2ff529eb71e4fffffffffffffffffff
    _max_exp_array[52] = 0x0c2d415c3db974afffffffffffffffffff
    _max_exp_array[53] = 0x0bad03e7d883f69bffffffffffffffffff
    _max_exp_array[54] = 0x0b320d03b2c343d5ffffffffffffffffff
    _max_exp_array[55] = 0x0abc25204e02828dffffffffffffffffff
    _max_exp_array[56] = 0x0a4b16f74ee4bb207fffffffffffffffff
    _max_exp_array[57] = 0x09deaf736ac1f569ffffffffffffffffff
    _max_exp_array[58] = 0x0976bd9952c7aa957fffffffffffffffff
    _max_exp_array[59] = 0x09131271922eaa606fffffffffffffffff
    _max_exp_array[60] = 0x08b380f3558668c46fffffffffffffffff
    _max_exp_array[61] = 0x0857ddf0117efa215bffffffffffffffff
    _max_exp_array[62] = 0x07ffffffffffffffffffffffffffffffff
    _max_exp_array[63] = 0x07abbf6f6abb9d087fffffffffffffffff
    _max_exp_array[64] = 0x075af62cbac95f7dfa7fffffffffffffff
    _max_exp_array[65] = 0x070d7fb7452e187ac13fffffffffffffff
    _max_exp_array[66] = 0x06c3390ecc8af379295fffffffffffffff
    _max_exp_array[67] = 0x067c00a3b07ffc01fd6fffffffffffffff
    _max_exp_array[68] = 0x0637b647c39cbb9d3d27ffffffffffffff
    _max_exp_array[69] = 0x05f63b1fc104dbd39587ffffffffffffff
    _max_exp_array[70] = 0x05b771955b36e12f7235ffffffffffffff
    _max_exp_array[71] = 0x057b3d49dda84556d6f6ffffffffffffff
    _max_exp_array[72] = 0x054183095b2c8ececf30ffffffffffffff
    _max_exp_array[73] = 0x050a28be635ca2b888f77fffffffffffff
    _max_exp_array[74] = 0x04d5156639708c9db33c3fffffffffffff
    _max_exp_array[75] = 0x04a23105873875bd52dfdfffffffffffff
    _max_exp_array[76] = 0x0471649d87199aa990756fffffffffffff
    _max_exp_array[77] = 0x04429a21a029d4c1457cfbffffffffffff
    _max_exp_array[78] = 0x0415bc6d6fb7dd71af2cb3ffffffffffff
    _max_exp_array[79] = 0x03eab73b3bbfe282243ce1ffffffffffff
    _max_exp_array[80] = 0x03c1771ac9fb6b4c18e229ffffffffffff
    _max_exp_array[81] = 0x0399e96897690418f785257fffffffffff
    _max_exp_array[82] = 0x0373fc456c53bb779bf0ea9fffffffffff
    _max_exp_array[83] = 0x034f9e8e490c48e67e6ab8bfffffffffff
    _max_exp_array[84] = 0x032cbfd4a7adc790560b3337ffffffffff
    _max_exp_array[85] = 0x030b50570f6e5d2acca94613ffffffffff
    _max_exp_array[86] = 0x02eb40f9f620fda6b56c2861ffffffffff
    _max_exp_array[87] = 0x02cc8340ecb0d0f520a6af58ffffffffff
    _max_exp_array[88] = 0x02af09481380a0a35cf1ba02ffffffffff
    _max_exp_array[89] = 0x0292c5bdd3b92ec810287b1b3fffffffff
    _max_exp_array[90] = 0x0277abdcdab07d5a77ac6d6b9fffffffff
    _max_exp_array[91] = 0x025daf6654b1eaa55fd64df5efffffffff
    _max_exp_array[92] = 0x0244c49c648baa98192dce88b7ffffffff
    _max_exp_array[93] = 0x022ce03cd5619a311b2471268bffffffff
    _max_exp_array[94] = 0x0215f77c045fbe885654a44a0fffffffff
    _max_exp_array[95] = 0x01ffffffffffffffffffffffffffffffff
    _max_exp_array[96] = 0x01eaefdbdaaee7421fc4d3ede5ffffffff
    _max_exp_array[97] = 0x01d6bd8b2eb257df7e8ca57b09bfffffff
    _max_exp_array[98] = 0x01c35fedd14b861eb0443f7f133fffffff
    _max_exp_array[99] = 0x01b0ce43b322bcde4a56e8ada5afffffff
    _max_exp_array[100] = 0x019f0028ec1fff007f5a195a39dfffffff
    _max_exp_array[101] = 0x018ded91f0e72ee74f49b15ba527ffffff
    _max_exp_array[102] = 0x017d8ec7f04136f4e5615fd41a63ffffff
    _max_exp_array[103] = 0x016ddc6556cdb84bdc8d12d22e6fffffff
    _max_exp_array[104] = 0x015ecf52776a1155b5bd8395814f7fffff
    _max_exp_array[105] = 0x015060c256cb23b3b3cc3754cf40ffffff
    _max_exp_array[106] = 0x01428a2f98d728ae223ddab715be3fffff
    _max_exp_array[107] = 0x013545598e5c23276ccf0ede68034fffff
    _max_exp_array[108] = 0x01288c4161ce1d6f54b7f61081194fffff
    _max_exp_array[109] = 0x011c592761c666aa641d5a01a40f17ffff
    _max_exp_array[110] = 0x0110a688680a7530515f3e6e6cfdcdffff
    _max_exp_array[111] = 0x01056f1b5bedf75c6bcb2ce8aed428ffff
    _max_exp_array[112] = 0x00faadceceeff8a0890f3875f008277fff
    _max_exp_array[113] = 0x00f05dc6b27edad306388a600f6ba0bfff
    _max_exp_array[114] = 0x00e67a5a25da41063de1495d5b18cdbfff
    _max_exp_array[115] = 0x00dcff115b14eedde6fc3aa5353f2e4fff
    _max_exp_array[116] = 0x00d3e7a3924312399f9aae2e0f868f8fff
    _max_exp_array[117] = 0x00cb2ff529eb71e41582cccd5a1ee26fff
    _max_exp_array[118] = 0x00c2d415c3db974ab32a51840c0b67edff
    _max_exp_array[119] = 0x00bad03e7d883f69ad5b0a186184e06bff
    _max_exp_array[120] = 0x00b320d03b2c343d4829abd6075f0cc5ff
    _max_exp_array[121] = 0x00abc25204e02828d73c6e80bcdb1a95bf
    _max_exp_array[122] = 0x00a4b16f74ee4bb2040a1ec6c15fbbf2df
    _max_exp_array[123] = 0x009deaf736ac1f569deb1b5ae3f36c130f
    _max_exp_array[124] = 0x00976bd9952c7aa957f5937d790ef65037
    _max_exp_array[125] = 0x009131271922eaa6064b73a22d0bd4f2bf
    _max_exp_array[126] = 0x008b380f3558668c46c91c49a2f8e967b9
    _max_exp_array[127] = 0x00857ddf0117efa215952912839f6473e6

    @external(readonly=True)
    def calculatePurchaseReturn(self,
                                  _supply: int,
                                  _connector_balance: int,
                                  _connector_weight: int,
                                  _deposit_amount: int) -> int:
        """
        Given a token supply, connector balance, weight and a deposit amount (in the connector token),
        calculates the return for a given conversion (in the main token)

        Formula:
        Return = _supply * ((1 + _depositAmount / _connectorBalance) ^ (_connectorWeight / 1000000) - 1)

        :param _supply: token total supply
        :param _connector_balance: total connector balance
        :param _connector_weight: connector weight, represented in ppm, 1-1000000
        :param _deposit_amount: deposit amount, in connector token
        :return: purchase return amount
        """
        # validate input
        if not (_supply > 0 and _connector_balance > 0 and self._MAX_WEIGHT >= _connector_weight > 0):
            revert("Invalid input")

        # special case for 0 deposit amount
        if _deposit_amount == 0:
            return 0

        # special case if the weight = 100%
        if _connector_weight == self._MAX_WEIGHT:
            return (_supply * _deposit_amount)/_connector_balance
        base_n = _deposit_amount + _connector_balance
        result, precision = self._power(base_n, _connector_balance, _connector_weight, self._MAX_WEIGHT)
        temp = _supply * result >> precision
        return temp - _supply

    @external(readonly=True)
    def calculateSaleReturn(self,
                              _supply: int,
                              _connector_balance: int,
                              _connector_weight: int,
                              _sell_amount: int) -> int:
        """
        Given a token supply, connector balance, weight and a sell amount (in the main token),
        calculates the return for a given conversion (in the connector token)

        Formula:
        Return = _connectorBalance * (1 - (1 - _sellAmount / _supply) ^ (1 / (_connectorWeight / 1000000)))

        :param _supply: token total supply
        :param _connector_balance: total connector
        :param _connector_weight: constant connector Weight, represented in ppm, 1-1000000
        :param _sell_amount: sell amount, in the token itself
        :return: sale return amount
        """
        # validate input
        if not (_supply > 0 and _connector_balance > 0 and self._MAX_WEIGHT >= _connector_weight > 0
                and _sell_amount <= _supply):
            revert("Invalid input")

        # special case for 0 sell amount
        if _sell_amount == 0:
            return 0

        # special case for selling the entire supply
        if _sell_amount == _supply:
            return _connector_balance

        # special case if the weight == 100%
        if _connector_weight == self._MAX_WEIGHT:
            return (_connector_balance * _sell_amount) / _supply

        base_d = _supply - _sell_amount
        result, precision = self._power(_supply, base_d, self._MAX_WEIGHT, _connector_weight)
        temp1 = _connector_balance * result
        temp2 = _connector_balance << precision
        return (temp1 - temp2) / result

    @external(readonly=True)
    def calculateCrossConnectorReturn(self, _from_connector_balance: int, _from_connector_weight: int,
                                      _to_connector_balance: int, _to_connector_weight: int, _amount: int) -> int:
        """
        Given two connector balances/weights and a sell amount (in the first connector token),
        calculates the return for a conversion from the first connector token to the second connector token
        (in the second connector token)

        Formula:
        Return = _toConnectorBalance * (1 - (_fromConnectorBalance / (_fromConnectorBalance + _amount)) ^ (_fromConnectorWeight / _toConnectorWeight))

        :param _from_connector_balance: input connector balance
        :param _from_connector_weight: input connector weight, represented in ppm, 1-1000000
        :param _to_connector_balance: output connector balance
        :param _to_connector_weight: output connector weight, represented in ppm, 1-1000000
        :param _amount: input connector amount
        :return: second connector amount
        """
        # validate input
        if not (_from_connector_balance > 0 and self._MAX_WEIGHT >= _from_connector_weight > 0
                and _to_connector_balance > 0 and self._MAX_WEIGHT >= _to_connector_weight > 0):
            revert("Invalid input")

        # special case for equal weights
        if _from_connector_weight == _to_connector_weight:
            return (_to_connector_balance * _amount) / (_from_connector_balance + _amount)

        base_n = _from_connector_balance + _amount
        result, precision = self._power(base_n, _from_connector_balance, _from_connector_weight, _to_connector_weight)
        temp1 = _to_connector_balance * result
        temp2 = _to_connector_balance << precision
        return (temp1 - temp2) / result

    def _power(self, _base_n: int, _base_d: int, _exp_n: int, _exp_d: int) -> (int, int):
        """
        General Description:
            Determine a value of precision.
            Calculate an integer approximation of (_baseN / _baseD) ^ (_expN / _expD) * 2 ^ precision.
            Return the result along with the precision used.

        Detailed Description:
            Instead of calculating "base ^ exp", we calculate "e ^ (log(base) * exp)".
            The value of "log(base)" is represented with an integer slightly smaller than "log(base) * 2 ^ precision".
            The larger "precision" is, the more accurately this value represents the real value.
            However, the larger "precision" is, the more bits are required in order to store this value.
            And the exponentiation function, which takes "x" and calculates "e ^ x", is limited to a maximum exponent (maximum value of "x").
            This maximum exponent depends on the "precision" used, and it is given by "_max_exp_array[precision] >> (MAX_PRECISION - precision)".
            Hence we need to determine the highest precision which can be used for the given input, before calling the exponentiation function.
            This allows us to compute "base ^ exp" with maximum accuracy and without exceeding 256 bits in any of the intermediate computations.
            This functions assumes that "_expN < 2 ^ 256 / log(MAX_NUM - 1)", otherwise the multiplication should be replaced with a "safeMul".

        :param _base_n:
        :param _base_d:
        :param _exp_n:
        :param _exp_d:
        :return:
        """
        if not (_base_n < self.MAX_NUM):
            revert("Invalid input")

        base = _base_n * self._FIXED_1 / _base_d
        if base < self.OPT_LOG_MAX_VAL:
            base_log = self._optimal_log(base)
        else:
            base_log = self._general_log(base)

        base_log_times_exp = base_log * _exp_n / _exp_d
        if base_log_times_exp < self.OPT_EXP_MAX_VAL:
            return self._optimal_exp(base_log_times_exp), self._MAX_PRECISION
        else:
            precision = self._find_position_in_max_exp_array(base_log_times_exp)
            return self._general_exp(base_log_times_exp >> (self._MAX_PRECISION - precision), precision), precision

    def _general_log(self, x: int) -> int:
        """
        Compute log(x / FIXED_1) * FIXED_1.
        This functions assumes that "x >= FIXED_1", because the output would be negative otherwise.

        :param x:
        :return:
        """
        res = 0

        # If x >= 2, then we compute the integer part of log2(x), which is larger than 0.
        if x >= self._FIXED_2:
            count = self._floor_log2(x / self._FIXED_1)
            x >> count
            res = count * self._FIXED_1

        # If x > 1, then we compute the fraction part of log2(x), which is larger than 0.
        if x > self._FIXED_1:
            for i in range(self._MAX_PRECISION, 0, -1):
                # now 1 < x < 4
                x = (x * x) / self._FIXED_1
                if x >= self._FIXED_2:
                    # now 1 < x < 2
                    x >>= 1
                    res += self._ONE << (i - 1)

        return res * self._LN2_NUMERATOR / self._LN2_DENOMINATOR

    def _floor_log2(self, _n: int) -> int:
        """Compute the largest integer smaller than or equal to the binary logarithm of the input.

        :param _n:
        :return:
        """
        res = 0

        if _n < 256:
            # At most 8 iterations
            while _n > 0:
                _n >> 1
                res += 1
        else:
            # Exactly 8 iterations
            s = 128
            while s > 0:
                if _n >= (self._ONE << s):
                    _n >>= s
                    res |= s
                s >>= 1
        return res

    def _find_position_in_max_exp_array(self, _x: int) -> int:
        """
        The global "_max_exp_array" is sorted in descending order, and therefore the following statements are equivalent:
        - This function finds the position of [the smallest value in "_max_exp_array" larger than or equal to "x"]
        - This function finds the highest position of [a value in "_max_exp_array" larger than or equal to "x"]

        :param _x:
        :return:
        """
        lo = self._MIN_PRECISION
        hi = self._MAX_PRECISION

        while lo + 1 < hi:
            mid = (lo + hi)/2
            if self._max_exp_array[mid] >= _x:
                lo = mid
            else:
                hi = mid

        if self._max_exp_array[hi] >= _x:
            return hi
        if self._max_exp_array[lo] >= _x:
            return lo

        return 0

    def _general_exp(self, _x: int, _precision: int) -> int:
        """
        This function can be auto-generated by the script 'PrintFunctionGeneralExp.py'.
        It approximates "e ^ x" via maclaurin summation: "(x^0)/0! + (x^1)/1! + ... + (x^n)/n!".
        It returns "e ^ (x / 2 ^ precision) * 2 ^ precision", that is, the result is upshifted for accuracy.
        The global "_max_exp_array" maps each "precision" to "((maximumExponent + 1) << (MAX_PRECISION - precision)) - 1".
        The maximum permitted value for "x" is therefore given by "_max_exp_array[precision] >> (MAX_PRECISION - precision)".

        :param _x:
        :param _precision:
        :return:
        """
        xi = _x
        res = 0
        xi = (xi * _x) >> _precision
        # add x ^ 02 * (33! / 02!)
        res += xi * 0x3442c4e6074a82f1797f72ac0000000
        xi = (xi * _x) >> _precision
        # add x ^ 03 * (33! / 03!)
        res += xi * 0x116b96f757c380fb287fd0e40000000
        xi = (xi * _x) >> _precision
        # add x ^ 04 * (33! / 04!)
        res += xi * 0x045ae5bdd5f0e03eca1ff4390000000
        xi = (xi * _x) >> _precision
        # add x ^ 05 * (33! / 05!)
        res += xi * 0x00defabf91302cd95b9ffda50000000
        xi = (xi * _x) >> _precision
        # add x ^ 06 * (33! / 06!)
        res += xi * 0x002529ca9832b22439efff9b8000000
        xi = (xi * _x) >> _precision
        # add x ^ 07 * (33! / 07!)
        res += xi * 0x00054f1cf12bd04e516b6da88000000
        xi = (xi * _x) >> _precision
        # add x ^ 08 * (33! / 08!)
        res += xi * 0x0000a9e39e257a09ca2d6db51000000
        xi = (xi * _x) >> _precision
        # add x ^ 09 * (33! / 09!)
        res += xi * 0x000012e066e7b839fa050c309000000
        xi = (xi * _x) >> _precision
        # add x ^ 10 * (33! / 10!)
        res += xi * 0x000001e33d7d926c329a1ad1a800000
        xi = (xi * _x) >> _precision
        # add x ^ 11 * (33! / 11!)
        res += xi * 0x0000002bee513bdb4a6b19b5f800000
        xi = (xi * _x) >> _precision
        # add x ^ 12 * (33! / 12!)
        res += xi * 0x00000003a9316fa79b88eccf2a00000
        xi = (xi * _x) >> _precision
        # add x ^ 13 * (33! / 13!)
        res += xi * 0x0000000048177ebe1fa812375200000
        xi = (xi * _x) >> _precision
        # add x ^ 14 * (33! / 14!)
        res += xi * 0x0000000005263fe90242dcbacf00000
        xi = (xi * _x) >> _precision
        # add x ^ 15 * (33! / 15!)
        res += xi * 0x000000000057e22099c030d94100000
        xi = (xi * _x) >> _precision
        # add x ^ 16 * (33! / 16!)
        res += xi * 0x0000000000057e22099c030d9410000
        xi = (xi * _x) >> _precision
        # add x ^ 17 * (33! / 17!)
        res += xi * 0x00000000000052b6b54569976310000
        xi = (xi * _x) >> _precision
        # add x ^ 18 * (33! / 18!)
        res += xi * 0x00000000000004985f67696bf748000
        xi = (xi * _x) >> _precision
        # add x ^ 19 * (33! / 19!)
        res += xi * 0x000000000000003dea12ea99e498000
        xi = (xi * _x) >> _precision
        # add x ^ 20 * (33! / 20!)
        res += xi * 0x00000000000000031880f2214b6e000
        xi = (xi * _x) >> _precision
        # add x ^ 21 * (33! / 21!)
        res += xi * 0x000000000000000025bcff56eb36000
        xi = (xi * _x) >> _precision
        # add x ^ 22 * (33! / 22!)
        res += xi * 0x000000000000000001b722e10ab1000
        xi = (xi * _x) >> _precision
        # add x ^ 23 * (33! / 23!)
        res += xi * 0x0000000000000000001317c70077000
        xi = (xi * _x) >> _precision
        # add x ^ 24 * (33! / 24!)
        res += xi * 0x00000000000000000000cba84aafa00
        xi = (xi * _x) >> _precision
        # add x ^ 25 * (33! / 25!)
        res += xi * 0x00000000000000000000082573a0a00
        xi = (xi * _x) >> _precision
        # add x ^ 26 * (33! / 26!)
        res += xi * 0x00000000000000000000005035ad900
        xi = (xi * _x) >> _precision
        # add x ^ 27 * (33! / 27!)
        res += xi * 0x000000000000000000000002f881b00
        xi = (xi * _x) >> _precision
        # add x ^ 28 * (33! / 28!)
        res += xi * 0x0000000000000000000000001b29340
        xi = (xi * _x) >> _precision
        # add x ^ 29 * (33! / 29!)
        res += xi * 0x00000000000000000000000000efc40
        xi = (xi * _x) >> _precision
        # add x ^ 30 * (33! / 30!)
        res += xi * 0x0000000000000000000000000007fe0
        xi = (xi * _x) >> _precision
        # add x ^ 31 * (33! / 31!)
        res += xi * 0x0000000000000000000000000000420
        xi = (xi * _x) >> _precision
        # add x ^ 32 * (33! / 32!)
        res += xi * 0x0000000000000000000000000000021
        xi = (xi * _x) >> _precision
        # add x ^ 33 * (33! / 33!)
        res += xi * 0x0000000000000000000000000000001

        # divide by 33! and then add x ^ 1 / 1! + x ^ 0 / 0!
        return res / 0x688589cc0e9505e2f2fee5580000000 + _x + (self._ONE << _precision)

    def _optimal_log(self, x: int) -> int:
        """
        Return log(x / FIXED_1) * FIXED_1
        Input range: FIXED_1 <= x <= LOG_EXP_MAX_VAL - 1
        Auto-generated via 'PrintFunctionOptimalLog.py'
        Detailed description:
        - Rewrite the input as a product of natural exponents and a single residual r, such that 1 < r < 2
        - The natural logarithm of each (pre-calculated) exponent is the degree of the exponent
        - The natural logarithm of r is calculated via Taylor series for log(1 + x), where x = r - 1
        - The natural logarithm of the input is calculated by summing up the intermediate results above
        - For example: log(250) = log(e^4 * e^1 * e^0.5 * 1.021692859) = 4 + 1 + 0.5 + log(1 + 0.021692859)

        :param x:
        :return:
        """
        res = 0
        # add 1 / 2 ^ 1
        if x >= 0xd3094c70f034de4b96ff7d5b6f99fcd8:
            res += 0x40000000000000000000000000000000
            x = x * self._FIXED_1 / 0xd3094c70f034de4b96ff7d5b6f99fcd8
        # add 1 / 2 ^ 2
        if x >= 0xa45af1e1f40c333b3de1db4dd55f29a7:
            res += 0x20000000000000000000000000000000
            x = x * self._FIXED_1 / 0xa45af1e1f40c333b3de1db4dd55f29a7
        # add 1 / 2 ^ 3
        if x >= 0x910b022db7ae67ce76b441c27035c6a1:
            res += 0x10000000000000000000000000000000
            x = x * self._FIXED_1 / 0x910b022db7ae67ce76b441c27035c6a1
        # add 1 / 2 ^ 4
        if x >= 0x88415abbe9a76bead8d00cf112e4d4a8:
            res += 0x08000000000000000000000000000000
            x = x * self._FIXED_1 / 0x88415abbe9a76bead8d00cf112e4d4a8
        # add 1 / 2 ^ 5
        if x >= 0x84102b00893f64c705e841d5d4064bd3:
            res += 0x04000000000000000000000000000000
            x = x * self._FIXED_1 / 0x84102b00893f64c705e841d5d4064bd3
        # add 1 / 2 ^ 6
        if x >= 0x8204055aaef1c8bd5c3259f4822735a2:
            res += 0x02000000000000000000000000000000
            x = x * self._FIXED_1 / 0x8204055aaef1c8bd5c3259f4822735a2
        # add 1 / 2 ^ 7
        if x >= 0x810100ab00222d861931c15e39b44e99:
            res += 0x01000000000000000000000000000000
            x = x * self._FIXED_1 / 0x810100ab00222d861931c15e39b44e99
        # add 1 / 2 ^ 8
        if x >= 0x808040155aabbbe9451521693554f733:
            res += 0x00800000000000000000000000000000
            x = x * self._FIXED_1 / 0x808040155aabbbe9451521693554f733

        z = y = x - self._FIXED_1
        w = y * y / self._FIXED_1
        # add y ^ 01 / 01 - y ^ 02 / 02
        res += z * (0x100000000000000000000000000000000 - y) / 0x100000000000000000000000000000000
        z = z * w / self._FIXED_1
        # add y^03 / 03 - y^04 / 04
        res += z * (0x0aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa - y) / 0x200000000000000000000000000000000
        z = z * w / self._FIXED_1
        # add y^05 / 05 - y^06 / 06
        res += z * (0x099999999999999999999999999999999 - y) / 0x300000000000000000000000000000000
        z = z * w / self._FIXED_1
        # add y^07 / 07 - y^08 / 08
        res += z * (0x092492492492492492492492492492492 - y) / 0x400000000000000000000000000000000
        z = z * w / self._FIXED_1
        # add y^09 / 09 - y^10 / 10
        res += z * (0x08e38e38e38e38e38e38e38e38e38e38e - y) / 0x500000000000000000000000000000000
        z = z * w / self._FIXED_1
        # add y^11 / 11 - y^12 / 12
        res += z * (0x08ba2e8ba2e8ba2e8ba2e8ba2e8ba2e8b - y) / 0x600000000000000000000000000000000
        z = z * w / self._FIXED_1
        # add y^13 / 13 - y^14 / 14
        res += z * (0x089d89d89d89d89d89d89d89d89d89d89 - y) / 0x700000000000000000000000000000000
        z = z * w / self._FIXED_1
        # add y^15 / 15 - y^16 / 16
        res += z * (0x088888888888888888888888888888888 - y) / 0x800000000000000000000000000000000
        return res

    def _optimal_exp(self, x: int) -> int:
        """
        Return e ^ (x / FIXED_1) * FIXED_1
        Input range: 0 <= x <= OPT_EXP_MAX_VAL - 1
        Auto-generated via 'PrintFunctionOptimalExp.py'
        Detailed description:
        - Rewrite the input as a sum of binary exponents and a single residual r, as small as possible
        - The exponentiation of each binary exponent is given (pre-calculated)
        - The exponentiation of r is calculated via Taylor series for e^x, where x = r
        - The exponentiation of the input is calculated by multiplying the intermediate results above
        - For example: e^5.021692859 = e^(4 + 1 + 0.5 + 0.021692859) = e^4 * e^1 * e^0.5 * e^0.021692859

        :param x:
        :return:
        """
        res = 0
        # get the input modulo 2^(-3)
        z = y = x % 0x10000000000000000000000000000000
        # add y^02 * (20! / 02!)
        z = z * y / self._FIXED_1
        res += z * 0x10e1b3be415a0000
        # add y^03 * (20! / 03!)
        z = z * y / self._FIXED_1
        res += z * 0x05a0913f6b1e0000
        # add y^04 * (20! / 04!)
        z = z * y / self._FIXED_1
        res += z * 0x0168244fdac78000
        # add y^05 * (20! / 05!)
        z = z * y / self._FIXED_1
        res += z * 0x004807432bc18000
        # add y^06 * (20! / 06!)
        z = z * y / self._FIXED_1
        res += z * 0x000c0135dca04000
        # add y^07 * (20! / 07!)
        z = z * y / self._FIXED_1
        res += z * 0x0001b707b1cdc000
        # add y^08 * (20! / 08!)
        z = z * y / self._FIXED_1
        res += z * 0x000036e0f639b800
        # add y^09 * (20! / 09!)
        z = z * y / self._FIXED_1
        res += z * 0x00000618fee9f800
        # add y^10 * (20! / 10!)
        z = z * y / self._FIXED_1
        res += z * 0x0000009c197dcc00
        # add y^11 * (20! / 11!)
        z = z * y / self._FIXED_1
        res += z * 0x0000000e30dce400
        # add y^12 * (20! / 12!)
        z = z * y / self._FIXED_1
        res += z * 0x000000012ebd1300
        # add y^13 * (20! / 13!)
        z = z * y / self._FIXED_1
        res += z * 0x0000000017499f00
        # add y^14 * (20! / 14!)
        z = z * y / self._FIXED_1
        res += z * 0x0000000001a9d480
        # add y^15 * (20! / 15!)
        z = z * y / self._FIXED_1
        res += z * 0x00000000001c6380
        # add y^16 * (20! / 16!)
        z = z * y / self._FIXED_1
        res += z * 0x000000000001c638
        # add y^17 * (20! / 17!)
        z = z * y / self._FIXED_1
        res += z * 0x0000000000001ab8
        # add y^18 * (20! / 18!)
        z = z * y / self._FIXED_1
        res += z * 0x000000000000017c
        # add y^19 * (20! / 19!)
        z = z * y / self._FIXED_1
        res += z * 0x0000000000000014
        # add y^20 * (20! / 20!)
        z = z * y / self._FIXED_1
        res += z * 0x0000000000000001
        # divide by 20! and then add y^1 / 1! + y^0 / 0!
        res = res / 0x21c3677c82b40000 + y + self._FIXED_1

        # multiply by e ^ 2 ^ (-3)
        if (x & 0x010000000000000000000000000000000) != 0:
            res = res * 0x1c3d6a24ed82218787d624d3e5eba95f9 / 0x18ebef9eac820ae8682b9793ac6d1e776
        # multiply by e ^ 2 ^ (-2)
        if (x & 0x020000000000000000000000000000000) != 0:
            res = res * 0x18ebef9eac820ae8682b9793ac6d1e778 / 0x1368b2fc6f9609fe7aceb46aa619baed4
        # multiply by e ^ 2 ^ (-1)
        if (x & 0x040000000000000000000000000000000) != 0:
            res = res * 0x1368b2fc6f9609fe7aceb46aa619baed5 / 0x0bc5ab1b16779be3575bd8f0520a9f21f
        # multiply by e ^ 2 ^ (+0)
        if (x & 0x080000000000000000000000000000000) != 0:
            res = res * 0x0bc5ab1b16779be3575bd8f0520a9f21e / 0x0454aaa8efe072e7f6ddbab84b40a55c9
        # multiply by e ^ 2 ^ (+1)
        if (x & 0x100000000000000000000000000000000) != 0:
            res = res * 0x0454aaa8efe072e7f6ddbab84b40a55c5 / 0x00960aadc109e7a3bf4578099615711ea
        # multiply by e ^ 2 ^ (+2)
        if (x & 0x200000000000000000000000000000000) != 0:
            res = res * 0x00960aadc109e7a3bf4578099615711d7 / 0x0002bf84208204f5977f9a8cf01fdce3d
        # multiply by e ^ 2 ^ (+3)
        if (x & 0x400000000000000000000000000000000) != 0:
            res = res * 0x0002bf84208204f5977f9a8cf01fdc307 / 0x0000003c6ab775dd0b95b4cbee7e65d11

        return res
