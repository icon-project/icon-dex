from iconservice import *

from ..interfaces.abc_smart_token import ABCSmartToken
from ..irc_token.irc_token import IRCToken
from ..utility.token_holder import TokenHolder
from ..utility.utils import Utils

TAG = 'SmartToken'


class SmartToken(IRCToken, TokenHolder, ABCSmartToken):
    _VERSION = '0.1'

    @eventlog
    def NewSmartToken(self, _token: 'Address'):
        pass

    @eventlog
    def Issuance(self, _amount: int):
        pass

    @eventlog
    def Destruction(self, _amount: int):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._version = VarDB('version', db, value_type=str)
        self._transfer_possibility = VarDB('transfer_possibility', db, value_type=bool)

    def on_install(self, _name: str, _symbol: str, _initialSupply: int, _decimals: int) -> None:
        IRCToken.on_install(self, _name, _symbol, _initialSupply, _decimals)
        TokenHolder.on_install(self)

        self._version.set(self._VERSION)
        self._transfer_possibility.set(True)

        self.NewSmartToken(self.address)

    def on_update(self) -> None:
        IRCToken.on_update(self)
        TokenHolder.on_update(self)

    def check_transfer_possibility(self):
        if not self._transfer_possibility.get():
            revert("This smart token cannot transfer")

    @external
    def disableTransfer(self, _disable: bool) -> None:
        self.owner_only()
        self._transfer_possibility.set(not _disable)

    @external(readonly=True)
    def getSmartTokenVersion(self) -> str:
        return self._version.get()

    @external(readonly=True)
    def getTransferPossibility(self) -> bool:
        return self._transfer_possibility.get()

    @external
    def issue(self, _to: Address, _amount: int) -> None:
        Utils.check_positive_value(_amount)
        self.owner_only()
        Utils.check_valid_address(_to)
        Utils.check_not_this(self.address, _to)

        self._balances[_to] += _amount
        total_supply = self._total_supply.get()
        self._total_supply.set(total_supply + _amount)

        self.Issuance(_amount)
        self.Transfer(self.address, _to, _amount, b'None')

    @external
    def destroy(self, _from: Address, _amount: int) -> None:
        Utils.check_positive_value(_amount)
        if self._balances[_from] < _amount:
            revert("Out of balance")
        if not self.msg.sender == _from and not self.msg.sender == self._owner.get():
            revert("You are not token holder or smart token owner")

        self._balances[_from] -= _amount
        total_supply = self._total_supply.get()
        self._total_supply.set(total_supply - _amount)

        self.Destruction(_amount)
        self.Transfer(_from, self.address, _amount, b'None')

    @external
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        self.check_transfer_possibility()
        IRCToken.transfer(self, _to, _value, _data)
