from math import factorial


def get_coefficients(num_of_coefficients):
    max_factorial = factorial(num_of_coefficients - 1)
    return [max_factorial // factorial(i) for i in range(1, num_of_coefficients)]


def get_max_exp_array(coefficients, num_of_precisions):
    return [binary_search(general_exp, [coefficients, precision]) for precision in range(num_of_precisions)]


def get_max_val_array(coefficients, max_exp_array):
    return [general_exp(max_exp_array[precision], coefficients, precision) for precision in range(len(max_exp_array))]


def binary_search(func, args):
    lo = 0
    hi = (1 << 256)-1

    while lo+1 < hi:
        mid = (lo+hi)//2
        try:
            func(mid, *args)
            lo = mid
        except Exception:
            hi = mid

    try:
        func(hi, *args)
        return hi
    except Exception:
        func(lo, *args)
        return lo


def general_exp(x, coefficients, precision):
    xi = x
    res = 0
    for coefficient in coefficients[1:]:
        xi = safe_mul(xi, x) >> precision
        res = safe_add(res, safe_mul(xi, coefficient))
    return safe_add(safe_add(res // coefficients[0], x), 1 << precision)


def optimal_log(x, hi_terms, lo_terms, fixed1):
    res = 0
    for term in hi_terms[+1:]:
        if x >= term.exp:
            res = safe_add(res, term.val)
            x = safe_mul(x, fixed1) // term.exp
    z = y = safe_sub(x, fixed1)
    w = safe_mul(y, y) // fixed1
    for term in lo_terms[:-1]:
        res = safe_add(res, safe_mul(z, safe_sub(term.num, y)) // term.den)
        z = safe_mul(z, w) // fixed1
    res = safe_add(res, safe_mul(z, safe_sub(lo_terms[-1].num, y)) // lo_terms[-1].den)
    return res


def optimal_exp(x, hi_terms, lo_terms, fixed1):
    res = 0
    z = y = x % hi_terms[0].bit
    for term in lo_terms[+1:]:
        z = safe_mul(z, y) // fixed1
        res = safe_add(res, safe_mul(z, term.val))
    res = safe_add(safe_add(res // lo_terms[0].val, y), fixed1)
    for term in hi_terms[:-1]:
        if x & term.bit:
            res = safe_mul(res, term.num) // term.den
    return res


def safe_sub(x, y):
    assert (x - y) >= 0
    return x - y


def safe_add(x, y):
    assert (x + y) < (1 << 256)
    return x + y


def safe_mul(x, y):
    assert (x * y) < (1 << 256)
    return x * y


def safe_shl(x, y):
    assert (x << y) < (1 << 256)
    return x << y
