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

import inspect
from collections import namedtuple
from typing import List
from unittest import mock
from unittest.mock import Mock, PropertyMock

from iconservice import Address, IconScoreDatabase, IconScoreBase, revert
from iconservice.database.db import ContextDatabase
from iconservice.iconscore.icon_score_constant import CONST_BIT_FLAG, ConstBitFlag
from iconservice.iconscore.icx import Icx
from iconservice.iconscore.internal_call import InternalCall


def create_db(address: Address):
    """
    Create memory db for IconScoreDatabase

    :param address: score address
    :return: IconScoreDatabase
    """
    memory_db = {}

    # noinspection PyUnusedLocal
    def put(context, key, value):
        memory_db[key] = value

    # noinspection PyUnusedLocal
    def get(context, key):
        return memory_db.get(key)

    # noinspection PyUnusedLocal
    def delete(context, key):
        del memory_db[key]

    context_db = Mock(spec=ContextDatabase)
    context_db.get = get
    context_db.put = put
    context_db.delete = delete

    return IconScoreDatabase(address, context_db)


# patch target format
Target = namedtuple("Target", "target, attribute, return_value")


def patch(targets: List[Target]):
    """
    patch multiple targets

    :param targets: a list of Target(target, attribute, return_value)
    :return: patcher
    """
    patcher = Patcher()

    for target in targets:
        patcher.append(target[0], target[1], target[2])

    return patcher


class Patcher:
    """
    patcher for multiple patch
    """

    def __init__(self):
        self.patchers = {}

    def append(self, target, attribute, return_value):
        path = f'{target.__module__}.{target.__name__}'
        if attribute:
            path += f'.{attribute}'
        attr = getattr(target, attribute) if attribute else None
        new_callable = PropertyMock if isinstance(attr, property) else None
        try:
            patcher_list = self.patchers[target.__name__]
        except KeyError:
            patcher_list = self.patchers[target.__name__] = {}

        patcher = mock.patch(path, new_callable=new_callable, return_value=return_value)
        patcher_list[attribute] = patcher

    def start(self):
        mocks = Mock()

        for target, patcher_list in self.patchers.items():
            target_mock = Mock()
            setattr(mocks, target, target_mock)

            for attribute, patcher in patcher_list.items():
                attribute_mock = patcher.start()
                if isinstance(attribute_mock, PropertyMock):
                    attribute_mock = attribute_mock.return_value

                if attribute:
                    setattr(target_mock, attribute, attribute_mock)
                else:
                    target_mock = attribute_mock

        return mocks

    def stop(self):
        for patcher_list in self.patchers.values():
            for patcher in patcher_list.values():
                patcher.stop()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


class ScorePatcher:
    """
    patcher for SCORE
    """

    def __init__(self, score_class):
        self.mocks = None
        self.patcher = Patcher()
        self.searched_class = set()
        self._append_patch_event_logs(score_class)
        self._append_patch_bases(score_class)
        self.patcher.append(IconScoreBase, 'get_owner', None)
        self.patcher.append(IconScoreBase, 'icx', Mock(spec=Icx))
        self.patcher.append(revert, None, None)

    def _append_patch_bases(self, a_class):
        for base in a_class.__bases__:
            if not inspect.isabstract(base):
                self._append_patch_class(base)

    def _append_patch_class(self, a_class):
        if a_class in self.searched_class:
            return

        self.searched_class.add(a_class)
        for name in a_class.__dict__:
            attr = getattr(a_class, name)
            if inspect.isfunction(attr) and name != '__init__':
                self.patcher.append(a_class, attr.__name__, None)

        self._append_patch_bases(a_class)

    def _append_patch_event_logs(self, a_class):
        if a_class in self.searched_class:
            return

        self.searched_class.add(a_class)
        for name in a_class.__dict__:
            attr = getattr(a_class, name)
            if inspect.isfunction(attr) and \
                    getattr(attr, CONST_BIT_FLAG, 0) & ConstBitFlag.EventLog:
                self.patcher.append(a_class, attr.__name__, None)

    def start(self):
        return self.patcher.start()

    def stop(self):
        self.patcher.stop()


# noinspection PyUnresolvedReferences
def assert_inter_call(self,
                      from_score: Address,
                      to_score: Address,
                      function_name: str,
                      params: list):
    """
    Asserts inter-call with params.
    To use this, `InternalCall.other_external_call` should be patched

    :param self: test context(unittest.TestCase)
    :param from_score: caller score
    :param to_score: target of interface score
    :param function_name: calling function name
    :param params: calling function params
    """
    external_call = InternalCall.other_external_call
    external_call.assert_called()

    match = False
    for call_args in external_call.call_args_list:
        if call_args[0][1] == from_score and \
                call_args[0][2] == to_score and call_args[0][4] == function_name:
            param_match = True
            for index, param in enumerate(params):
                if call_args[0][5][index] != param:
                    param_match = False
                    break
            if param_match:
                match = True
                break

    self.assertTrue(match)
