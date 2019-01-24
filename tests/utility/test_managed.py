# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message

from contracts.utility.managed import Managed
from tests import patch_property, ScorePatcher, create_db


class TestManaged(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(Managed)
        self.patcher.start()

        score_address = Address.from_string("cx" + "1" * 40)
        self.score = Managed(create_db(score_address))

        self.sender = Address.from_string("hx" + "2" * 40)
        with patch_property(IconScoreBase, 'msg', Message(self.sender)):
            self.score.on_install()
            self.assertEqual(self.sender, self.score._manager.get())
            self.assertEqual(ZERO_SCORE_ADDRESS, self.score._new_manager.get())

    def tearDown(self):
        self.patcher.stop()

    def test_getManager(self):
        actual_manager = self.score.getManager()
        self.assertEqual(self.score._manager.get(), actual_manager)

    def test_getNewManager(self):
        actual_new_manager = self.score.getNewManager()
        self.assertEqual(self.score._new_manager.get(), actual_new_manager)

    def test_transferManagement(self):
        # failure case: non manager try to transfer management.
        non_manager = Address.from_string("hx" + "3" * 40)
        new_manager = Address.from_string("hx" + "4" * 40)
        with patch_property(IconScoreBase, 'msg', Message(non_manager)):
            self.assertRaises(RevertException, self.score.transferManagement, new_manager)

        # failure case: set new manager as previous manager
        with patch_property(IconScoreBase, 'msg', Message(self.sender)):
            self.assertRaises(RevertException, self.score.transferManagement, self.sender)

        # success case: transfer management to new_manager
        with patch_property(IconScoreBase, 'msg', Message(self.sender)):
            self.score.transferManagement(new_manager)
            self.assertEqual(self.sender, self.score._manager.get())
            self.assertEqual(new_manager, self.score._new_manager.get())

    def test_acceptManagement(self):
        # ### initial setting for test start
        new_manager = Address.from_string("hx" + "4" * 40)
        with patch_property(IconScoreBase, 'msg', Message(self.sender)):
            self.score.transferManagement(new_manager)
        # ### initial setting for test end

        # failure case: current manager try to accept managership
        # (only new_manager can accept managership)
        with patch_property(IconScoreBase, 'msg', Message(self.sender)):
            self.assertRaises(RevertException, self.score.acceptManagement)

        # failure case: another address try to accept managership
        # (only new_manager can accept managership)
        another_manager = Address.from_string("hx" + "5" * 40)
        with patch_property(IconScoreBase, 'msg', Message(another_manager)):
            self.assertRaises(RevertException, self.score.acceptManagement)

        # success case: new_manager accept management
        with patch_property(IconScoreBase, 'msg', Message(new_manager)):
            self.score.acceptManagement()
            self.assertEqual(new_manager, self.score._manager.get())
            self.assertEqual(ZERO_SCORE_ADDRESS, self.score._new_manager.get())

            self.score.ManagerUpdate.assert_called_with(self.sender, new_manager)
