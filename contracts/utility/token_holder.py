from iconservice import *

from .owned import Owned
from .utils import Utils
from contracts.interfaces.itoken_holder import ITokenHolder
from contracts.interfaces.iirc_token import IRCTokenInterface


class TokenHolder(Owned, ITokenHolder):
    def __init__(self, db: IconScoreDatabase):
        Owned.__init__(self, db)

    @external
    def withdrawTokens(self, _token: 'Address', _to: 'Address', _amount: int) -> None:
        Owned.owner_only(self)
        Utils.greater_than_zero(_amount)
        Utils.not_this(self.address, _to)
        Utils.valid_address(_to)

        irc_token_score = self.create_interface_score(_token, IRCTokenInterface)
        irc_token_score.transfer(_to, _amount)
