# The minimum scaling factor is 2 ^ MIN_PRECISION
MIN_PRECISION = 32
# The maximum scaling factor is 2 ^ MAX_PRECISION
MAX_PRECISION = 127

# The number of binomial coefficients in function 'generalExp'
NUM_OF_COEFFICIENTS = 34


# The input to function 'optimalLog' must be smaller than e ^ LOG_MAX_HI_TERM_VAL
LOG_MAX_HI_TERM_VAL = 1
# Compute e ^ (LOG_MAX_HI_TERM_VAL / 2 ^ n) for n = 0 to LOG_NUM_OF_HI_TERMS
LOG_NUM_OF_HI_TERMS = 8

# The input to function 'optimalExp' must be smaller than 2 ^ EXP_MAX_HI_TERM_VAL
EXP_MAX_HI_TERM_VAL = 4
# Compute e ^ 2 ^ n for n = EXP_MAX_HI_TERM_VAL - EXP_NUM_OF_HI_TERMS to EXP_MAX_HI_TERM_VAL
EXP_NUM_OF_HI_TERMS = 7
