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

from math import factorial
from decimal import Decimal
from decimal import getcontext
from collections import namedtuple

from contracts.formula.auto_generate.common.functions import optimal_exp
from contracts.formula.auto_generate.common.constants import MAX_PRECISION
from contracts.formula.auto_generate.common.constants import EXP_MAX_HI_TERM_VAL
from contracts.formula.auto_generate.common.constants import EXP_NUM_OF_HI_TERMS


getcontext().prec = 100
FIXED_1 = (1 << MAX_PRECISION)


HiTerm = namedtuple('HiTerm', 'bit,num,den')
LoTerm = namedtuple('LoTerm', 'val,ind')


hiTerms = []
loTerms = []


top = int(Decimal(2**(0+EXP_MAX_HI_TERM_VAL-EXP_NUM_OF_HI_TERMS)).exp()*FIXED_1)-1
for n in range(EXP_NUM_OF_HI_TERMS+1):
    cur = Decimal(2**(n+EXP_MAX_HI_TERM_VAL-EXP_NUM_OF_HI_TERMS)).exp()
    den = int(((1 << 256)-1)/(cur*top))
    num = int(den*cur)
    top = top*num//den
    bit = (FIXED_1 << (n+EXP_MAX_HI_TERM_VAL))>>EXP_NUM_OF_HI_TERMS
    hiTerms.append(HiTerm(bit, num, den))


MAX_VAL = hiTerms[-1].bit-1
loTerms = [LoTerm(1, 1)]
res = optimal_exp(MAX_VAL, hiTerms, loTerms, FIXED_1)
while True:
    n = len(loTerms)+1
    val = factorial(n)
    loTermsNext = [LoTerm(val//factorial(i+1), i+1) for i in range(n)]
    resNext = optimal_exp(MAX_VAL, hiTerms, loTermsNext, FIXED_1)
    if res < resNext:
        res = resNext
        loTerms = loTermsNext
    else:
        break


hiTermBitMaxLen = len(hex(hiTerms[-1].bit))
hiTermNumMaxLen = len(hex(hiTerms[0].num))
hiTermDenMaxLen = len(hex(hiTerms[0].den))
loTermValMaxLen = len(hex(loTerms[+1].val))
loTermIndMaxLen = len(str(loTerms[-1].ind))


hiTermIndMin = EXP_MAX_HI_TERM_VAL-EXP_NUM_OF_HI_TERMS
hiTermIndMaxLen = max(len(str(EXP_MAX_HI_TERM_VAL-1)), len(str(EXP_MAX_HI_TERM_VAL-EXP_NUM_OF_HI_TERMS)))

print('        res = 0')
print('        # get the input modulo 2^({:+d})'.format(EXP_MAX_HI_TERM_VAL-EXP_NUM_OF_HI_TERMS))
print('        z = y = x % 0x{:x}'.format(hiTerms[0].bit))
for n in range(1, len(loTerms)):
    str1 = '{0:#0{1}x}'.format(loTerms[n].val, loTermValMaxLen)
    str2 = '{0:0{1}d}' .format(loTerms[n].ind, loTermIndMaxLen)
    str3 = '{0:0{1}d}' .format(len(loTerms), loTermIndMaxLen)
    str4 = '{0:0{1}d}' .format(loTerms[n].ind, loTermIndMaxLen)
    print('        # add y^{} * ({}! / {}!)'.format(str2, str3, str4))
    print('        z = z * y // self._FIXED_1')
    print('        res += z * {}'.format(str1))
print('        # divide by {}! and then add y^1 / 1! + y^0 / 0!'.format(len(loTerms)))
print('        res = res // 0x{:x} + y + self._FIXED_1'.format(loTerms[0].val))
print('')

for n in range(len(hiTerms)-1):
    str1 = '{0:#0{1}x}'.format(hiTerms[n].bit, hiTermBitMaxLen)
    str2 = '{0:#0{1}x}'.format(hiTerms[n].num, hiTermNumMaxLen)
    str3 = '{0:#0{1}x}'.format(hiTerms[n].den, hiTermDenMaxLen)
    str4 = '{0:+{1}d}' .format(hiTermIndMin+n, hiTermIndMaxLen)
    print('        # multiply by e^2^({})'.format(str4))
    print('        if (x & {}) != 0:'.format(str1))
    print('            res = res * {} // {}'.format(str2, str3))
print('')
print('        return res')
