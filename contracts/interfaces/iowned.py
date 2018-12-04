from iconservice import *


# noinspection PyPep8Naming
class IOwned(ABC):
    """
    Owned interface
    """

    @abstractmethod
    def owner(self) -> 'Address':
        """
        Return current SCORE owner

        :return:
        """
        pass

    @abstractmethod
    def transferOwnerShip(self, _newOwner: Address) -> None:
        """
        Allows transferring the contract ownership
        the new owner still needs to accept the transfer
        can only be called by the contract owner

        :param _newOwner: new contract owner
        :return:
        """
        pass

    @abstractmethod
    def acceptOwnerShip(self) -> None:
        """
        Used by a new owner to accept an ownership transfer

        :return:
        """
        pass
