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
class ABCConverter(ABC):
    """
    Converter interface
    """

    @abstractmethod
    def getReturn(self, _fromToken: Address, _toToken: Address, _amount: int) -> dict:
        """
        Returns the expected return for converting a specific amount of _fromToken to _toToken

        :param _fromToken: address of IRC2 token to convert from
        :param _toToken: address of IRC2 token to convert to
        :param _amount: amount to convert, in fromToken
        :return: expected conversion return amount and conversion fee, in dict
            e.g.) {'amount': [INT], 'fee': [INT]}
        """
        pass

    @abstractmethod
    def getConversionFee(self) -> int:
        """
        Returns current conversion fee, represented in ppm, 0...maxConversionFee

        :return: current conversion fee
        """
        pass

    @abstractmethod
    def getConnector(self, _address: Address) -> dict:
        """
        Returns connector information

        :param _address: connector token address
        :return: connector information, in dict
        """
        pass

    @abstractmethod
    def getConnectorBalance(self, _connectorToken: Address) -> int:
        """
        Returns the connector's virtual balance if one is defined,
        otherwise returns the actual balance

        :param _connectorToken: connector token address
        :return: connector balance
        """
        pass

    @abstractmethod
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        """
        invoked when the contract receives tokens.
        if the data param is parsed as conversion format,
        token conversion is executed.
        conversion format is:
        ```
        {
            'toToken': [ADDRESS],
            'minReturn': [INT]
        }
        ```

        :param _from: token sender. should be network
        :param _value: amount of tokens
        :param _data: additional data
        """
        pass
