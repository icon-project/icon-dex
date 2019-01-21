from decimal import Decimal, getcontext


getcontext().prec = 80 # 78 digits for a maximum of 2^256-1, and 2 more digits for after the decimal point


def calculate_purchase_return(supply, balance, weight, amount):
    return Decimal(supply)*((1+Decimal(amount)/Decimal(balance))**(Decimal(weight)/1000000)-1)


def calculate_sale_return(supply, balance, weight, amount):
    return Decimal(balance)*(1-(1-Decimal(amount)/Decimal(supply))**(1000000/Decimal(weight)))


def power(baseN, baseD, expN, expD, precision):
    return (Decimal(baseN)/Decimal(baseD))**(Decimal(expN)/Decimal(expD))*2**precision
