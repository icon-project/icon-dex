from iconservice import *
from .abc_owned import ABCOwned


# noinspection PyPep8Naming
class ABCTokenHolder(ABCOwned):
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
