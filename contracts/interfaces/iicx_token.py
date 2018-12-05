from iconservice import *
from .iirc_token import IIRCToken, IRCTokenInterface
from .itoken_holder import ITokenHolder, TokenHolderInterface


# noinspection PyPep8Naming
class IIcxToken(IIRCToken, ITokenHolder):
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


class IcxTokenInterface(IRCTokenInterface, TokenHolderInterface, IIcxToken):
    @interface
    def deposit(self) -> None:
        pass

    @interface
    def withdraw(self, _amount: int) -> None:
        pass

    @interface
    def withdrawTo(self, _amount: int, _to: 'Address') -> None:
        pass
