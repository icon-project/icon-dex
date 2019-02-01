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
class ABCIRCToken(ABC):
    """
    IRCToken interface
    """

    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of a token

        :return:
        """
        pass

    @abstractmethod
    def symbol(self) -> str:
        """
        Returns the symbol of a token

        :return:
        """

        pass

    @abstractmethod
    def decimals(self) -> int:
        """
        Returns the decimals of a token

        :return:
        """

        pass

    @abstractmethod
    def totalSupply(self) -> int:
        """
        Returns the total supply of a token
        :return:
        """

        pass

    @abstractmethod
    def balanceOf(self, _owner: Address) -> int:
        """
        Returns the balance of an account

        :param _owner:
        :return:
        """

        pass

    @abstractmethod
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        """
        Transfer token to an account

        :param _to: an account to receive token
        :param _value: an value of token to send
        :param _data: bytes data
        :return:
        """
        pass
