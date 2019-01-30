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

from .abc_irc_token import ABCIRCToken
from .abc_token_holder import ABCTokenHolder


# noinspection PyPep8Naming
class ABCIcxToken(ABCIRCToken, ABCTokenHolder):
    """
    IcxToken interface
    """

    @abstractmethod
    def deposit(self) -> None:
        """
        Deposit ICX in the account.
        """
        pass

    @abstractmethod
    def withdraw(self, _amount: int) -> None:
        """
        Withdraw ICX from th account

        :param _amount: amount of ICX to withdraw
        :return:
        """
        pass

    @abstractmethod
    def withdrawTo(self, _amount: int, _to: 'Address') -> None:
        """
        Withdraw ICX from the account to a target account(_to)

        :param _amount: amount of ICX to withdraw
        :param _to: account to receive the ether
        :return:
        """
        pass
