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
    def getAddress(self, _scoreName: str) -> 'Address':
        if self._score_address[_scoreName] is None:
            return ZERO_SCORE_ADDRESS
        else:
            return self._score_address[_scoreName]

    @external(readonly=True)
    def getScoreIds(self) -> list:
        return self.SCORE_KEYS

    @external
    def registerAddress(self, _scoreName: str, _scoreAddress: 'Address'):
        self.owner_only()
        Utils.check_valid_address(_scoreAddress)
        if not _scoreAddress.is_contract:
            revert("only SCORE address can be registered")
        if _scoreName not in self.SCORE_KEYS:
            revert(f"_scoreName is not in the score key list: {_scoreName}")

        self._score_address[_scoreName] = _scoreAddress
        self.AddressUpdate(_scoreName, _scoreAddress)

    @external
    def unregisterAddress(self, _scoreName: str):
        self.owner_only()
        if self._score_address[_scoreName] is None:
            revert("this score is not registered")

        del self._score_address[_scoreName]
        self.AddressUpdate(_scoreName, ZERO_SCORE_ADDRESS)
