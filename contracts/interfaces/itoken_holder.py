from iconservice import *
from .iowned import IOwned, OwnedInterface


# noinspection PyPep8Naming
class ITokenHolder(IOwned):
    """
    TokenHolder interface
    """

    @abstractmethod
    def withdrawTokens(self, _token: 'Address', _to: 'Address', _amount: int) -> None:
        """
        withdraws tokens held by the contract and sends them to an account
        can only be called by the owner

        :param _token: IRC token contract address
        :param _to: account to receive the new amount
        :param _amount: amount to withdraw
        :return:
        """
        pass


class TokenHolderInterface(OwnedInterface, ITokenHolder):
    @interface
    def withdrawTokens(self, _token: 'Address', _to: 'Address', _amount: int) -> None:
        pass
