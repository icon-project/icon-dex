from auto_generate.common.functions import get_coefficients
from auto_generate.common.functions import get_max_exp_array
from auto_generate.common.constants import NUM_OF_COEFFICIENTS
from auto_generate.common.constants import MIN_PRECISION
from auto_generate.common.constants import MAX_PRECISION


coefficients = get_coefficients(NUM_OF_COEFFICIENTS)
max_exp_array = get_max_exp_array(coefficients, MAX_PRECISION+1)
max_exp_array_shl = [((max_exp_array[precision]+1) << (MAX_PRECISION-precision))-1
                     for precision in range(len(max_exp_array))]

_len = len(hex(max_exp_array_shl[0]))

print('    _max_exp_array = [None] * {}'.format(len(max_exp_array)))
for precision in range(len(max_exp_array)):
    prefix = '' if MIN_PRECISION <= precision <= MAX_PRECISION else '# '
    print('    {0:s}_max_exp_array[{1:d}] = {2:#0{3}x}'.format(prefix, precision, max_exp_array_shl[precision], _len))

