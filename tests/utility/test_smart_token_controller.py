import unittest

from iconservice import *
from iconservice.base.message import Message
from iconservice.iconscore.internal_call import InternalCall

from contracts.icx_token.icx_token import IcxToken
from contracts.utility.smart_token_controller import SmartTokenController
from contracts.utility.token_holder import TokenHolder
from contracts.utility.utils import Utils
from tests import patch, ScorePatcher, create_db, assert_inter_call


# noinspection PyUnresolvedReferences
class TestSmartTokenController(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(IcxToken)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.smart_token_address = Address.from_string("cx" + "2" * 40)
        self.score = SmartTokenController(create_db(self.score_address))

        self.owner = Address.from_string("hx" + "2" * 40)
        with patch([
            (IconScoreBase, 'msg', Message(self.owner)),
            (Utils, 'check_valid_address', None),
        ]):
            self.score.on_install(self.smart_token_address)
            TokenHolder.on_install.assert_called_with(self.score)
            Utils.check_valid_address.assert_called_with(self.smart_token_address)

    def tearDown(self):
        self.patcher.stop()

    def test_transferTokenOwnership(self):
        new_owner = Address.from_string("hx" + "3" * 40)

        with patch([
            (IconScoreBase, 'msg', Message(self.owner)),
            (InternalCall, 'other_external_call', None),
        ]):
            self.score.transferTokenOwnership(new_owner)
            self.score.owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score.storage.token,
                'transferOwnerShip',
                [new_owner])

    def test_acceptTokenOwnership(self):
        with patch([
            (IconScoreBase, 'msg', Message(self.owner)),
            (InternalCall, 'other_external_call', None),
        ]):
            self.score.acceptTokenOwnership()
            self.score.owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score.storage.token,
                'acceptOwnerShip',
                []
            )

    def test_disableTokenTransfers(self):
        disable = True
        with patch([
            (IconScoreBase, 'msg', Message(self.owner)),
            (InternalCall, 'other_external_call', None),
        ]):
            self.score.disableTokenTransfers(disable)
            self.score.owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score.storage.token,
                'disableTransfer',
                [disable]
            )

    def test_withdrawFromToken(self):
        token = Address.from_string("cx" + "3" * 40)
        to = Address.from_string("hx" + "3" * 40)
        amount = 100
        with patch([
            (IconScoreBase, 'msg', Message(self.owner)),
            (InternalCall, 'other_external_call', None),
        ]):
            self.score.withdrawFromToken(token, to, amount)
            self.score.owner_only.assert_called()

            assert_inter_call(
                self,
                self.score.address,
                self.score.storage.token,
                'withdrawTokens',
                [token, to, amount]
            )
