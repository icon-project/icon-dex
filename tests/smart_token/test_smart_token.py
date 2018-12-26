import unittest
from unittest.mock import Mock

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message
from contracts.irc_token.irc_token import IRCToken
from contracts.utility.token_holder import TokenHolder

from contracts.smart_token.smart_token import SmartToken
from tests import patch, ScorePatcher, create_db


# noinspection PyUnresolvedReferences
class TestSmartToken(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(SmartToken)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.smart_token = SmartToken(create_db(self.score_address))
        token_name = "test_token"
        token_symbol = "TST"
        token_supply = 100
        token_decimals = 18

        self.token_owner = Address.from_string("hx" + "2" * 40)
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            self.smart_token.on_install(token_name, token_symbol, token_supply, token_decimals)

            IRCToken.on_install.assert_called_with(self.smart_token, token_name, token_symbol, token_supply, token_decimals)
            TokenHolder.on_install.assert_called_with(self.smart_token)
            self.assertEqual(self.smart_token._VERSION, self.smart_token._version.get())
            self.assertEqual(True, self.smart_token._transfer_possibility.get())
            self.smart_token.NewSmartToken.assert_called_with(self.score_address)

    def tearDown(self):
        self.patcher.stop()

    def test_check_transfer_possibility(self):
        self.smart_token._transfer_possibility.set(True)
        self.smart_token.check_transfer_possibility()

        self.smart_token._transfer_possibility.set(False)
        self.assertRaises(RevertException, self.smart_token.check_transfer_possibility)

    def test_disableTransfer(self):
        self.smart_token._transfer_possibility.set(True)
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            self.smart_token.owner_only = Mock()

            self.smart_token.disableTransfer(True)
            self.smart_token.owner_only.assert_called()
            self.assertEqual(False, self.smart_token._transfer_possibility.get())

            self.smart_token.disableTransfer(False)
            self.smart_token.owner_only.assert_called()
            self.assertEqual(True, self.smart_token._transfer_possibility.get())

    def test_issue(self):
        token_receiver = Address.from_string("hx" + "3" * 40)

        # success_case: issue 10 token to public
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            before_balance = self.smart_token._balances[token_receiver]
            before_total_supply = self.smart_token._total_supply.get()

            self.smart_token.issue(token_receiver, 10)
            self.smart_token.owner_only.assert_called()
            self.assertEqual(before_balance + 10, self.smart_token._balances[token_receiver])
            self.assertEqual(before_total_supply + 10, self.smart_token._total_supply.get())

            self.smart_token.Issuance.assert_called_with(10)
            self.smart_token.Transfer.assert_called_with(self.score_address, token_receiver, 10, b'None')

        # failure_case: amount is under 0
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            minus_amount = -10
            self.assertRaises(RevertException, self.smart_token.issue, token_receiver, minus_amount)

        # failure_case: 'to' address is invalid
        to_address = ZERO_SCORE_ADDRESS
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            self.assertRaises(RevertException, self.smart_token.issue, to_address, 10)

    def test_destroy(self):
        token_holder = Address.from_string("hx" + "3" * 40)

        # owner setting
        self.smart_token._owner.set(self.token_owner)

        # increase 10 token to holder's balance
        self.smart_token._balances[token_holder] += 10
        # increase total supply according to token holder's balance
        self.smart_token._total_supply.set(self.smart_token._total_supply.get() + 10)

        before_balance = self.smart_token._balances[token_holder]
        before_total_supply = self.smart_token._total_supply.get()

        # failure case: amount is under 0
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            self.assertRaises(RevertException, self.smart_token.destroy, token_holder, -10)

        # failure case: amount is higher than token_holder's balance
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            self.assertRaises(RevertException, self.smart_token.destroy, token_holder, 20)

        # failure case: msg.sender is not 'from' nor the owner
        eoa_address = Address.from_string("hx" + "4" * 40)
        with patch([(IconScoreBase, 'msg', Message(eoa_address))]):
            self.assertRaises(RevertException, self.smart_token.destroy, token_holder, 10)

        # success case: token_owner destroy 5 tokens from token_holder
        with patch([(IconScoreBase, 'msg', Message(self.token_owner))]):
            destroy_amount = 5
            self.smart_token.destroy(token_holder, destroy_amount)

            self.assertEqual(before_balance - destroy_amount, self.smart_token._balances[token_holder])
            self.assertEqual(before_total_supply - destroy_amount, self.smart_token._total_supply.get())

            self.smart_token.Destruction.assert_called_with(destroy_amount)
            self.smart_token.Transfer.assert_called_with(token_holder, self.score_address, destroy_amount, b'None')

        # success case: token_holder destroy 5 their own token
        with patch([(IconScoreBase, 'msg', Message(token_holder))]):
            destroy_amount = 5
            before_balance = self.smart_token._balances[token_holder]
            before_total_supply = self.smart_token._total_supply.get()

            self.smart_token.destroy(token_holder, destroy_amount)

            self.assertEqual(before_balance - destroy_amount, self.smart_token._balances[token_holder])
            self.assertEqual(before_total_supply - destroy_amount, self.smart_token._total_supply.get())

            self.smart_token.Destruction.assert_called_with(destroy_amount)
            self.smart_token.Transfer.assert_called_with(token_holder, self.score_address, destroy_amount, b'None')

    def test_transfer(self):
        sender = Address.from_string("hx" + "2" * 40)
        token_receiver = Address.from_string("hx" + "3" * 40)

        # failure case: transfer tokens when transfer possibility is False
        with patch([(IconScoreBase, 'msg', Message(sender))]):
            self.smart_token._transfer_possibility.set(False)
            self.assertRaises(RevertException, self.smart_token.transfer, token_receiver, 10)
            IRCToken.transfer.assert_not_called()

        # success case: transfer tokens when transfer possibility is True
        self.smart_token._transfer_possibility.set(True)

        self.smart_token.transfer(token_receiver, 10)
        IRCToken.transfer.assert_called_with(self.smart_token, token_receiver, 10, None)
