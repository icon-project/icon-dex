from iconservice import *

from ..interfaces.abc_irc_token import ABCIRCToken
from ..interfaces.abc_token_holder import ABCTokenHolder
from ..utility.proxy_score import ProxyScore
from .owned import Owned
from .utils import Utils


class TokenHolder(Owned, ABCTokenHolder):
    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)

    def on_install(self) -> None:
        Owned.on_install(self)

    def on_update(self) -> None:
        Owned.on_update(self)

    @external
    def withdrawTokens(self, _token: 'Address', _to: 'Address', _amount: int) -> None:
        self.owner_only()
        Utils.check_positive_value(_amount)
        Utils.check_not_this(self.address, _to)
        Utils.check_valid_address(_to)

        irc_token_score = self.create_interface_score(_token, ProxyScore(ABCIRCToken))
        irc_token_score.transfer(_to, _amount)
