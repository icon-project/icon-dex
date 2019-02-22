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

from contracts.formula.auto_generate.common.functions import get_coefficients
from contracts.formula.auto_generate.common.functions import get_max_exp_array
from contracts.formula.auto_generate.common.constants import NUM_OF_COEFFICIENTS
from contracts.formula.auto_generate.common.constants import MIN_PRECISION
from contracts.formula.auto_generate.common.constants import MAX_PRECISION


coefficients = get_coefficients(NUM_OF_COEFFICIENTS)
max_exp_array = get_max_exp_array(coefficients, MAX_PRECISION+1)
max_exp_array_shl = [((max_exp_array[precision]+1) << (MAX_PRECISION-precision))-1
                     for precision in range(len(max_exp_array))]

_len = len(hex(max_exp_array_shl[0]))

print('    _max_exp_array = [None] * {}'.format(len(max_exp_array)))
for precision in range(len(max_exp_array)):
    prefix = '' if MIN_PRECISION <= precision <= MAX_PRECISION else '# '
    print('    {0:s}_max_exp_array[{1:d}] = {2:#0{3}x}'.format(prefix, precision, max_exp_array_shl[precision], _len))

