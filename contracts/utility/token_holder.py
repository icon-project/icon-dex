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

from .owned import Owned
from .utils import *
from ..interfaces.abc_irc_token import ABCIRCToken
from ..interfaces.abc_token_holder import ABCTokenHolder
from ..utility.proxy_score import ProxyScore


class TokenHolder(Owned, ABCTokenHolder):
    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)

    def on_install(self) -> None:
        Owned.on_install(self)

    def on_update(self) -> None:
        Owned.on_update(self)

    @external
    def withdrawTokens(self, _token: Address, _to: Address, _amount: int) -> None:
        self.require_owner_only()
        require_positive_value(_amount)
        require_not_this(self.address, _to)
        require_valid_address(_to)

        irc_token_score = self.create_interface_score(_token, ProxyScore(ABCIRCToken))
        irc_token_score.transfer(_to, _amount)
