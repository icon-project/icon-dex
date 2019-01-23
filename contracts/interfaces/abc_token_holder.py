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
from .abc_owned import ABCOwned


# noinspection PyPep8Naming
class ABCTokenHolder(ABCOwned):
    """
    TokenHolder interface
    """

    @abstractmethod
    def withdrawTokens(self, _token: 'Address', _to: 'Address', _amount: int) -> None:
        """
        withdraws tokens held by the contract and sends them to an account
        can only be called by the owner

        :param _token: IRC token contract address
        :param _to: account to receive the new amount
        :param _amount: amount to withdraw
        :return:
        """
        pass
