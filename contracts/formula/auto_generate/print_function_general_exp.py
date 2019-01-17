from contracts.formula.auto_generate.common.functions import get_coefficients
from contracts.formula.auto_generate.common.constants import NUM_OF_COEFFICIENTS


coefficients = get_coefficients(NUM_OF_COEFFICIENTS)


valueMaxLen = len(hex(coefficients[1]))
indexMaxLen = len(str(len(coefficients)))


print('        xi = _x')
print('        res = 0')
for i in range(1, len(coefficients)):
    print('        # add x^{1:0{2}d} * ({0:0{2}d}! / {1:0{2}d}!)'.format(len(coefficients), i + 1, indexMaxLen))
    print('        xi = (xi * _x) >> _precision')
    print('        res += xi * {0:#0{1}x}'.format(coefficients[i], valueMaxLen))
print('')
print('        # divide by {}! and then add x^1 / 1! + x^0 / 0!'.format(len(coefficients)))
print('        return res // 0x{:x} + _x + (self._ONE << _precision)'.format(coefficients[0]))
