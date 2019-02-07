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
class ABCOwned(ABC):
    """
    Owned interface
    """

    @abstractmethod
    def getOwner(self) -> Address:
        """
        Return current SCORE owner

        :return:
        """
        pass

    @abstractmethod
    def transferOwnerShip(self, _newOwner: Address) -> None:
        """
        Allows transferring the contract ownership
        the new owner still needs to accept the transfer
        can only be called by the contract owner

        :param _newOwner: new contract owner
        :return:
        """
        pass

    @abstractmethod
    def acceptOwnerShip(self) -> None:
        """
        Used by a new owner to accept an ownership transfer

        :return:
        """
        pass
