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

from ..interfaces.abc_converter import ABCConverter
from ..interfaces.abc_icx_token import ABCIcxToken
from ..interfaces.abc_irc_token import ABCIRCToken
from ..interfaces.abc_flexible_token import ABCFlexibleToken
from ..utility.proxy_score import ProxyScore
from ..utility.token_holder import TokenHolder
from ..utility.utils import *

TAG = 'Network'

# interface SCOREs
IRCToken = ProxyScore(ABCIRCToken)
IcxToken = ProxyScore(ABCIcxToken)
FlexibleToken = ProxyScore(ABCFlexibleToken)
Converter = ProxyScore(ABCConverter)


# noinspection PyPep8Naming,PyMethodOverriding
class Network(TokenHolder):
    _MAX_CONVERSION_COUNT = 10

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._icx_tokens = DictDB('icx_tokens', db, value_type=bool)

    def on_install(self) -> None:
        TokenHolder.on_install(self)

    def on_update(self) -> None:
        TokenHolder.on_update(self)

    @external(readonly=True)
    def getExpectedReturnByPath(self, _path: str, _amount: int) -> int:
        """
        returns the expected return amount for converting a specific amount by following
        a given conversion path.
        notice that there is no support for circular paths

        :param _path: conversion path, see conversion path format above
        :param _amount: amount to convert from (in the initial source token)
        :return: expected conversion return amount and conversion fee
        """
        converted_path = self._convert_path(_path)
        self._require_valid_path(converted_path)
        require_positive_value(_amount)

        amount = _amount
        from_token_address = converted_path[0]
        for i in range(1, len(converted_path), 2):
            to_token_address = converted_path[i + 1]
            # converted_path[i] is flexible token address
            flexible_token = self.create_interface_score(converted_path[i], FlexibleToken)
            converter = self.create_interface_score(flexible_token.getOwner(), Converter)

            amount = converter.getReturn(from_token_address, to_token_address, amount)["amount"]
            from_token_address = to_token_address
        # todo: consider about returning fee (in solidity, return amount and fee)
        return amount

    @external(readonly=True)
    def getIcxTokenRegistered(self, _icxToken: Address) -> bool:
        """
        returns the information about icx token registration of a given token address

        :param _icxToken: icx token address that you want to check
        :return: registration information. if returns true, that shows token is registered as an icx token in the network
        """
        return self._icx_tokens[_icxToken]

    @staticmethod
    def _convert_path(path: str):
        converted_path = map(lambda address: address.strip(), path.split(","))
        return [Address.from_string(address) for address in converted_path]

    def _convert_bytes_data(self, data: bytes, token_sender_address: Address):
        """
        convert bytes data to a dictionary type data and check each key and the type of value
        this method does not check whether a value is valid or not

        :param data: utf-8 encoded bytes data
        :param token_sender_address: address of token sender
        :return: converted dictionary data
        """
        result_dict_data = dict()
        dict_data = dict()
        try:
            dict_data = json_loads(data.decode(encoding="utf-8"))
            result_dict_data["path"] = self._convert_path(dict_data["path"])
            result_dict_data["minReturn"] = dict_data["minReturn"]
        except UnicodeDecodeError:
            revert("data's encoding type is invalid. utf-8 is valid encoding type.")
        except ValueError as e:
            revert(f"json format error: {e}")
        except KeyError as e:
            revert(f"missing key and value: {e}")
        except Exception as e:
            # InvalidParamsException could be raised when converting the path
            revert(str(e))

        require(isinstance(result_dict_data["minReturn"], int), "need valid minReturn data")
        if "for" not in dict_data or dict_data["for"] is None:
            result_dict_data["for"] = token_sender_address
        else:
            result_dict_data["for"] = Address.from_string(dict_data["for"])
        return result_dict_data

    def _require_valid_path(self, path: list):
        """
        validates a conversion path.
        verifies that the number of elements is odd and that maximum number of 'conversion' is 10
        this also verifies that if the path is circular path or not

        :param path: converted path
        """
        path_len = len(path)
        require(2 < path_len <= self._MAX_CONVERSION_COUNT * 2 + 1 and path_len % 2 == 1, "invalid path")

        path_set = {address for i, address in enumerate(path) if i % 2 == 1}
        require(len(path_set) == path_len // 2, "do not support circular path")

    @external
    def registerIcxToken(self, _icxToken: Address, _register: bool):
        """
        allows the owner to register/unregister Icx tokens

        :param _icxToken: Icx token contract address
        :param _register: true to register, false to unregister
        """
        self.require_owner_only()
        require_valid_address(_icxToken)
        require_not_this(self.address, _icxToken)

        self._icx_tokens[_icxToken] = _register

    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        """
        invoked when the contract receives tokens
        if the data is b'conversionResult', this regard as the result of conversion from a converter
        if the data parameter is parsed as conversion format,
        token conversion is executed
        conversion format is:
        ```
        {
            'path': [STR]
            'minReturn': [INT]
            'for': [STR_ADDRESS] or None (optional)
        }
        ```

        :param _from: token sender
        :param _value: amount of tokens
        :param _data: additional data
        """
        # only when the received token is the result of a convert from a converter or request converting, accept it.
        if _data == b'conversionResult':
            return

        dict_data = self._convert_bytes_data(_data, _from)
        # check the value of dict_data
        require(dict_data["path"][0] == self.msg.sender, "wrong access, only token can call this method")

        require_positive_value(dict_data["minReturn"])
        require_valid_address(dict_data["for"])
        self._require_valid_path(dict_data["path"])

        self._convert_for_internal(dict_data["path"], _value, dict_data["minReturn"], dict_data["for"])

    @external
    @payable
    def convert(self, _path: str, _minReturn: int):
        """
        converts the Icx token to any other token in the network by following
        a predefined conversion path and transfers the result tokens back to the sender
        note that the converter should already own the source tokens

        :param _path: conversion path, see conversion path format above
        :param _minReturn:
        if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :return: tokens issued in return
        """
        return self.convertFor(_path, _minReturn, self.msg.sender)

    @external
    @payable
    def convertFor(self, _path: str, _minReturn: int, _for: Address):
        """
        converts the Icx token to any other token in the network by following
        a predefined conversion path and transfers the result tokens to a target account
        note that the converter should already own the source tokens
        if the first token address of the path is not the icx token, raise error

        :param _path: conversion path, see conversion path format above
        :param _minReturn:
        if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :param _for: account that will receive the conversion result
        :return: tokens issued in return
        """
        converted_path = self._convert_path(_path)
        self._require_valid_path(converted_path)
        require_positive_value(_minReturn)
        require_valid_address(_for)
        require_not_this(self.address, _for)
        icx_amount = self.msg.value

        icx_token = converted_path[0]
        require(self._icx_tokens[icx_token], "wrong path, first address must be icx token")

        # transfer ICX coin to IcxToken SCORE. network will get same amount of icx token instead
        self.icx.transfer(icx_token, icx_amount)

        return self._convert_for_internal(converted_path, icx_amount, _minReturn, _for)

    def _convert_for_internal(self, path: list, amount: int, min_return: int, _for: Address):
        """
        converts token to any other token in the network
        by following a predefined conversion paths and transfers the result
        tokens to a target account

        :param path: conversion path, see conversion path format above
        :param amount: amount to convert from (in the initial source token)
        :param min_return:
        if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :param _for: account that will receive the conversion result
        :return: tokens issued in return
        """
        (to_token_address, amount) = self._convert_by_path(path, amount, min_return, _for)

        if self._icx_tokens[to_token_address]:
            icx_token = self.create_interface_score(to_token_address, IcxToken)
            icx_token.withdrawTo(amount, _for)
        else:
            token = self.create_interface_score(to_token_address, IRCToken)
            token.transfer(_for, amount, b'None')

        return amount

    def _convert_by_path(self, path: list, amount: int, min_return: int, _for: Address):
        """
        executes the actual conversion by following the conversion path

        :param path: conversion path, see conversion path format above
        :param amount: amount to convert from (in the initial source token)
        :param min_return:
        if the conversion results in an amount smaller than the minimum return - it is cancelled, must be nonzero
        :param _for: account that will receive the conversion result
        :return: IRC token to convert to (the last element in the path) & tokens issued in return
        """
        # define from and to token address
        to_token_address = ZERO_SCORE_ADDRESS
        from_token_address = path[0]
        from_token = self.create_interface_score(from_token_address, IRCToken)

        data = dict()
        for i in range(1, len(path), 2):
            flexible_token_address = path[i]
            to_token_address = path[i+1]

            to_token = self.create_interface_score(to_token_address, IRCToken)
            flexible_token = self.create_interface_score(flexible_token_address, FlexibleToken)
            converter_address = flexible_token.getOwner()

            amount_before_converting = to_token.balanceOf(self.address)
            data["toToken"] = str(to_token_address)
            data["minReturn"] = min_return if i == len(path)-2 else 1
            encoded_data = json_dumps(data).encode(encoding='utf-8')

            from_token.transfer(converter_address, amount, encoded_data)

            amount_after_converting = to_token.balanceOf(self.address)
            amount = amount_after_converting - amount_before_converting
            from_token = to_token

        return to_token_address, amount
