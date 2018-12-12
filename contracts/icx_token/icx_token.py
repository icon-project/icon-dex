from iconservice import *

from contracts.interfaces.abc_icx_token import ABCIcxToken
from contracts.irc_token.irc_token import IRCToken
from contracts.utility.token_holder import TokenHolder
from contracts.utility.utils import Utils

TAG = 'IcxToken'


class IcxToken(IRCToken, TokenHolder, ABCIcxToken):

    @eventlog
    def Issuance(self, _amount: int):
        pass

    @eventlog
    def Destruction(self, _amount: int):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        IRCToken.__init__(self, db)
        TokenHolder.__init__(self, db)

    def on_install(self) -> None:
        IRCToken.on_install(self, 'icx_token', 'ICX', 0, 18)
        TokenHolder.on_install(self)

    def on_update(self) -> None:
        IRCToken.on_update(self)
        TokenHolder.on_update(self)

    @payable
    def fallback(self):
        self.deposit()

    @payable
    @external
    def deposit(self):
        self._balances[self.msg.sender] += self.msg.value
        total_supply = self._total_supply.get()
        self._total_supply.set(total_supply + self.msg.value)

        self.Issuance(self.msg.value)
        self.Transfer(self.address, self.msg.sender, self.msg.value, b'None')

    @external
    def withdraw(self, _amount: int):
        self.withdrawTo(_amount, self.msg.sender)

    @external
    def withdrawTo(self, _amount: int, _to: 'Address'):
        Utils.check_amount_is_positive(_amount)
        if self._balances[self.msg.sender] < _amount:
            revert("Out of balance")

        self.icx.send(_to, _amount)
        self._balances[self.msg.sender] -= _amount
        total_supply = self._total_supply.get()
        self._total_supply.set(total_supply - _amount)

        self.Destruction(_amount)

    @external
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        Utils.not_this(self.address, _to)
        IRCToken.transfer(self, _to, _value, _data)
