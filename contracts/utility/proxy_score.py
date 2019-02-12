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

# noinspection PyUnreachableCode
# for type hinting
if False:
    from typing import TypeVar

    T = TypeVar('T')


class ProxyScore(type):
    """
    A Proxy class that provides an Interface SCORE from the abc class

    usage:
        token_score = self.create_interface_score(token_address, ProxyScore(ABCIRCToken))
        token_score.transfer(to, value)
    """

    @classmethod
    def _create_proxy_class(mcs, abc_class: 'T') -> 'T':
        """
        Creates an interface SCORE related in given abc class,

        :param abc_class: An abstract class
        :return: interface SCORE class
        """

        interface_functions = {}

        attributes = dir(abc_class)
        for attribute_name in attributes:
            attribute = getattr(abc_class, attribute_name)
            if callable(attribute) \
                    and hasattr(attribute, '__isabstractmethod__') \
                    and attribute.__isabstractmethod__:
                interface_functions[attribute.__name__] = mcs._get_interface_function(attribute)

        proxy_name = "%s(%s)" % (mcs.__name__, abc_class.__name__)
        return type(proxy_name, (InterfaceScore, abc_class), interface_functions)

    @classmethod
    def _get_interface_function(mcs, func):
        try:
            cache = mcs.__dict__["_interface_function_cache"]
        except KeyError:
            mcs._interface_function_cache = cache = {}
        try:
            interface_function = cache[func]
        except KeyError:
            cache[func] = interface_function = interface(func)
            interface_function.__isabstractmethod__ = False
        return interface_function

    def __new__(mcs, abc_class: 'T') -> 'T':
        """
        Retrieves an interface SCORE related in given abc class if the cache exists,
        otherwise creates a new one

        :param abc_class: An abstract class
        :return: interface SCORE class
        """
        try:
            cache = mcs.__dict__["_proxy_class_cache"]
        except KeyError:
            mcs._proxy_class_cache = cache = {}
        try:
            proxy_class = cache[abc_class]
        except KeyError:
            cache[abc_class] = proxy_class = mcs._create_proxy_class(abc_class)
        return proxy_class
