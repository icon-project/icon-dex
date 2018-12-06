from iconservice import *
from contracts.interfaces.iowned import IOwned


class Owned(IconScoreBase, IOwned):
    _OWNER = 'owner'
    _NEW_OWNER = 'new_owner'

    @eventlog(indexed=2)
    def OwnerUpdate(self, _prevOwner: Address, _newOwner: Address):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        # initial IconScoreBase twice
        # todo: check the need of calling __init__ method of IconScoreBase
        self._owner = VarDB(self._OWNER, db, value_type=Address)
        self._new_owner = VarDB(self._NEW_OWNER, db, value_type=Address)
        self._owner.set(self.msg.sender)

    def on_install(self) -> None:
        # this class doesn't need to call IconScoreBase's on_install method
        pass

    def on_update(self) -> None:
        # this class doesn't need to call IconScoreBase's on_update method
        pass

    def owner_only(self):
        if self.msg.sender != self._owner.get():
            revert("Invalid owner")

    @external(readonly=True)
    def owner(self) -> 'Address':
        return self._owner.get()

    @external(readonly=True)
    def newOwner(self) -> 'Address':
        return self._new_owner.get()

    @external
    def transferOwnerShip(self, _newOwner: Address):
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
