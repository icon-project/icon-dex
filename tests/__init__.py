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
from unittest.mock import Mock, patch, PropertyMock

from iconservice import Address, IconScoreDatabase, IconScoreBase
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


def patch_property(target, attribute, return_value):
    """
    patch property of target

    :param target: containing class
    :param attribute: property name string
    :param return_value: returning value of the property
    :return: patcher
    """
    return patch.object(
        target, attribute, new_callable=PropertyMock, return_value=return_value)


class MultiPatch:
    """
    patch for multiple patch
    """

    def __init__(self, patchers=None):
        if patchers is None:
            patchers = []
        self._patchers = patchers

    def append(self, patcher):
        self._patchers.append(patcher)

    def start(self):
        mocks = []

        for patcher in self._patchers:
            mocks.append(patcher.start())

        return mocks

    def stop(self):
        for patcher in self._patchers:
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
        self.patcher = MultiPatch()
        self.searched_class = set()
        self._append_patch_event_logs(score_class)
        self._append_patch_bases(score_class)
        self.patcher.append(patch.object(IconScoreBase, 'get_owner'))
        self.patcher.append(patch_property(IconScoreBase, 'icx', Mock(spec=Icx)))

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
                self.patcher.append(patch.object(a_class, attr.__name__))

        self._append_patch_bases(a_class)

    def _append_patch_event_logs(self, a_class):
        if a_class in self.searched_class:
            return

        self.searched_class.add(a_class)
        for name in a_class.__dict__:
            attr = getattr(a_class, name)
            if inspect.isfunction(attr) and \
                    getattr(attr, CONST_BIT_FLAG, 0) & ConstBitFlag.EventLog:
                self.patcher.append(patch.object(a_class, attr.__name__))

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
