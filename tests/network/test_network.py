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

import json
import unittest
from random import SystemRandom
from typing import TYPE_CHECKING
from unittest.mock import Mock, PropertyMock, patch

from iconservice.base.exception import RevertException, InvalidParamsException
from iconservice.base.message import Message

from contracts.interfaces.abc_icx_token import ABCIcxToken
from contracts.interfaces.abc_irc_token import ABCIRCToken
from contracts.network.network import Network
from contracts.utility.proxy_score import ProxyScore
from contracts.utility.token_holder import TokenHolder
from contracts.utility.utils import *
from tests import patch_property, MultiPatch, ScorePatcher, create_db

if TYPE_CHECKING:
    from iconservice.base.address import Address


# noinspection PyUnresolvedReferences
class TestNetwork(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(Network)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.network_score = Network(create_db(self.score_address))

        self.network_owner = Address.from_string("hx" + "1" * 40)

        self.smart_token_address_list = [Address.from_string("cx" + str(i) * 40) for i in range(0, 3)]
        self.connector_token_list = [Address.from_string("cx" + str(i) * 40) for i in range(3, 7)]
        self.icx_token = Address.from_string("cx" + "7" * 40)

        with patch_property(IconScoreBase, 'msg', Message(self.network_owner)):
            self.network_score.on_install()
            TokenHolder.on_install.assert_called_with(self.network_score)

    def tearDown(self):
        self.patcher.stop()

    def test_check_valid_path(self):
        # success case: input the valid path
        path = [self.connector_token_list[0], self.smart_token_address_list[0], self.connector_token_list[1]]
        self.network_score._require_valid_path(path)

        # failure case: input path whose length under 3
        invalid_path = [self.connector_token_list[0], self.smart_token_address_list[0]]
        self.assertRaises(RevertException, self.network_score._require_valid_path, invalid_path)

        # failure case: input path whose length is more than 21
        random = SystemRandom()
        # use random data to avoid same address is made
        invalid_path = [Address.from_string(
            "cx" + str(random.randrange(10)) + str(random.randrange(10)) * 39) in range(0, 22)]
        self.assertRaises(RevertException, self.network_score._require_valid_path, invalid_path)

        # failure case: input path whose length is even
        invalid_path = [self.connector_token_list[0], self.smart_token_address_list[0],
                        self.connector_token_list[1], self.smart_token_address_list[1]]
        self.assertRaises(RevertException, self.network_score._require_valid_path, invalid_path)

        # failure case: input path which has the same smart token address in it
        invalid_path = [self.connector_token_list[0], self.smart_token_address_list[0], self.connector_token_list[1],
                        self.smart_token_address_list[0], self.connector_token_list[1]]
        self.assertRaises(RevertException, self.network_score._require_valid_path, invalid_path)

        # success case: input path which has the same smart token address in the 'from' or 'to' position in it
        # path: [connector0 - smart token0 - smart token1 - smart token2, smart token0]
        path = [self.connector_token_list[0], self.smart_token_address_list[0], self.smart_token_address_list[1],
                self.smart_token_address_list[2], self.smart_token_address_list[0]]
        self.network_score._require_valid_path(path)

        # success case: input path which has the same smart tokens that only exist in 'from' or 'to' in it
        path = [self.smart_token_address_list[0], self.smart_token_address_list[1], self.connector_token_list[0],
                self.smart_token_address_list[2], self.smart_token_address_list[0]]
        self.network_score._require_valid_path(path)

    def test_check_and_convert_bytes_data(self):
        # failure case: input invalid JSON format data
        invalid_json_format = dict()
        invalid_json_format["path"] = "{0},{1},{2}".format(str(self.connector_token_list[0]),
                                                           str(self.smart_token_address_list[0]),
                                                           str(self.connector_token_list[1]))
        invalid_json_format["for"] = str(self.network_owner)
        invalid_json_format["minReturn"] = 10
        stringed_invalid_json_format = "[" + json.dumps(invalid_json_format) + "}"
        encoded_invalid_json_format = stringed_invalid_json_format.encode(encoding="utf-8")
        self.assertRaises(RevertException, self.network_score._convert_bytes_data, encoded_invalid_json_format,
                          self.network_owner)

        # failure case: input data which is not decoded to utf-8
        valid_json_format = dict()
        valid_json_format["path"] = "{0},{1},{2}".format(str(self.connector_token_list[0]),
                                                         str(self.smart_token_address_list[0]),
                                                         str(self.connector_token_list[1]))

        valid_json_format["for"] = str(self.network_owner)
        valid_json_format["minReturn"] = 10
        stringed_valid_json_format = json.dumps(valid_json_format)
        cp037_encoded_valid_json_format = stringed_valid_json_format.encode(encoding='cp037')
        self.assertRaises(RevertException,
                          self.network_score._convert_bytes_data,
                          cp037_encoded_valid_json_format,
                          self.network_owner)

        # failure case: input invalid path data (associated with '/')
        json_format = dict()
        json_format["path"] = "{0}/{1}/{2}".format(str(self.connector_token_list[0]),
                                                   str(self.smart_token_address_list[0]),
                                                   str(self.connector_token_list[1]))
        json_format["for"] = str(self.network_owner)
        json_format["minReturn"] = 10
        stringed_valid_json_format = json.dumps(json_format)
        encoded_valid_json_format = stringed_valid_json_format.encode(encoding='utf-8')
        self.assertRaises(InvalidParamsException,
                          self.network_score._convert_bytes_data,
                          encoded_valid_json_format,
                          self.network_owner)

        # failure case: input invalid path data ( has an invalid address as an element )
        json_format = dict()
        json_format["path"] = "{0},{1},{2}".format(str(self.connector_token_list[0]),
                                                   str("invalid_address"),
                                                   str(self.connector_token_list[1]))
        json_format["for"] = str(self.network_owner)
        json_format["minReturn"] = 10
        stringed_valid_json_format = json.dumps(json_format)
        encoded_valid_json_format = stringed_valid_json_format.encode(encoding='utf-8')
        self.assertRaises(InvalidParamsException,
                          self.network_score._convert_bytes_data,
                          encoded_valid_json_format,
                          self.network_owner)

        # failure case: input string type minReturn
        json_format = dict()
        json_format["path"] = "{0},{1},{2}".format(str(self.connector_token_list[0]),
                                                   str(self.smart_token_address_list[0]),
                                                   str(self.connector_token_list[1]))
        json_format["for"] = str(self.network_owner)
        json_format["minReturn"] = "10"
        stringed_valid_json_format = json.dumps(json_format)
        encoded_valid_json_format = stringed_valid_json_format.encode(encoding='utf-8')
        self.assertRaises(RevertException,
                          self.network_score._convert_bytes_data,
                          encoded_valid_json_format,
                          self.network_owner)

        # success case: "for" key is not in the data
        # ( returned data should have token sender address as a "for" key's value )
        token_sender = Address.from_string("hx" + "a" * 40)
        json_format = dict()
        json_format["path"] = "{0},{1},{2}".format(str(self.connector_token_list[0]),
                                                   str(self.smart_token_address_list[0]),
                                                   str(self.connector_token_list[1]))
        json_format["minReturn"] = 10
        stringed_valid_json_format = json.dumps(json_format)
        encoded_valid_json_format = stringed_valid_json_format.encode(encoding='utf-8')
        result_data = self.network_score._convert_bytes_data(encoded_valid_json_format, token_sender)
        self.assertEqual(token_sender, result_data["for"])

        # success case: "for" key is exist but value is None
        # ( returned dict data should have token sender address as a "for" key's value )
        json_format["for"] = None
        stringed_valid_json_format = json.dumps(json_format)
        encoded_valid_json_format = stringed_valid_json_format.encode(encoding='utf-8')
        result_data = self.network_score._convert_bytes_data(encoded_valid_json_format, token_sender)
        self.assertEqual(token_sender, result_data["for"])

        # success case: input data which has "for" key and it's value
        for_address = Address.from_string("hx" + "b" * 40)
        json_format["for"] = str(for_address)
        stringed_valid_json_format = json.dumps(json_format)
        encoded_valid_json_format = stringed_valid_json_format.encode(encoding='utf-8')
        result_data = self.network_score._convert_bytes_data(encoded_valid_json_format, token_sender)
        self.assertEqual(for_address, result_data["for"])

    def test_convertFor(self):
        icx_amount = 10

        # failure case: input wrong path format
        min_return = 10
        for_address = Address.from_string("hx" + "a" * 40)
        invalid_path = "{0}/{1}/{2}".format(str(self.icx_token),
                                            str(self.smart_token_address_list[0]),
                                            str(self.connector_token_list[0]))
        with patch_property(IconScoreBase, 'msg', Message(self.network_owner, value=icx_amount)):
            self.assertRaises(InvalidParamsException,
                              self.network_score.convertFor,
                              invalid_path, min_return, for_address)

        # failure case: input path whose has invalid address as an element
        min_return = 10
        for_address = Address.from_string("hx" + "a" * 40)
        invalid_path = "{0},{1},{2}".format(str(self.icx_token),
                                            str("invalid_address"),
                                            str(self.connector_token_list[1]))
        with patch_property(IconScoreBase, 'msg', Message(self.network_owner, value=icx_amount)):
            self.assertRaises(InvalidParamsException,
                              self.network_score.convertFor,
                              invalid_path, min_return, for_address)

        # failure case: input min return less than 0
        invalid_min_return = -1
        for_address = Address.from_string("hx" + "a" * 40)
        path = "{0},{1},{2}".format(str(self.icx_token),
                                    str(self.smart_token_address_list[0]),
                                    str(self.connector_token_list[0]))
        with patch_property(IconScoreBase, 'msg', Message(self.network_owner, value=icx_amount)):
            self.assertRaises(RevertException,
                              self.network_score.convertFor,
                              path, invalid_min_return, for_address)

        # failure case: input path whose first address is not Icx token address
        min_return = 10
        for_address = Address.from_string("hx" + "a" * 40)
        invalid_path = "{0},{1},{2}".format(str(self.connector_token_list[0]),
                                            str(self.smart_token_address_list[0]),
                                            str(self.connector_token_list[1]))
        with patch_property(IconScoreBase, 'msg', Message(self.network_owner, value=icx_amount)):
            self.assertRaises(RevertException,
                              self.network_score.convertFor,
                              invalid_path, min_return, for_address)

        # success case: input valid path
        min_return = 10
        for_address = Address.from_string("hx" + "a" * 40)
        path = "{0},{1},{2}".format(str(self.icx_token),
                                    str(self.smart_token_address_list[0]),
                                    str(self.connector_token_list[1]))
        self.network_score._icx_tokens[self.icx_token] = True
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.network_owner, value=icx_amount)),
            patch.object(Network, '_convert_for_internal')
        ]):
            self.network_score.convertFor(path, min_return, for_address)
            self.network_score.icx.transfer.assert_called_with(self.icx_token, icx_amount)
            converted_path = [self.icx_token, self.smart_token_address_list[0], self.connector_token_list[1]]
            self.network_score._convert_for_internal.assert_called_with(converted_path,
                                                                        icx_amount,
                                                                        min_return,
                                                                        for_address)

    def test_tokenFallback(self):
        # success case: input 'conversionResult' to _data ( convert_for_internal should not be called )
        from_address = Address.from_string("hx" + "a" * 40)
        for_address = Address.from_string("hx" + "b" * 40)
        value = 10
        min_return = 5
        path = "{0},{1},{2}".format(str(self.connector_token_list[0]),
                                    str(self.smart_token_address_list[0]),
                                    str(self.connector_token_list[1]))
        converted_path = [Address.from_string(address) for address in path.split(",")]

        data = dict()
        data["path"] = path
        data["minReturn"] = min_return
        data["for"] = str(for_address)
        stringed_data = json.dumps(data)
        decoded_data = stringed_data.encode(encoding='utf-8')

        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.connector_token_list[0])),
            patch.object(Network, '_convert_for_internal')
        ]):
            self.network_score.tokenFallback(from_address, value, b'conversionResult')
            self.network_score._convert_for_internal.assert_not_called()

        # failure case: input None data to the _data
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.connector_token_list[0])),
            patch.object(Network, '_convert_for_internal')
        ]):
            self.assertRaises(RevertException,
                              self.network_score.tokenFallback,
                              from_address, value, b'None')

            self.assertRaises(RevertException,
                              self.network_score.tokenFallback,
                              from_address, value, None)

        # failure case: msg.sender is not equal to path[0] ( should be equal )
        msg_sender = Address.from_string("cx" + "c" * 40)
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(msg_sender)),
            patch.object(Network, '_convert_for_internal')
        ]):
            self.assertRaises(RevertException,
                              self.network_score.tokenFallback,
                              from_address, value, decoded_data)

        # success case: input valid data
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.connector_token_list[0])),
            patch.object(Network, '_convert_for_internal'),
            patch.object(Network, '_require_valid_path'),
            patch('contracts.network.network.require_positive_value'),
            patch('contracts.network.network.require_valid_address'),
        ]) as mocks:
            self.network_score.tokenFallback(from_address, value, decoded_data)
            mocks[3].assert_called()  # patched mock of require_positive_value
            mocks[4].assert_called()  # patched mock of require_valid_address
            self.network_score._require_valid_path.assert_called_with(converted_path)
            self.network_score._convert_for_internal. \
                assert_called_with(converted_path, value, min_return, for_address)

    def test_convert_for_internal(self):
        min_return = 10
        amount_to_convert = 5
        convert_result_amount = 10
        for_address = Address.from_string("hx" + "a" * 40)

        icx_token_score_interface = \
            self.network_score.create_interface_score(self.icx_token, ProxyScore(ABCIcxToken))
        icx_token_score_interface.withdrawTo = PropertyMock()

        irc_token_score_interface = \
            self.network_score.create_interface_score(self.connector_token_list[0], ProxyScore(ABCIRCToken))
        irc_token_score_interface.transfer = PropertyMock()

        # success case: finally converted token is Icx token ( Icx token SCORE's 'withdrawTo' method should be called )
        converted_path = [self.connector_token_list[0], self.smart_token_address_list[0], self.icx_token]
        # '_convert_by_path' method returns 'to' token Address, and converted amount
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.network_owner)),
            patch.object(Network, '_convert_by_path', return_value=(self.icx_token, convert_result_amount)),
            patch.object(Network, 'create_interface_score', return_value=icx_token_score_interface)
        ]):
            # register icx_token
            self.network_score._icx_tokens[self.icx_token] = True

            self.network_score._convert_for_internal(converted_path, amount_to_convert, min_return, for_address)
            icx_token_score_interface.withdrawTo.assert_called_with(convert_result_amount, for_address)

        # success case: finally converted token is irc token ( token SCORE's 'transfer' method should be called )
        converted_path = [self.icx_token, self.smart_token_address_list[0], self.connector_token_list[1]]
        # '_convert_by_path' method returns 'to' token Address, and converted amount
        with MultiPatch([
            patch_property(IconScoreBase, 'msg', Message(self.network_owner)),
            patch.object(Network, '_convert_by_path', return_value=(self.connector_token_list[1], convert_result_amount)),
            patch.object(Network, 'create_interface_score', return_value=irc_token_score_interface)
        ]):
            self.network_score._convert_for_internal(converted_path, amount_to_convert, min_return, for_address)
            irc_token_score_interface.transfer.assert_called_with(for_address, convert_result_amount, b'None')

    def test_convert_by_path(self):
        # success case: check all other SCORE's methods called correctly
        # in this path, 'smart token' is 1, 3, 'from token' is 0, 2, 'to token' is 2, 4 ( index )
        converted_path = [self.connector_token_list[0], self.smart_token_address_list[0], self.connector_token_list[1],
                          self.smart_token_address_list[1], self.connector_token_list[2]]
        for_address = Address.from_string("hx" + "a" * 40)

        # this method substitutes 'create_interface_score' method of IconScoreBase
        def create_interface_score_mock(token_address, interface_score):
            if interface_score.__name__ == 'ProxyScore(ABCSmartToken)':
                # add getOwner method to the token address instance
                # this token instance operates as a converter interface score
                token_address.getOwner = Mock(return_value="{0} converter address".format(token_address))
            else:
                # add 'transfer' and 'balanceOf' methods to token address
                # this token instance operates as an IRC token interface score
                token_address.transfer = PropertyMock()
                token_address.balanceOf = PropertyMock(return_value=0)
            return token_address

        with patch_property(IconScoreBase, 'msg', Message(self.network_owner)):
            # the amount is set to 0. in this unit test, do not check the exact return value
            # just check whether if specific methods have been called or not
            amount = 0
            min_return = 10

            self.network_score.create_interface_score = create_interface_score_mock
            actual_to_token, actual_amount = self.network_score.\
                _convert_by_path(converted_path, amount, min_return, for_address)
            self.assertEqual(converted_path[-1], actual_to_token)
            self.assertEqual(amount, actual_amount)
            # check smart token's 'getOwner' method have been called ( smart token's index is 1, 3 )
            for i, smart_token in enumerate(converted_path):
                if i % 2 == 1:
                    smart_token.getOwner.assert_called_once()

            # check 'from' token's 'transfer' method have been called ( from token's index is 0, 2 )
            for i, from_token in enumerate(converted_path):
                if i % 2 == 0 and i != len(converted_path) - 1:
                    data = dict()
                    data["toToken"] = str(converted_path[i+2])
                    # in the last converting, minReturn should be user inputted data (10)
                    data["minReturn"] = min_return if i == len(converted_path) - 3 else 1
                    encoded_data = json_dumps(data).encode()
                    from_token.transfer.assert_called_once_with("{0} converter address".format(converted_path[i + 1]),
                                                                amount, encoded_data)

            # check 'to' token's getBalanceOf method have been called ( to token's index is 2, 4 )
            for i, from_token in enumerate(converted_path):
                if i % 2 == 0 and i != 0:
                    # 'balanceOf' method should be called twice
                    from_token.balanceOf.assert_called()

    def test_getExpectedReturnByPath(self):
        # failure case: input invalid path data ( associated with '/' )
        amount = 10
        invalid_path = "{0}/{1}/{2}".format(str(self.connector_token_list[0]),
                                            str(self.smart_token_address_list[0]),
                                            str(self.connector_token_list[1]))
        self.assertRaises(InvalidParamsException,
                          self.network_score.getExpectedReturnByPath,
                          invalid_path, amount)

        # failure case: input invalid path ( has a invalid address as an element )
        amount = 10
        invalid_path = "{0},{1},{2}".format(str(self.connector_token_list[0]),
                                            str("invalid_address"),
                                            str(self.connector_token_list[1]))
        self.assertRaises(InvalidParamsException,
                          self.network_score.getExpectedReturnByPath,
                          invalid_path, amount)

        # failure case: amount is less than 0
        invalid_amount = -1
        path = "{0},{1},{2}".format(str(self.connector_token_list[0]),
                                    str(self.smart_token_address_list[0]),
                                    str(self.connector_token_list[1]))
        self.assertRaises(RevertException,
                          self.network_score.getExpectedReturnByPath,
                          path, invalid_amount)

        # success case: input valid path and amount
        converted_path = [self.connector_token_list[0], self.smart_token_address_list[0], self.connector_token_list[1],
                          self.smart_token_address_list[1], self.connector_token_list[2]]
        stringed_path = ",".join([str(address) for address in converted_path])
        amount = 10

        def create_interface_score_mock(token_address, interface_score):
            if interface_score.__name__ == "ProxyScore(ABCSmartToken)":
                token_address.getOwner = Mock(return_value=token_address)
                return token_address

            # return converted_path's address instance ( to verify getReturn called or not )
            for index, address in enumerate(converted_path):
                if token_address == address:
                    address.getReturn = Mock(return_value={"amount": amount + index, "fee": 0})
                    return address

        with patch_property(IconScoreBase, 'msg', Message(self.network_owner)):
            self.network_score.create_interface_score = create_interface_score_mock

            actual_amount = self.network_score.getExpectedReturnByPath(stringed_path, amount)
            expected_final_amount = amount + len(converted_path) - 2
            # finally converted amount should be initial amount(10) + last smart token index number(3)
            self.assertEqual(expected_final_amount, actual_amount)
            expected_intermediate_amount = 10
            for i in range(1, len(converted_path), 2):
                converted_path[i].getReturn.\
                    assert_called_with(converted_path[i-1], converted_path[i+1], expected_intermediate_amount)
                expected_intermediate_amount += i
