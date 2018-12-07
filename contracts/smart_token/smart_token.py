from iconservice import *

from contracts.interfaces.ismart_token import ISmartToken
from contracts.irc_token.irc_token import IRCToken
from contracts.utility.token_holder import TokenHolder
from contracts.utility.utils import Utils

TAG = 'SmartToken'


class SmartToken(IRCToken, TokenHolder, ISmartToken):
    _VERSION = '0.1'

    @eventlog
    def NewSmartToken(self, _token: 'Address'):
        pass

    @eventlog
    def Issuance(self, _amount):
        pass

    @eventlog
    def Destruction(self, _amount):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        IRCToken.__init__(self, db)
        TokenHolder.__init__(self, db)

        self._version = VarDB('version', db, value_type=str)
        self._transfer_possibility = VarDB('transfer_possibility', db, value_type=bool)

    def on_install(self, _name: str, _symbol: str, _initialSupply: int, _decimals: int) -> None:
        IRCToken.on_install(self, _name, _symbol, _initialSupply, _decimals)
        TokenHolder.on_install(self)

        self._version.set(self._VERSION)
        self._transfer_possibility.set(False)

        self.NewSmartToken(self.address)

    def on_update(self) -> None:
        IRCToken.on_update(self)
        TokenHolder.on_update(self)

    def check_transfer_possibility(self):
        if not self._transfer_possibility:
            revert("this smart token cannot transfer")

    def disableTransfer(self, _disable: bool) -> None:
        self.owner_only()
        self._transfer_possibility.set(not _disable)

    @external(readonly=True)
    def get_transfer_possibility(self):
        return self._transfer_possibility.get()

    @external
    def issue(self, _to: Address, _amount: int) -> None:
        self.owner_only()
        Utils.valid_address(_to)
        Utils.not_this(_to)

        self._balances[_to] += _amount
        total_supply = self._total_supply.get()
        self._total_supply.set(total_supply + _amount)

        self.Issuance(_amount)
        self.Transfer(self.address, _to, _amount, b'None')

    @external
    def destroy(self, _from: Address, _amount: int) -> None:
        if not self.msg.sender == _from and not self.msg.sender == self._owner.get():
            revert("you cannot destroy token")

        self._balances[_from] -= _amount
        total_supply = self._total_supply.get()
        self._total_supply.set(total_supply - _amount)

        self.Destruction(_amount)
        self.Transfer(_from, self.address, _amount, b'None')
