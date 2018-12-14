import unittest

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message

from contracts.icx_token.icx_token import IcxToken
from contracts.irc_token.irc_token import IRCToken
from contracts.utility.token_holder import TokenHolder
from tests import patch, ScorePatcher, create_db


# noinspection PyUnresolvedReferences
class TestIcxScore(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(IcxToken)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.icx_token = IcxToken(create_db(self.score_address))

        sender = Address.from_string("hx" + "2" * 40)
        with patch([(IconScoreBase, 'msg', Message(sender))]):
            self.icx_token.on_install()
            IRCToken.on_install.assert_called_with(self.icx_token, 'icx_token', 'ICX', 0, 18)
            TokenHolder.on_install.assert_called_with(self.icx_token)

    def tearDown(self):
        self.patcher.stop()

    def test_deposit(self):
        sender = Address.from_string("hx" + "2" * 40)
        value = 10

        with patch([(IconScoreBase, 'msg', Message(sender, value=value))]):
            before_balance = self.icx_token._balances[sender]
            before_total_supply = self.icx_token._total_supply.get()

            self.icx_token.deposit()
            self.assertEqual(value, self.icx_token._balances[sender] - before_balance)
            self.assertEqual(value, self.icx_token._total_supply.get() - before_total_supply)

            self.icx_token.Issuance.assert_called_with(value)
            self.icx_token.Transfer.assert_called_with(self.icx_token.address, sender, value, b'None')

    def test_withdrawTo(self):
        sender = Address.from_string("hx" + "2" * 40)
        to = Address.from_string("hx" + "3" * 40)

        self.icx_token._balances[sender] = 10
        self.icx_token._total_supply.set(10)

        with patch([(IconScoreBase, 'msg', Message(sender))]):
            # failure case: amount is minus value
            self.assertRaises(RevertException, self.icx_token.withdrawTo, -1, to)

            # failure case: test if the revert would be called when out of balance
            self.assertRaises(RevertException, self.icx_token.withdrawTo, 20, to)

            # success case: withdraw 10 token to 'to'
            self.icx_token.withdrawTo(10, to)
            self.icx_token.icx.transfer.assert_called_with(to, 10)

            self.assertEqual(0, self.icx_token._balances[sender])
            self.assertEqual(0, self.icx_token._total_supply.get())
            self.icx_token.Destruction.assert_called_with(10)

    def test_transfer(self):
        sender = Address.from_string("hx" + "2" * 40)
        # failure case: transfer token to this score (should raise error)
        with patch([(IconScoreBase, 'msg', Message(sender))]):
            self.assertRaises(RevertException, self.icx_token.transfer, self.score_address, 10)
            IRCToken.transfer.assert_not_called()

        # success case: send 10 token to other
        token_receiver = Address.from_string("hx" + "4" * 40)
        self.icx_token.transfer(token_receiver, 10)

        IRCToken.transfer.assert_called_with(self.icx_token, token_receiver, 10, None)

