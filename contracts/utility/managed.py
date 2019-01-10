from iconservice import *

from contracts.utility.owned import Owned
from contracts.utility.utils import Utils


# noinspection PyPep8Naming
class Managed(Owned):
    """
    Provides support and utilities for contract management
    Note that a managed contract must also have an owner
    """

    @eventlog(indexed=2)
    def ManagerUpdate(self, _prevManager: 'Address', _newManager: 'Address'):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._manager = VarDB('manager', db, value_type=Address)
        self._new_manager = VarDB('new_manager', db, value_type=Address)

    def on_install(self) -> None:
        self._manager.set(self.msg.sender)
        self._new_manager.set(ZERO_SCORE_ADDRESS)

    def on_update(self) -> None:
        Owned.on_update(self)

    # allows execution by the manager only
    def require_manager_only(self):
        Utils.require(self.msg.sender == self._manager.get(), "Invalid manager")

    # allows execution by either the owner or the manager only
    def require_owner_or_manager_only(self):
        Utils.require(self.msg.sender == self._manager.get() or self.msg.sender == self.getOwner,
                      "Invalid sender")

    @external(readonly=True)
    def getManager(self) -> 'Address':
        return self._manager.get()

    @external(readonly=True)
    def getNewManager(self) -> 'Address':
        return self._new_manager.get()

    @external
    def transferManagement(self, _newManager: 'Address'):
        """
        allows transferring the contract management
        the new manager still needs to accept the transfer
        can only be called by the contract manager

        :param _newManager: new contract manager
        :return:
        """
        self.require_owner_or_manager_only()
        Utils.require(self._manager.get() != _newManager, "New manager is already manager")
        self._new_manager.set(_newManager)

    @external
    def acceptManagement(self):
        """
        used by a new manager to accept a management transfer
        """
        if self.msg.sender != self._new_manager.get():
            revert("You are not a new manager")
        prev_manager = self._manager.get()
        new_manager = self._new_manager.get()

        self.ManagerUpdate(prev_manager, new_manager)
        self._manager.set(new_manager)
        self._new_manager.set(ZERO_SCORE_ADDRESS)
