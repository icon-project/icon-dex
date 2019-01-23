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
from contracts.formula.auto_generate.common.functions import get_max_exp_array
from contracts.formula.auto_generate.common.functions import get_max_val_array
from contracts.formula.auto_generate.common.constants import NUM_OF_COEFFICIENTS
from contracts.formula.auto_generate.common.constants import MIN_PRECISION
from contracts.formula.auto_generate.common.constants import MAX_PRECISION

coefficients = get_coefficients(NUM_OF_COEFFICIENTS)
max_exp_array = get_max_exp_array(coefficients, MAX_PRECISION+1)
max_val_array = get_max_val_array(coefficients, max_exp_array)


print('MIN_PRECISION = {}'.format(MIN_PRECISION))
print('MAX_PRECISION = {}'.format(MAX_PRECISION))

# 0~127
print('max_exp_array = [')
for precision in range(len(max_exp_array)):
    print('    {:40s}  # {:<3d}'.format(hex(max_exp_array[precision])+',', precision))
print(']')


print('max_val_array = [')
for precision in range(len(max_val_array)):
    print('    {:40s}  # {:<3d}'.format(hex(max_val_array[precision])+',', precision))
print(']')



