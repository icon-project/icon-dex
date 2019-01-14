from iconservice import *

from contracts.interfaces.abc_smart_token import ABCSmartToken
from contracts.utility.proxy_score import ProxyScore
from contracts.utility.storage import Storage
from contracts.utility.token_holder import TokenHolder
from .utils import Utils

# interface SCORE of `SmartToken`
SmartToken = ProxyScore(ABCSmartToken)


# noinspection PyPep8Naming,PyMethodOverriding
class SmartTokenController(TokenHolder):
    """
    Once it accepts ownership of the token, it becomes the token's sole controller
    that can execute any of its functions.

    The smart token must be set on construction and cannot be changed afterwards.
    Wrappers are provided (as opposed to a single 'execute' function)
    for each of the token's functions, for easier access.

    Note that the controller can transfer token ownership to a new controller that
    doesn't allow executing any function on the token, for a trustless solution.
    Doing that will also remove the owner's ability to upgrade the controller.
    """

    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)
        self.storage = Storage(db)
        self.storage.add_fields([('token', VarDB, Address)])

    def on_install(self, _token: 'Address') -> None:
        Utils.check_valid_address(_token)
        TokenHolder.on_install(self)
        self.storage.token = _token

    def on_update(self) -> None:
        TokenHolder.on_update(self)

    def is_active(self) -> bool:
        """
        returns whether the controller is active
        :return: True if the controller active
        """
        smart_token = self.create_interface_score(self.storage.token, SmartToken)
        return smart_token.getOwner() == self.address

    def require_active(self):
        """
        ensures that the controller is the token's owner
        """
        Utils.require(self.is_active())

    def require_inactive(self):
        """
        ensures that the controller is not the token's owner
        """
        Utils.require(not self.is_active())

    @external
    def transferTokenOwnership(self, _newOwner: Address) -> None:
        """
        allows transferring the token ownership the new owner needs to accept the transfer
        can only be called by the contract owner

        :param _newOwner: new token owner
        """
        self.owner_only()
        smart_token = self.create_interface_score(self.storage.token, SmartToken)
        smart_token.transferOwnerShip(_newOwner)

    @external
    def acceptTokenOwnership(self) -> None:
        """
        used by a new owner to accept a token ownership transfer
        can only be called by the contract owner
        """
        self.owner_only()
        smart_token = self.create_interface_score(self.storage.token, SmartToken)
        smart_token.acceptOwnerShip()

    @external
    def disableTokenTransfers(self, _disable: bool) -> None:
        """
        disables/enables token transfers
        can only be called by the contract owner

        :param _disable: true to disable transfers, false to enable them
        """
        self.owner_only()
        smart_token = self.create_interface_score(self.storage.token, SmartToken)
        smart_token.disableTransfer(_disable)

    @external
    def withdrawFromToken(self, _token: Address, _to: Address, _amount: int) -> None:
        """
        withdraws tokens held by the controller and sends them to an account
        can only be called by the owner

        :param _token: token contract address
        :param _to: account to receive the new amount
        :param _amount: amount to withdraw
        """
        self.owner_only()
        smart_token = self.create_interface_score(self.storage.token, SmartToken)
        smart_token.withdrawTokens(_token, _to, _amount)
