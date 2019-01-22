from iconservice import *


# noinspection PyPep8Naming
class ABCFormula(ABC):
    """
    Formula interface
    """
    @abstractmethod
    def calculate_purchase_return(self,
                                  supply: int,
                                  connector_balance: int,
                                  connector_weight: int,
                                  deposit_amount: int) -> int:
        """
        Given a token supply, connector balance, weight and a deposit amount (in the connector token),
        calculates the return for a given conversion (in the main token)

        Formula:
        Return = supply * ((1 + deposit_amount / connector_balance) ^ (connector_weight / 1000000) - 1)

        :param supply: token total supply
        :param connector_balance: total connector balance
        :param connector_weight: connector weight, represented in ppm, 1-1000000
        :param deposit_amount: deposit amount, in connector token
        :return: purchase return amount
        """
        pass

    @abstractmethod
    def calculate_sale_return(self,
                              supply: int,
                              connector_balance: int,
                              connector_weight: int,
                              sell_amount: int) -> int:
        """
        Given a token supply, connector balance, weight and a sell amount (in the main token),
        calculates the return for a given conversion (in the connector token)

        Formula:
        Return = connector_balance * (1 - (1 - sell_amount / supply) ^ (1 / (connector_weight / 1000000)))

        :param supply: token total supply
        :param connector_balance: total connector
        :param connector_weight: constant connector Weight, represented in ppm, 1-1000000
        :param sell_amount: sell amount, in the token itself
        :return: sale return amount
        """
        pass

    @abstractmethod
    def calculate_cross_connector_return(self,
                                         from_connector_balance: int,
                                         from_connector_weight: int,
                                         to_connector_balance: int,
                                         to_connector_weight: int,
                                         amount: int) -> int:
        """
        Given two connector balances/weights and a sell amount (in the first connector token),
        calculates the return for a conversion from the first connector token to the second connector token (in the second connector token)

        Formula:
        Return = to_connector_balance * (1 - (from_connector_balance / (from_connector_balance + amount)) ^ (from_connector_weight / to_connector_weight))

        :param from_connector_balance: input connector balance
        :param from_connector_weight: input connector weight, represented in ppm, 1-1000000
        :param to_connector_balance: output connector balance
        :param to_connector_weight: output connector weight, represented in ppm, 1-1000000
        :param amount: input connector amount
        :return: second connector amount
        """
        pass
