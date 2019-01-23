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

from contracts.formula.auto_generate.common.functions import get_coefficients
from contracts.formula.auto_generate.common.constants import NUM_OF_COEFFICIENTS


coefficients = get_coefficients(NUM_OF_COEFFICIENTS)


valueMaxLen = len(hex(coefficients[1]))
indexMaxLen = len(str(len(coefficients)))


print('        xi = x')
print('        res = 0')
for i in range(1, len(coefficients)):
    print('        # add x^{1:0{2}d} * ({0:0{2}d}! / {1:0{2}d}!)'.format(len(coefficients), i + 1, indexMaxLen))
    print('        xi = (xi * x) >> precision')
    print('        res += xi * {0:#0{1}x}'.format(coefficients[i], valueMaxLen))
print('')
print('        # divide by {}! and then add x^1 / 1! + x^0 / 0!'.format(len(coefficients)))
print('        return res // 0x{:x} + x + (self._ONE << precision)'.format(coefficients[0]))
