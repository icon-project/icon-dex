from iconservice import *


# noinspection PyPep8Naming
class ABCBancorNetwork(ABC):
    """
    Bancor Network interface
    """

    @abstractmethod
    def convert(self, _path: list, _amount: int, _minReturn) -> int:
        """converts the token to any other token in the bancor network by following
        a predefined conversion path and transfers the result tokens back to the sender
        note that the converter should already own the source tokens

        :param _path: conversion path, see conversion path format above
        :param _amount: amount to convert from (in the initial source token)
        :param _minReturn: if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :return: tokens issued in return
        """
        pass

    @abstractmethod
    def convertFor(self, _path: list, _amount: int, _minReturn: int, _for: 'Address') -> int:
        """converts the token to any other token in the bancor network by following
        a predefined conversion path and transfers the result tokens to a target account
        note that the converter should already own the source tokens

        :param _path: conversion path, see conversion path format above
        :param _amount: amount to convert from (in the initial source token)
        :param _minReturn: if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :param _for: account that will receive the conversion result
        :return: tokens issued in return
        """
        pass

    @abstractmethod
    def convertForPrioritized(self, _path: list, _amount: int, _minReturn: int, _for: 'Address', _block: int, _v: int,
                              _r: bytes, _s: bytes) -> int:
        """converts the token to any other token in the bancor network
        by following a predefined conversion path and transfers the result
        tokens to a target account.
        this version of the function also allows the verified signer
        to bypass the universal gas price limit.
        note that the converter should already own the source tokens


        :param _path: conversion path, see conversion path format above
        :param _amount: amount to convert from (in the initial source token)
        :param _minReturn: if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :param _for: account that will receive the conversion result
        :param _block: if the current block exceeded the given parameter - it is cancelled
        :param _v: (signature[128:130]) associated with the signer address and helps to validate if the signature is legit
        :param _r: (signature[0:64]) associated with the signer address and helps to validate if the signature is legit
        :param _s: (signature[64:128]) associated with the signer address and helps to validate if the signature is legit
        :return: tokens issued in return
        """
        pass


