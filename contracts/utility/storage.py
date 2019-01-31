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

from iconservice import *


class Storage:
    """
    Wrapper class of icon container dbs.

    field_info = list of tuple ('field name', type of container db, value type)
    e.g.)
        FIELDS = [
            ('smart_token_address', VarDB, Address),
            ('registry', VarDB, Address),
            ('prev_registry', VarDB, Address),
            ('conversion_whitelist', VarDB, Address),
            ('connector_tokens', ArrayDB, Address),
            ('total_connector_weight', VarDB, int),
            ('max_conversion_fee', VarDB, int),
            ('conversion_fee', VarDB, int),
            ('conversions_enabled', VarDB, bool)
        ]
    """

    def __init__(self, db: IconScoreDatabase):
        self._db = db

    def add_fields(self, field_infos):
        """
        Add fields to this object

        :param field_infos: list of tuple `field info`
        """
        for name, db_class, value_type in field_infos:
            db = db_class(name, self._db, value_type=value_type)
            setattr(self, f'_{name}', db)

    def __setattr__(self, item, value):
        shadow = f'_{item}'
        attr = getattr(self, shadow, None)
        if isinstance(attr, VarDB):
            attr.set(value)
        else:
            super().__setattr__(item, value)

    def __getattribute__(self, item):
        if not item.startswith('_'):
            shadow = f'_{item}'
            if hasattr(self, shadow):
                # If the shadow object of given attribute exists returns it
                # and if it is instance of VarDB, returns real value
                attr = getattr(self, shadow)
                return attr.get() if isinstance(attr, VarDB) else attr
        return super().__getattribute__(item)
