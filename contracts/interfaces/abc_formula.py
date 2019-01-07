from iconservice import *


# noinspection PyPep8Naming
class ABCFormula(ABC):
    """
    Formula interface
    """
    @abstractmethod
    def calculatePurchaseReturn(self,
                                  _supply: int,
                                  _connector_balance: int,
                                  _connector_weight: int,
                                  _deposit_amount: int) -> int:
        """
        Given a token supply, connector balance, weight and a deposit amount (in the connector token),
        calculates the return for a given conversion (in the main token)

        Formula:
        Return = _supply * ((1 + _depositAmount / _connectorBalance) ^ (_connectorWeight / 1000000) - 1)

        :param _supply: token total supply
        :param _connector_balance: total connector balance
        :param _connector_weight: connector weight, represented in ppm, 1-1000000
        :param _deposit_amount: deposit amount, in connector token
        :return: purchase return amount
        """
        pass

    @abstractmethod
    def calculateSaleReturn(self,
                              _supply: int,
                              _connector_balance: int,
                              _connector_weight: int,
                              _sell_amount: int) -> int:
        """
        Given a token supply, connector balance, weight and a sell amount (in the main token),
        calculates the return for a given conversion (in the connector token)

        Formula:
        Return = _connectorBalance * (1 - (1 - _sellAmount / _supply) ^ (1 / (_connectorWeight / 1000000)))

        :param _supply: token total supply
        :param _connector_balance: total connector
        :param _connector_weight: constant connector Weight, represented in ppm, 1-1000000
        :param _sell_amount: sell amount, in the token itself
        :return: sale return amount
        """
        pass

    @abstractmethod
    def calculateCrossConnectorReturn(self,
                                         _from_connector_balance: int,
                                         _from_connector_weight: int,
                                         _to_connector_balance: int,
                                         _to_connector_weight: int,
                                         _amount: int) -> int:
        """
        Given two connector balances/weights and a sell amount (in the first connector token),
        calculates the return for a conversion from the first connector token to the second connector token (in the second connector token)

        Formula:
        Return = _toConnectorBalance * (1 - (_fromConnectorBalance / (_fromConnectorBalance + _amount)) ^ (_fromConnectorWeight / _toConnectorWeight))

        :param _from_connector_balance: input connector balance
        :param _from_connector_weight: input connector weight, represented in ppm, 1-1000000
        :param _to_connector_balance: output connector balance
        :param _to_connector_weight: output connector weight, represented in ppm, 1-1000000
        :param _amount: input connector amount
        :return: second connector amount
        """
        pass
