from auto_generate.common.functions import get_coefficients
from auto_generate.common.functions import get_max_exp_array
from auto_generate.common.functions import get_max_val_array
from auto_generate.common.constants import NUM_OF_COEFFICIENTS
from auto_generate.common.constants import MIN_PRECISION
from auto_generate.common.constants import MAX_PRECISION

coefficients = get_coefficients(NUM_OF_COEFFICIENTS)
maxExpArray = get_max_exp_array(coefficients,MAX_PRECISION+1)
maxValArray = get_max_val_array(coefficients,maxExpArray)


print('module.exports.MIN_PRECISION = {};'.format(MIN_PRECISION))
print('module.exports.MAX_PRECISION = {};'.format(MAX_PRECISION))


print('module.exports.maxExpArray = [')
for precision in range(len(maxExpArray)):
    print('    /* {:3d} */    \'0x{:x}\','.format(precision,maxExpArray[precision]))
print('];')


print('module.exports.maxValArray = [')
for precision in range(len(maxValArray)):
    print('    /* {:3d} */    \'0x{:x}\','.format(precision,maxValArray[precision]))
print('];')
