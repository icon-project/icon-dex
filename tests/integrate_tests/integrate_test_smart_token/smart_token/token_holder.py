from iconservice import *

from .owned import Owned
from .utils import Utils
from .iirc_token import IRCTokenInterface


class TokenHolder(Owned):
    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)

    def on_install(self) -> None:
        Owned.on_install(self)

    def on_update(self) -> None:
        Owned.on_update(self)

    @external
    def withdrawTokens(self, _token: 'Address', _to: 'Address', _amount: int) -> None:
        Owned.owner_only(self)
        Utils.check_amount_is_positive(_amount)
        Utils.not_this(self.address, _to)
        Utils.valid_address(_to)

        irc_token_score = self.create_interface_score(_token, IRCTokenInterface)
        irc_token_score.transfer(_to, _amount)
