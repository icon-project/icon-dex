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

from .proxy_score import ProxyScore
from .token_holder import TokenHolder
from .utils import *
from ..interfaces.abc_smart_token import ABCSmartToken

# interface SCORE of `SmartToken`
SmartToken = ProxyScore(ABCSmartToken)


# noinspection PyPep8Naming,PyMethodOverriding
class SmartTokenController(TokenHolder):
    """
    Once it accepts ownership of the token, it becomes the token's sole controller
    that can execute any of its functions.

    The smart token must be set on construction and cannot be changed afterwards.
    Wrappers are provided (as opposed to a single 'execute' function)
    for each of the token's functions, for easier access.

    Note that the controller can transfer token ownership to a new controller that
    doesn't allow executing any function on the token, for a trustless solution.
    Doing that will also remove the owner's ability to upgrade the controller.
    """

    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)
        self._token = VarDB('token', db, Address)

    def on_install(self, _token: Address) -> None:
        require_valid_address(_token)
        TokenHolder.on_install(self)
        self._token.set(_token)

    def on_update(self) -> None:
        TokenHolder.on_update(self)

    def _is_active(self) -> bool:
        """
        returns whether the controller is active
        :return: True if the controller active
        """
        smart_token = self.create_interface_score(self._token.get(), SmartToken)
        return smart_token.getOwner() == self.address

    def _require_active(self):
        """
        ensures that the controller is the token's owner
        """
        require(self._is_active())

    def _require_inactive(self):
        """
        ensures that the controller is not the token's owner
        """
        require(not self._is_active())

    @external(readonly=True)
    def isActive(self) -> bool:
        """

        :return:
        """
        return self._is_active()

    @external
    def transferTokenOwnership(self, _newOwner: Address) -> None:
        """
        allows transferring the token ownership the new owner needs to accept the transfer
        can only be called by the contract owner

        :param _newOwner: new token owner
        """
        self.require_owner_only()
        smart_token = self.create_interface_score(self._token.get(), SmartToken)
        smart_token.transferOwnerShip(_newOwner)

    @external
    def acceptTokenOwnership(self) -> None:
        """
        used by a new owner to accept a token ownership transfer
        can only be called by the contract owner
        """
        self.require_owner_only()
        smart_token = self.create_interface_score(self._token.get(), SmartToken)
        smart_token.acceptOwnerShip()

    @external
    def disableTokenTransfers(self, _disable: bool) -> None:
        """
        disables/enables token transfers
        can only be called by the contract owner

        :param _disable: true to disable transfers, false to enable them
        """
        self.require_owner_only()
        smart_token = self.create_interface_score(self._token.get(), SmartToken)
        smart_token.disableTransfer(_disable)

    @external
    def withdrawFromToken(self, _token: Address, _to: Address, _amount: int) -> None:
        """
        withdraws tokens held by the controller and sends them to an account
        can only be called by the owner

        :param _token: token contract address
        :param _to: account to receive the new amount
        :param _amount: amount to withdraw
        """
        self.require_owner_only()
        smart_token = self.create_interface_score(self._token.get(), SmartToken)
        smart_token.withdrawTokens(_token, _to, _amount)

    @external(readonly=True)
    def getToken(self) -> Address:
        """
        Returns token address for the SCORE to manage

        :return: token address
        """
        return self._token.get()
