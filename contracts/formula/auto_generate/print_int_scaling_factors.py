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

from contracts.formula.auto_generate.common.constants import MAX_PRECISION


FIXED_1 = 1 << MAX_PRECISION
FIXED_2 = 2 << MAX_PRECISION
MAX_NUM = 1 << (256-MAX_PRECISION)


maxLen = len(hex(max([FIXED_1, FIXED_2, MAX_NUM])))


print('    _FIXED_1 = {0:#0{1}x}'.format(FIXED_1, maxLen))
print('    _FIXED_2 = {0:#0{1}x}'.format(FIXED_2, maxLen))
print('    _MAX_NUM = {0:#0{1}x}'.format(MAX_NUM, maxLen))
