from iconservice import *


class Utils:
    @staticmethod
    def check_positive_value(amount: int):
        if not amount > 0:
            revert("Amount should be greater than 0")

    @staticmethod
    def check_valid_address(address: 'Address'):
        if address == ZERO_SCORE_ADDRESS:
            # todo: write revert message
            revert("")

    @staticmethod
    def check_not_this(score_address: 'Address', address: 'Address'):
        if score_address == address:
            # todo: write revert message
            revert("")

