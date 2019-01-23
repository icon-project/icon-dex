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


# noinspection PyPep8Naming
class ABCNetwork(ABC):
    """
    Network interface
    """

    @abstractmethod
    def convert(self, _path: list, _amount: int, _minReturn) -> int:
        """
        Converts the token to any other token in the bancor network by following
        a predefined conversion path and transfers the result tokens back to the sender
        note that the converter should already own the source tokens

        :param _path: conversion path, see conversion path format above
        :param _amount: amount to convert from (in the initial source token)
        :param _minReturn: if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :return: tokens issued in return
        """
        pass

    @abstractmethod
    def convertFor(self, _path: list, _amount: int, _minReturn: int, _for: 'Address') -> int:
        """
        Converts the token to any other token in the bancor network by following
        a predefined conversion path and transfers the result tokens to a target account
        note that the converter should already own the source tokens

        :param _path: conversion path, see conversion path format above
        :param _amount: amount to convert from (in the initial source token)
        :param _minReturn: if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :param _for: account that will receive the conversion result
        :return: tokens issued in return
        """
        pass
