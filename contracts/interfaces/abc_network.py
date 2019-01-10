from iconservice import *


# noinspection PyPep8Naming
class ABCNetwork(ABC):
    """
    Network interface
    """

    @abstractmethod
    def convert(self, _path: list, _minReturn) -> int:
        """
        converts the token to any other token in the network by following
        a predefined conversion path and transfers the result tokens back to the sender
        note that the converter should already own the source tokens

        :param _path: conversion path, see conversion path format above
        :param _amount: amount to convert from (in the initial source token)
        :param _minReturn: if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :return: tokens issued in return
        """
        pass

    @abstractmethod
    def convertFor(self, _path: list, _minReturn: int, _for: 'Address') -> int:
        """
        converts the token to any other token in the network by following
        a predefined conversion path and transfers the result tokens to a target account
        note that the converter should already own the source tokens

        :param _path: conversion path, see conversion path format above
        :param _amount: amount to convert from (in the initial source token)
        :param _minReturn: if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :param _for: account that will receive the conversion result
        :return: tokens issued in return
        """
        pass
