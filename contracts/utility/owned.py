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

from ..interfaces.abc_owned import ABCOwned


class Owned(IconScoreBase, ABCOwned):

    @eventlog(indexed=2)
    def OwnerUpdate(self, _prevOwner: 'Address', _newOwner: 'Address'):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._owner = VarDB('prev_owner', db, value_type=Address)
        self._new_owner = VarDB('new_owner', db, value_type=Address)

    def on_install(self) -> None:
        self._owner.set(self.msg.sender)
        self._new_owner.set(ZERO_SCORE_ADDRESS)

    def on_update(self) -> None:
        IconScoreBase.on_update(self)

    def owner_only(self):
        if self.msg.sender != self._owner.get():
            revert("Invalid owner")

    @external(readonly=True)
    def getOwner(self) -> 'Address':
        return self._owner.get()

    @external(readonly=True)
    def getNewOwner(self) -> 'Address':
        return self._new_owner.get()

    @external
    def transferOwnerShip(self, _newOwner: 'Address'):
        self.owner_only()
        if _newOwner == self._owner.get():
            revert("New owner is already owner")
        self._new_owner.set(_newOwner)

    @external
    def acceptOwnerShip(self):
        if self.msg.sender != self._new_owner.get():
            revert("You are not a new owner")
        prev_owner = self._owner.get()
        new_owner = self._new_owner.get()

        self.OwnerUpdate(prev_owner, new_owner)
        self._owner.set(new_owner)
        self._new_owner.set(ZERO_SCORE_ADDRESS)
