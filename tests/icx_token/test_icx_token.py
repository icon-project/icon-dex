import unittest

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message
from iconservice.base.transaction import Transaction

from contracts.icx_token.icx_token import IcxToken
from tests import patch, ScorePatcher, create_db


class TestIcxScore(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(IcxToken)
        self.patcher.start()

        score_address = Address.from_string("cx" + "1" * 40)
        self.score = IcxToken(create_db(score_address))

        sender = Address.from_string("hx" + "2" * 40)
        with patch([(IconScoreBase, 'msg', Message(sender))]):
            self.score.on_install()
            self.patcher.IRCToken.on_install.assert_called()
            self.patcher.TokenHolder.on_install.assert_called()

    def tearDown(self):
        self.patcher.stop()

    def test_deposit(self):
        sender = Address.from_string("hx" + "2" * 40)
        value = 10

        with patch([
            (IconScoreBase, 'msg', Message(sender, value=value)),
        ]):
            before_balance = self.score._balances[sender]
            before_total_supply = self.score._total_supply.get()

            self.score.deposit()
            assert value == self.score._balances[sender] - before_balance
            assert value == self.score._total_supply.get() - before_total_supply
            self.patcher.EventLogEmitter.emit_event_log.assert_called()
            self.patcher.EventLogEmitter.emit_event_log.assert_called()

    def test_withdrawTo(self):
        sender = Address.from_string("hx" + "2" * 40)
        to = Address.from_string("hx" + "3" * 40)

        self.score._balances[sender] = 10
        self.score._total_supply.set(10)

        with patch([(IconScoreBase, 'msg', Message(sender))]):
            # test if the revert would be called when out of balance
            self.assertRaises(RevertException, self.score.withdrawTo, 20, to)

            self.score.withdrawTo(10, to)

            self.patcher.IconScoreBase.icx.send.assert_called()

            assert self.score._balances[sender] == 0
            assert self.score._total_supply.get() == 0
            self.patcher.EventLogEmitter.emit_event_log.assert_called()
