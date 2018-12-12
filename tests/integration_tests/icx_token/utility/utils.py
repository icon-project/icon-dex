from iconservice import *


class Utils:
    @staticmethod
    def check_amount_is_positive(amount: int):
        if not amount > 0:
            revert("Amount should be greater than 0")

    @staticmethod
    def valid_address(address: 'Address'):
        if address == ZERO_SCORE_ADDRESS:
            # todo: write revert message
            revert("")

    @staticmethod
    def not_this(score_address: 'Address', address: 'Address'):
        if score_address == address:
            # todo: write revert message
            revert("")

