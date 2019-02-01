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
class ABCScoreRegistry(ABC):
    """
    ScoreRegistry interface
    """
    # todo: consider administrating ids using Enum ( cannot import Enum class now )
    SCORE_REGISTRY = "ScoreRegistry"

    NETWORK = "Network"

    SCORE_KEYS = [SCORE_REGISTRY, NETWORK]

    @abstractmethod
    def getAddress(self, _scoreName: bytes) -> Address:
        """
        Returns score address
        :param _scoreName:
        :return:
        """
        pass
