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
class ABCSmartToken(ABCIRCToken, ABCTokenHolder):
    """
    ISmartToken interface
    """

    @abstractmethod
    def disableTransfer(self, _disable: bool) -> None:
        """
        Disables/enables transfers
        can only be called by the contract owner

        :param _disable: true to disable transfers, false to enable them
        :return:
        """
        pass

    @abstractmethod
    def issue(self, _to: Address, _amount: int) -> None:
        """
        Increases the token supply and sends the new tokens to an account
        can only be called by the contract owner

        :param _to: account to receive the new amount
        :param _amount: amount to increase the supply by
        :return:
        """
        pass

    @abstractmethod
    def destroy(self, _from: Address, _amount: int) -> None:
        """
        Removes tokens from an account and decreases the token supply
        can be called by the contract owner to destroy tokens from any account or by any holder to destroy tokens from his/her own account

        :param _from: account to remove the amount from
        :param _amount: amount to decrease the supply by
        :return:
        """
        pass
