from iconservice import *
from .abc_irc_token import ABCIRCToken
from .abc_token_holder import ABCTokenHolder


# noinspection PyPep8Naming
class ABCIcxToken(ABCIRCToken, ABCTokenHolder):
    """
    IcxToken interface
    """

    @abstractmethod
    def deposit(self) -> None:
        """
        Deposit ICX in the account.
        """
        pass

    @abstractmethod
    def withdraw(self, _amount: int) -> None:
        """
        Withdraw ICX from th account

        :param _amount: amount of ICX to withdraw
        :return:
        """
        pass

    @abstractmethod
    def withdrawTo(self, _amount: int, _to: 'Address') -> None:
        """
        Withdraw ICX from the account to a target account(_to)

        :param _amount: amount of ICX to withdraw
        :param _to: account to receive the ether
        :return:
        """
        pass
