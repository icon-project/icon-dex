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

# source code from
# https://github.com/bancorprotocol/contracts

from decimal import Decimal
from decimal import getcontext
from collections import namedtuple

from contracts.formula.auto_generate.common.functions import optimal_log
from contracts.formula.auto_generate.common.constants import MAX_PRECISION
from contracts.formula.auto_generate.common.constants import LOG_MAX_HI_TERM_VAL
from contracts.formula.auto_generate.common.constants import LOG_NUM_OF_HI_TERMS


getcontext().prec = 100
FIXED_1 = (1 << MAX_PRECISION)


HiTerm = namedtuple('HiTerm', 'val,exp')
LoTerm = namedtuple('LoTerm', 'num,den')


hiTerms = []
loTerms = []


for n in range(LOG_NUM_OF_HI_TERMS+1):
    cur = Decimal(LOG_MAX_HI_TERM_VAL)/2**n
    val = int(FIXED_1*cur)
    exp = int(FIXED_1*cur.exp())
    hiTerms.append(HiTerm(val, exp))


MAX_VAL = hiTerms[0].exp-1
loTerms = [LoTerm(FIXED_1*2,FIXED_1*2)]
res = optimal_log(MAX_VAL, hiTerms, loTerms, FIXED_1)
while True:
    n = len(loTerms)
    val = FIXED_1*(2*n+2)
    loTermsNext = loTerms+[LoTerm(val//(2*n+1), val)]
    resNext = optimal_log(MAX_VAL, hiTerms, loTermsNext, FIXED_1)
    if res < resNext:
        res = resNext
        loTerms = loTermsNext
    else:
        break


hiTermValMaxLen = len(hex(hiTerms[+1].val))
hiTermExpMaxLen = len(hex(hiTerms[+1].exp))
loTermNumMaxLen = len(hex(loTerms[0].num))
loTermDenMaxLen = len(hex(loTerms[-1].den))


hiTermIndMaxLen = len(str(len(hiTerms)-1))
loTermPosMaxLen = len(str(len(loTerms)*2-1))
loTermNegMaxLen = len(str(len(loTerms)*2-0))

print('        res = 0')
for n in range(1, len(hiTerms)):
    str1 = '{0:#0{1}x}'.format(hiTerms[n].exp, hiTermExpMaxLen)
    str2 = '{0:#0{1}x}'.format(hiTerms[n].val, hiTermValMaxLen)
    str3 = '{0:0{1}d}' .format(n, hiTermIndMaxLen)
    print('        # add {} / 2^{}'.format(LOG_MAX_HI_TERM_VAL, str3))
    print('        if x >= {}:'.format(str1))
    print('            res += {}'.format(str2))
    print('            x = x * self._FIXED_1 // {}'.format(str1))
print('')
print('        z = y = x - self._FIXED_1')
print('        w = y * y // self._FIXED_1')
for n in range(len(loTerms)-1):
    str1 = '{0:#0{1}x}'.format(loTerms[n].num, loTermNumMaxLen)
    str2 = '{0:#0{1}x}'.format(loTerms[n].den, loTermDenMaxLen)
    str3 = '{0:0{1}d}' .format(2*n+1, loTermPosMaxLen)
    str4 = '{0:0{1}d}' .format(2*n+2, loTermNegMaxLen)
    print('        # add y^{} / {} - y^{} / {}'.format(str3, str3, str4, str4))
    print('        res += z * ({} - y) // {}'.format(str1, str2))
    print('        z = z * w // self._FIXED_1')
for n in range(len(loTerms)-1, len(loTerms)):
    str1 = '{0:#0{1}x}'.format(loTerms[n].num, loTermNumMaxLen)
    str2 = '{0:#0{1}x}'.format(loTerms[n].den, loTermDenMaxLen)
    str3 = '{0:0{1}d}' .format(2*n+1, loTermPosMaxLen)
    str4 = '{0:0{1}d}' .format(2*n+2, loTermNegMaxLen)
    print('        # add y^{} / {} - y^{} / {}'.format(str3, str3, str4, str4))
    print('        res += z * ({} - y) // {}'.format(str1, str2))
print('')
print('        return res')

