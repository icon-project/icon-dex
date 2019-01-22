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

from decimal import Decimal, getcontext

getcontext().prec = 80  # 78 digits for a maximum of 2^256-1, and 2 more digits for after the decimal point


def calculate_purchase_return(supply, balance, weight, amount):
    return Decimal(supply)*((1+Decimal(amount)/Decimal(balance))**(Decimal(weight)/1000000)-1)


def calculate_sale_return(supply, balance, weight, amount):
    return Decimal(balance)*(1-(1-Decimal(amount)/Decimal(supply))**(1000000/Decimal(weight)))


def power(baseN, baseD, expN, expD, precision):
    return (Decimal(baseN)/Decimal(baseD))**(Decimal(expN)/Decimal(expD))*2**precision
