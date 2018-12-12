from iconservice import *


# noinspection PyPep8Naming
class ABCConverter(ABC):
    """
    Converter interface
    """

    @abstractmethod
    def getReturn(self, _fromToken: 'Address', _toToken: 'Address', _amount: int) -> dict:
        """
        Returns the expected return for converting a specific amount of _fromToken to _toToken

        :param _fromToken: address of IRC2 token to convert from
        :param _toToken: address of IRC2 token to convert to
        :param _amount: amount to convert, in fromToken
        :return: expected conversion return amount and conversion fee, in dict
        """
        pass

    @abstractmethod
    def convert(self,
                _fromToken: 'Address', _toToken: 'Address', _amount: int, _minReturn: int) -> int:
        """
        Converts a specific amount of _fromToken to _toToken

        :param _fromToken: address of IRC2 token to convert from
        :param _toToken: address of IRC2 token to convert to
        :param _amount: amount to convert, in fromToken
        :param _minReturn: if the conversion results in an amount smaller than the minimum return
        - it is cancelled, must be nonzero
        :return: conversion return amount
        """
        pass

    @abstractmethod
    def getConversionWhitelist(self) -> 'Address':
        """
        Returns an address of whitelist contract with list of addresses that are allowed to use
        the converter

        :return: address of whitelist contract
        """
        pass

    @abstractmethod
    def getConversionFee(self) -> int:
        """
        Returns current conversion fee, represented in ppm, 0...maxConversionFee

        :return: current conversion fee
        """
        pass

    @abstractmethod
    def getConnector(self, _address: 'Address') -> dict:
        """
        Returns connector information

        :param _address: connector token address
        :return: connector information, in dict
        """
        pass

    @abstractmethod
    def getConnectorBalance(self, _connectorToken: 'Address') -> int:
        """
        Returns the connector's virtual balance if one is defined,
        otherwise returns the actual balance

        :param _connectorToken: connector token address
        :return: connector balance
        """
        pass
