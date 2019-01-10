from iconservice import *


class Utils:
    @staticmethod
    def check_positive_value(amount: int):
        if not amount > 0:
            revert("Amount should be greater than 0")

    @staticmethod
    def check_valid_address(address: 'Address'):
        if not Utils.is_valid_address(address):
            # todo: write revert message
            revert("")

    @staticmethod
    def check_not_this(score_address: 'Address', address: 'Address'):
        if score_address == address:
            # todo: write revert message
            revert("")

    @staticmethod
    def require(condition: bool, revert_message=None):
        """
        Checks the input condition is satisfied. If not satisfied reverts.

        :param condition: condition to check
        :param revert_message: (Optional) revert message
        """
        if not condition:
            revert(revert_message)

    @staticmethod
    def is_valid_address(address: 'Address'):
        return address is not None and address != ZERO_SCORE_ADDRESS
