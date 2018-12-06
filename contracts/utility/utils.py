from iconservice import *


class Utils:
    @staticmethod
    def greater_than_zero(amount: int):
        if not amount > 0:
            revert("amount should be greater than 0")

    @staticmethod
    def valid_address(address: 'Address'):
        if address == ZERO_SCORE_ADDRESS:
            revert("")

    @staticmethod
    def not_this(score_address: 'Address', address: 'Address'):
        if score_address == address:
            revert("")
