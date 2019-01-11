from auto_generate.common.functions import get_coefficients
from auto_generate.common.functions import get_max_exp_array
from auto_generate.common.functions import binary_search
from auto_generate.common.functions import general_exp
from auto_generate.common.functions import safe_mul
from auto_generate.common.constants import NUM_OF_COEFFICIENTS
from auto_generate.common.constants import MIN_PRECISION
from auto_generate.common.constants import MAX_PRECISION


NUM_OF_VALUES_PER_ROW = 4
assert (MAX_PRECISION+1) % NUM_OF_VALUES_PER_ROW == 0


def get_max_exp(_precision, factor):
    max_exp = maxExpArray[MIN_PRECISION]
    for p in range(MIN_PRECISION, _precision):
        max_exp = safe_mul(max_exp, factor) >> MAX_PRECISION
        general_exp(max_exp, coefficients, _precision)
    return max_exp


def assert_factor(factor):
    for _precision in range(MIN_PRECISION, MAX_PRECISION+1):
        get_max_exp(_precision, factor)


coefficients = get_coefficients(NUM_OF_COEFFICIENTS)
maxExpArray = get_max_exp_array(coefficients, MAX_PRECISION+1)
growthFactor = binary_search(assert_factor, {})
maxMaxExpLen = len('0x{:x}'.format(maxExpArray[-1]))


print('Max Exp Per Precision:')
formatString = '{:s}{:d}{:s}'.format('Precision = {:3d} | Max Exp = {:', maxMaxExpLen, 's} | Ratio = {:9.7f}')
for precision in range(MAX_PRECISION+1):
    maxExp = '0x{:x}'.format(maxExpArray[precision])
    ratio = maxExpArray[precision]/maxExpArray[precision-1] if precision > 0 else 0.0
    print(formatString.format(precision, maxExp, ratio))
print('')


print('max_exp_array = [')
formatString = '{:s}{:d}{:s}'.format('{:', maxMaxExpLen, 's},')
for i in range(len(maxExpArray)//NUM_OF_VALUES_PER_ROW):
    items = []
    for j in range(NUM_OF_VALUES_PER_ROW):
        items.append('0x{:x}'.format(maxExpArray[i*NUM_OF_VALUES_PER_ROW+j]))
    print('    '+''.join([formatString.format(item) for item in items]))
print(']\n')


print('Compute the values dynamically, using a growth-factor of 0x{:x} >> {:d}:'.format(growthFactor, MAX_PRECISION))
formatString = '{:s}{:d}{:s}{:d}{:s}'.format('Precision = {:3d} | Theoretical Max Exp = {:', maxMaxExpLen,
                                             's} | Practical Max Exp = {:', maxMaxExpLen, 's} | Difference = {:d}')
for precision in range(MIN_PRECISION, MAX_PRECISION+1):
    theoreticalMaxExp = maxExpArray[precision]
    practicalMaxExp = get_max_exp(precision, growthFactor)
    print(formatString.format(precision, '0x{:x}'.format(theoreticalMaxExp), '0x{:x}'.format(practicalMaxExp),
                              theoreticalMaxExp-practicalMaxExp))

