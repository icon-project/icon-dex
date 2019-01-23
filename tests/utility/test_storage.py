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
from unittest.mock import patch

from iconservice import Address, VarDB, ArrayDB, DictDB

from contracts.utility.storage import Storage
from tests import create_db


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.storage = Storage(create_db(Address.from_string("cx" + "1" * 40)))
        self.storage.add_fields([
            ('array_db', ArrayDB, int),
            ('dict_db', DictDB, int),
            ('var_db', VarDB, int)
        ])

    def tearDown(self):
        pass

    def test_has_field(self):
        self.assertTrue(hasattr(self.storage, 'array_db'))
        self.assertTrue(hasattr(self.storage, 'dict_db'))
        self.assertTrue(hasattr(self.storage, 'var_db'))

    def test_has_shadow_field(self):
        # test if the storage has shadow classes
        self.assertTrue(hasattr(self.storage, '_array_db'))
        self.assertTrue(hasattr(self.storage, '_dict_db'))
        self.assertTrue(hasattr(self.storage, '_var_db'))

    def test_array_db_type(self):
        _array_db = self.storage._array_db
        self.assertTrue(isinstance(_array_db, ArrayDB))
        array_db = self.storage.array_db
        self.assertTrue(isinstance(array_db, ArrayDB))

    def test_dict_db_type(self):
        _dict_db = self.storage._dict_db
        self.assertTrue(isinstance(_dict_db, DictDB))
        dict_db = self.storage.dict_db
        self.assertTrue(isinstance(dict_db, DictDB))

    def test_var_db_type(self):
        _var_db = self.storage._var_db
        self.assertTrue(isinstance(_var_db, VarDB))
        # var db returns real value of VarDB
        var_db = self.storage.var_db
        self.assertTrue(isinstance(var_db, int))

    def test_setter_var_db(self):
        with patch.object(VarDB, 'set') as set:
            self.storage.var_db = 1234
            set.assert_called_with(1234)

        self.storage.var_db = 1234
        self.storage.var_db += 1
        self.assertEqual(self.storage.var_db, 1235)
        self.storage.var_db = self.storage.var_db + 10
        self.assertEqual(self.storage.var_db, 1245)

    def test_getter_var_db(self):
        with patch.object(VarDB, 'get') as get:
            value = self.storage.var_db
            get.assert_called()
