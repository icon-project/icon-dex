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

from ..interfaces.abc_score_registry import ABCScoreRegistry
from ..utility.owned import Owned
from ..utility.utils import *

TAG = 'ScoreRegistry'


# noinspection PyPep8Naming
class ScoreRegistry(Owned, ABCScoreRegistry):

    @eventlog(indexed=1)
    def AddressUpdate(self, _contractName: str, _scoreAddress: Address):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._score_address = DictDB("score_address", db, value_type=Address)

    def on_install(self) -> None:
        Owned.on_install(self)
        self.registerAddress(self.SCORE_REGISTRY, self.address)

    def on_update(self) -> None:
        Owned.on_update(self)

    @external(readonly=True)
    def getAddress(self, _scoreName: str) -> Address:
        if self._score_address[_scoreName] is None:
            return ZERO_SCORE_ADDRESS
        else:
            return self._score_address[_scoreName]

    @external(readonly=True)
    def getScoreIds(self) -> list:
        return self.SCORE_KEYS

    @external
    def registerAddress(self, _scoreName: str, _scoreAddress: Address):
        self.require_owner_only()
        require_valid_address(_scoreAddress)
        require(_scoreAddress.is_contract, "only SCORE address can be registered")
        require(_scoreName in self.SCORE_KEYS, f"_scoreName is not in the score key list: {_scoreName}")

        self._score_address[_scoreName] = _scoreAddress
        self.AddressUpdate(_scoreName, _scoreAddress)

    @external
    def unregisterAddress(self, _scoreName: str):
        self.require_owner_only()
        require(self._score_address[_scoreName] is not None, "this score is not registered")

        del self._score_address[_scoreName]
        self.AddressUpdate(_scoreName, ZERO_SCORE_ADDRESS)
