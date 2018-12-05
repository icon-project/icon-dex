from iconservice import *


# noinspection PyPep8Naming
class IIRCToken(ABC):
    """
    IRCToken interface
    """

    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of a token

        :return:
        """
        pass

    @abstractmethod
    def symbol(self) -> str:
        """
        Returns the symbol of a token

        :return:
        """

        pass

    @abstractmethod
    def decimals(self) -> int:
        """
        Returns the decimals of a token

        :return:
        """

        pass

    @abstractmethod
    def totalSupply(self) -> int:
        """
        Returns the total supply of a token
        :return:
        """

        pass

    @abstractmethod
    def balanceOf(self, _owner: 'Address') -> int:
        """
        Returns the balance of an account

        :param _owner:
        :return:
        """

        pass

    @abstractmethod
    def transfer(self, _to: 'Address', _value: int, _data: bytes = None):
        """
        Transfer token to an account

        :param _to: an account to receive token
        :param _value: an value of token to send
        :param _data: bytes data
        :return:
        """
        pass


class IRCTokenInterface(InterfaceScore, IIRCToken):
    @interface
    def name(self) -> str:
        pass

    @interface
    def symbol(self) -> str:
        pass

    @interface
    def decimals(self) -> int:
        pass

    @interface
    def totalSupply(self) -> int:
        pass

    @interface
    def balanceOf(self, _owner: 'Address') -> int:
        pass

    @interface
    def transfer(self, _to: 'Address', _value: int, _data: bytes = None):
        pass
