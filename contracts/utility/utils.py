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

from iconservice import *


def require_positive_value(amount: int):
    require(amount > 0, "Amount should be greater than 0")


def require_valid_address(address: 'Address'):
    # todo: write revert message
    require(is_valid_address(address), "")


def require_not_this(score_address: 'Address', address: 'Address'):
    # todo: write revert message
    require(score_address != address, "")


def require(condition: bool, revert_message=None):
    """
    Checks the input condition is satisfied. If not satisfied reverts.

    :param condition: condition to check
    :param revert_message: (Optional) revert message
    """
    if not condition:
        revert(revert_message)


def is_valid_address(address: 'Address'):
    return address is not None and address != ZERO_SCORE_ADDRESS


def safe_sub(_x: int, _y: int) -> int:
    """Returns the difference of _x minus _y, asserts if the subtraction results in a negative number

    :param _x: minuend
    :param _y: subtrahend
    :return: difference
    """
    if _x < _y:
        revert("Difference between two numbers should be positive")
    return _x - _y
