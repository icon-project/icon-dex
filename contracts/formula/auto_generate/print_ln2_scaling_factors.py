# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
# Copyright 2017 Bprotocol Foundation
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

from decimal import Decimal
from decimal import getcontext
from decimal import ROUND_FLOOR
from decimal import ROUND_CEILING

from contracts.formula.auto_generate.common.constants import MAX_PRECISION


getcontext().prec = 100


def ln(n):
    return Decimal(n).ln()


def log2(n):
    return ln(n)/ln(2)


def floor(d):
    return int(d.to_integral_exact(rounding=ROUND_FLOOR))


def ceiling(d):
    return int(d.to_integral_exact(rounding=ROUND_CEILING))


LN2_NUMERATOR = (2**256-1) // floor(log2(2**(256-MAX_PRECISION)-1)*2**MAX_PRECISION)
LN2_DENOMINATOR = ceiling(LN2_NUMERATOR/ln(2))


print('    _LN2_NUMERATOR = 0x{:x}'.format(LN2_NUMERATOR))
print('    _LN2_DENOMINATOR = 0x{:x}'.format(LN2_DENOMINATOR))
