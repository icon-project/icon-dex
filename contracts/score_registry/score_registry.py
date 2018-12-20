from iconservice import *

from ..interfaces.abc_score_registry import ABCScoreRegistry
from ..utility.owned import Owned
from ..utility.utils import Utils

TAG = 'ScoreRegistry'


class ScoreRegistry(Owned, ABCScoreRegistry):

    @eventlog(indexed=1)
    def AddressUpdate(self, _contractName: str, _scoreAddress: 'Address'):
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
    def getAddressFromBytesName(self, _scoreName: bytes) -> 'Address':
        if self._score_address[_scoreName] is None:
            return ZERO_SCORE_ADDRESS
        else:
            return self._score_address[_scoreName]

    @external(readonly=True)
    def getAddressFromStringName(self, _scoreName: str) -> 'Address':
        score_name_bytes = _scoreName.encode(encoding='utf-8')
        if self._score_address[score_name_bytes] is None:
            return ZERO_SCORE_ADDRESS
        else:
            return self._score_address[score_name_bytes]

    @external(readonly=True)
    def getScoreIds(self) -> list:
        return [self.SCORE_FEATURES, self.SCORE_REGISTRY, self.BANCOR_NETWORK, self.BANCOR_FORMULA, self.BNT_TOKEN, self.BNT_CONVERTER]

    @external
    def registerAddress(self, _scoreName: str, _scoreAddress: 'Address'):
        self.owner_only()
        Utils.check_valid_address(_scoreAddress)
        if not _scoreAddress.is_contract:
            revert("only SCORE address can be registered")
        # todo: consider checking score name is included in score name ids

        score_name_bytes = _scoreName.encode(encoding='utf-8')
        self._score_address[score_name_bytes] = _scoreAddress

        self.AddressUpdate(_scoreName, _scoreAddress)

    @external
    def unregisterAddress(self, _scoreName: str):
        self.owner_only()
        score_name_bytes = _scoreName.encode(encoding='utf-8')
        if self._score_address[score_name_bytes] is None:
            revert("this score is not registered")

        del self._score_address[score_name_bytes]

        # todo: consider managing eventlog seperately
        self.AddressUpdate(_scoreName, ZERO_SCORE_ADDRESS)
