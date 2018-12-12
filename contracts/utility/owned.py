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
