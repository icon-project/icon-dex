import unittest
from unittest.mock import Mock

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message

from contracts.utility.owned import Owned
from tests import patch, ScorePatcher, create_db


class TestOwned(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(Owned)
        self.patcher.start()

        score_address = Address.from_string("cx" + "1" * 40)
        self.score = Owned(create_db(score_address))

        self.sender = Address.from_string("hx" + "2" * 40)
        with patch([(IconScoreBase, 'msg', Message(self.sender))]):
            self.score.on_install()
            self.assertEqual(self.sender, self.score._owner.get())
            self.assertEqual(ZERO_SCORE_ADDRESS, self.score._new_owner.get())

    def tearDown(self):
        self.patcher.stop()

    def test_getOwner(self):
        actual_owner = self.score.getOwner()
        self.assertEqual(self.score._owner.get(), actual_owner)

    def test_getNewOwner(self):
        actual_new_owner = self.score.getNewOwner()
        self.assertEqual(self.score._new_owner.get(), actual_new_owner)

    def test_transferOwnerShip(self):
        # failure case: non owner try to transfer ownership.
        non_owner = Address.from_string("hx" + "3" * 40)
        new_owner = Address.from_string("hx" + "4" * 40)
        with patch([(IconScoreBase, 'msg', Message(non_owner))]):
            self.assertRaises(RevertException, self.score.transferOwnerShip, new_owner)

        # failure case: try to set new owner as previous owner
        with patch([(IconScoreBase, 'msg', Message(self.sender))]):
            self.assertRaises(RevertException, self.score.transferOwnerShip, self.sender)

        # success case: transfer ownership to new_owner
        with patch([(IconScoreBase, 'msg', Message(self.sender))]):
            self.score.owner_only = Mock()
            self.score.transferOwnerShip(new_owner)
            self.score.owner_only.assert_called()
            self.assertEqual(self.sender, self.score._owner.get())
            self.assertEqual(new_owner, self.score._new_owner.get())

    def test_acceptOwnership(self):
        # ### initial setting for test start
        new_owner = Address.from_string("hx" + "4" * 40)
        with patch([(IconScoreBase, 'msg', Message(self.sender))]):
            self.score.transferOwnerShip(new_owner)

        # ### initial setting for test end

        # failure case: current owner try to accept ownership ( only new owner can accept ownership)
        with patch([(IconScoreBase, 'msg', Message(self.sender))]):
            self.assertRaises(RevertException, self.score.acceptOwnerShip)

        # failure case: another address try to accept ownership
        # ( only new owner can accept ownership)
        another_owner = Address.from_string("hx" + "5" * 40)
        with patch([(IconScoreBase, 'msg', Message(another_owner))]):
            self.assertRaises(RevertException, self.score.acceptOwnerShip)

        # success case:
        with patch([(IconScoreBase, 'msg', Message(new_owner))]):
            self.score.acceptOwnerShip()
            self.assertEqual(new_owner, self.score._owner.get())
            self.assertEqual(ZERO_SCORE_ADDRESS, self.score._new_owner.get())

            self.score.OwnerUpdate.assert_called_with(self.sender, new_owner)
