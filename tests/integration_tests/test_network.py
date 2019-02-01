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
from iconservice.base.exception import RevertException
from tbears.libs.icon_integrate_test import Account

from tests.integration_tests.utils import *


class TestNetwork(IconIntegrateTestBase):
    _INITIAL_ICX_SEND_AMOUNT = 2000
    _ICX_DECIMALS = 10 ** 18

    _INITIAL_FT1_TOKEN_TOTAL_SUPPLY = 2000
    _FT1_DECIMALS = 18

    _INITIAL_FT2_TOKEN_TOTAL_SUPPLY = 2000
    _FT2_DECIMALS = 18

    _FT1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT = 1000 * _ICX_DECIMALS
    _FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT = 1000 * 10 ** _FT1_DECIMALS

    _FT2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT = 1000 * _ICX_DECIMALS
    _FT2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT = 1000 * 10 ** _FT2_DECIMALS

    _CLIENT_FT1_TOKEN_AMOUNT = _INITIAL_FT1_TOKEN_TOTAL_SUPPLY * 10 ** _FT1_DECIMALS - \
                               _FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT
    _CLIENT_FT2_TOKEN_AMOUNT = _INITIAL_FT2_TOKEN_TOTAL_SUPPLY * 10 ** _FT2_DECIMALS - \
                               _FT2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT

    # TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"

    # todo: implement checking method which get path as a params and checking automatically
    def setUp(self, **kwargs):
        self.icon_service = None
        self.network_owner_wallet = KeyWallet.create()
        self.network_owner_address = self.network_owner_wallet.get_address()

        genesis_account_list = [
            Account("network_owner", Address.from_string(self.network_owner_address), 1_000_000 * self._icx_factor)
        ]
        super().setUp(genesis_account_list)

        update_governance(icon_integrate_test_base=super(), from_=self._test1, params={})

        # Adds import white list
        params = {"importStmt": "{'iconservice.iconscore.icon_score_constant' : ['T']}"}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self._test1,
                         to_=str(GOVERNANCE_SCORE_ADDRESS),
                         method="addImportWhiteList",
                         params=params)

        # if you want to send request to network, uncomment next line
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # # setting registry SCORE

        # deploy registry SCORE
        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("score_registry"),
                                        from_=self.network_owner_wallet,
                                        params={})
        self.score_registry_address = deploy_tx_result["scoreAddress"]

        # # setting Icx token SCORE

        # deploy Icx token
        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("icx_token"),
                                        from_=self.network_owner_wallet,
                                        params={})
        self.icx_token_address = deploy_tx_result["scoreAddress"]

        # send Icx to Icx token (issue icx token)
        icx_transfer_call(icon_integrate_test_base=super(),
                          from_=self.network_owner_wallet,
                          to_=self.icx_token_address,
                          value=self._INITIAL_ICX_SEND_AMOUNT * self._ICX_DECIMALS)

        actual_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.icx_token_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})
        self.assertEqual(hex(self._INITIAL_ICX_SEND_AMOUNT * self._ICX_DECIMALS), actual_icx_token_amount)

        # # setting flexible token SCOREs

        # deploy FT1, FT2 token
        self.ft1_token_name = 'flexible_token_1'
        self.ft1_token_symbol = 'FT1'
        self.ft1_token_init_supply = hex(self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY)
        self.ft1_token_decimals = hex(self._FT1_DECIMALS)
        deploy_params = {"_name": self.ft1_token_name,
                         "_symbol": self.ft1_token_symbol,
                         "_initialSupply": self.ft1_token_init_supply,
                         "_decimals": self.ft1_token_decimals}

        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("flexible_token"),
                                        from_=self.network_owner_wallet,
                                        params=deploy_params)

        self.flexible_token_1_address = deploy_tx_result["scoreAddress"]

        self.ft2_token_name = 'flexible_token_2'
        self.ft2_token_symbol = 'FT2'
        self.ft2_token_init_supply = hex(self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY)
        self.ft2_token_decimals = hex(self._FT2_DECIMALS)
        deploy_params = {"_name": self.ft2_token_name,
                         "_symbol": self.ft2_token_symbol,
                         "_initialSupply": self.ft2_token_init_supply,
                         "_decimals": self.ft2_token_decimals}

        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("flexible_token"),
                                        from_=self.network_owner_wallet,
                                        params=deploy_params)

        self.flexible_token_2_address = deploy_tx_result["scoreAddress"]

        # # setting FT1 converter SCORE

        # deploy FT1 converter
        deploy_params = {"_token": str(self.flexible_token_1_address),
                         "_registry": str(self.score_registry_address),
                         "_maxConversionFee": 0,
                         "_connectorToken": str(self.icx_token_address),
                         "_connectorWeight": 500000}

        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("converter"),
                                        from_=self.network_owner_wallet,
                                        params=deploy_params)
        self.ft1_converter_address = deploy_tx_result['scoreAddress']

        # add connector (ft2 token)
        send_tx_params = {"_token": str(self.flexible_token_2_address),
                          "_weight": 500000,
                          "_enableVirtualBalance": int(False)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.ft1_converter_address,
                         method="addConnector",
                         params=send_tx_params)

        # send icx_token to ft1 converter
        send_tx_params = {"_to": str(self.ft1_converter_address),
                          "_value": self._FT1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.icx_token_address,
                         method="transfer",
                         params=send_tx_params)

        actual_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.icx_token_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.ft1_converter_address)})
        self.assertEqual(hex(self._FT1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT), actual_icx_token_amount)

        # send ft2 token to ft1 converter
        send_tx_params = {"_to": str(self.ft1_converter_address),
                          "_value": self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        actual_ft2_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.ft1_converter_address)})
        self.assertEqual(hex(self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT), actual_ft2_token_amount)

        # transfer ownership of flexible token 1 to ft1 converter
        send_tx_params = {"_newOwner": str(self.ft1_converter_address)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_1_address,
                         method="transferOwnerShip",
                         params=send_tx_params)

        # accept ownership of flexible token 1
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.ft1_converter_address,
                         method="acceptTokenOwnership",
                         params={})

        # check if the converter activated
        actual_activation = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.ft1_converter_address,
                                     method="isActive",
                                     params={})
        self.assertEqual(hex(True), actual_activation)

        # # setting FT2 converter SCORE

        # deploy FT2 converter
        deploy_params = {"_token": str(self.flexible_token_2_address),
                         "_registry": str(self.score_registry_address),
                         "_maxConversionFee": 0,
                         "_connectorToken": str(self.icx_token_address),
                         "_connectorWeight": 500000}

        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("converter"),
                                        from_=self.network_owner_wallet,
                                        params=deploy_params)
        self.ft2_converter_address = deploy_tx_result['scoreAddress']

        # add connector (ft1 token)
        send_tx_params = {"_token": str(self.flexible_token_1_address),
                          "_weight": 500000,
                          "_enableVirtualBalance": int(False)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.ft2_converter_address,
                         method="addConnector",
                         params=send_tx_params)

        # send icx_token and ft1 token to ft2 converter
        send_tx_params = {"_to": str(self.ft2_converter_address),
                          "_value": self._FT2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.icx_token_address,
                         method="transfer",
                         params=send_tx_params)

        actual_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.icx_token_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.ft2_converter_address)})
        self.assertEqual(hex(self._FT2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT), actual_icx_token_amount)

        # send ft1 token to ft2 converter
        send_tx_params = {"_to": str(self.ft2_converter_address),
                          "_value": self._FT2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_1_address,
                         method="transfer",
                         params=send_tx_params)

        actual_ft1_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.ft2_converter_address)})
        self.assertEqual(hex(self._FT2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT), actual_ft1_token_amount)

        # transfer ownership of flexible token 2 to ft2 converter
        send_tx_params = {"_newOwner": str(self.ft2_converter_address)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_2_address,
                         method="transferOwnerShip",
                         params=send_tx_params)

        # accept ownership of flexible token 2
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.ft2_converter_address,
                         method="acceptTokenOwnership",
                         params={})

        # check if the converter activated
        actual_activation = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.ft2_converter_address,
                                     method="isActive",
                                     params={})
        self.assertEqual(hex(True), actual_activation)

        # # setting network SCORE

        # deploy network
        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("network"),
                                        from_=self.network_owner_wallet,
                                        params={})
        self.network_score_address = deploy_tx_result['scoreAddress']

        # register icx token
        send_tx_params = {"_icxToken": str(self.icx_token_address), "_register": int(True)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.network_score_address,
                         method="registerIcxToken",
                         params=send_tx_params)

        actual_icx_token_registered = icx_call(icon_integrate_test_base=super(),
                                               from_=self.network_owner_wallet.get_address(),
                                               to_=self.network_score_address,
                                               method="getIcxTokenRegistered",
                                               params={"_icxToken": str(self.icx_token_address)})
        self.assertEqual(hex(True), actual_icx_token_registered)

        # register network to score_registry
        send_tx_params = {"_scoreName": "Network", "_scoreAddress": str(self.network_score_address)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.score_registry_address,
                         method="registerAddress",
                         params=send_tx_params)

        # check if the network score registered correctly
        actual_registered_network_address = icx_call(icon_integrate_test_base=super(),
                                                     from_=self.network_owner_wallet.get_address(),
                                                     to_=self.score_registry_address,
                                                     method="getAddress",
                                                     params={"_scoreName": "Network"})
        self.assertEqual(str(self.network_score_address), actual_registered_network_address)

    def test_getExpectedReturn_short_path(self):
        # success case: check if the expected return amount is equal to actual converting result (short path)
        converting_ft2_amount = 10
        min_return = 1
        buy_path = "{0},{1},{2}".format(str(self.flexible_token_2_address),
                                        str(self.flexible_token_1_address),
                                        str(self.flexible_token_1_address))

        expected_return_amount = icx_call(icon_integrate_test_base=super(),
                                          from_=self.network_owner_wallet.get_address(),
                                          to_=self.network_score_address,
                                          method="getExpectedReturnByPath",
                                          params={"_path": buy_path,
                                                  "_amount": converting_ft2_amount})

        before_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        converting_params = {"path": buy_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        after_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})

        actual_issued_ft1_amount = int(after_client_ft1_amount, 16) - int(before_client_ft1_amount, 16)
        self.assertEqual(int(expected_return_amount, 16), actual_issued_ft1_amount)

    def test_getExpectedReturn_long_path(self):
        # success case: check if the expected return amount is equal to actual converting result (long path)
        converting_ft2_amount = 10
        min_return = 1
        long_path = "{0},{1},{2},{3},{4}".format(self.flexible_token_2_address,
                                                 self.flexible_token_1_address,
                                                 self.icx_token_address,
                                                 self.flexible_token_2_address,
                                                 self.flexible_token_1_address)

        before_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        expected_return_amount = icx_call(icon_integrate_test_base=super(),
                                          from_=self.network_owner_wallet.get_address(),
                                          to_=self.network_score_address,
                                          method="getExpectedReturnByPath",
                                          params={"_path": long_path,
                                                  "_amount": converting_ft2_amount})

        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        after_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})

        actual_received_ft1_amount = int(after_client_ft1_amount, 16) - int(before_client_ft1_amount, 16)
        self.assertEqual(int(expected_return_amount, 16), actual_received_ft1_amount)

    def test_getExpectedReturn_input_invalid_convert_path(self):
        # failure case: input path which invalid length
        converting_ft2_amount = 10
        invalid_path = "{0},{1}".format(self.flexible_token_2_address,
                                        self.flexible_token_1_address)

        self.assertRaises(RevertException, icx_call,
                          super(),
                          self.network_owner_wallet.get_address(),
                          self.network_score_address,
                          "getExpectedReturnByPath",
                          {"_path": invalid_path,
                           "_amount": converting_ft2_amount})

        invalid_score_address = Address.from_string("cx" + "0" * 40)
        invalid_path = "{0},{1},{2}".format(self.flexible_token_2_address,
                                            self.flexible_token_1_address,
                                            invalid_score_address)

        # failure case: input the path which involves the not existed score address (when from is token)
        self.assertRaises(RevertException, icx_call,
                          super(),
                          self.network_owner_wallet.get_address(),
                          self.network_score_address,
                          "getExpectedReturnByPath",
                          {"_path": invalid_path,
                           "_amount": converting_ft2_amount})

    def test_convert_input_invalid_convert_path(self):
        # failure case: input the path which involves the not existed score address (when from is icx)
        invalid_score_address = Address.from_string("cx" + "0" * 40)

        converting_icx_amount = 10
        invalid_path = "{0},{1},{2}".format(self.icx_token_address,
                                            self.flexible_token_1_address,
                                            invalid_score_address)
        min_return = 1
        send_tx_params = {"_path": invalid_path,
                          "_minReturn": min_return}
        self.assertRaises(AssertionError, transaction_call,
                          super(),
                          self.network_owner_wallet,
                          self.network_score_address,
                          "convert",
                          send_tx_params,
                          converting_icx_amount)

        # failure case: input the path which involves the not existed score address (when from is token)
        converting_ft2_amount = 10
        invalid_path = "{0},{1},{2}".format(self.flexible_token_2_address,
                                            self.flexible_token_1_address,
                                            invalid_score_address)
        min_return = 1
        converting_params = {"path": invalid_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}

        self.assertRaises(AssertionError, transaction_call,
                          super(),
                          self.network_owner_wallet,
                          self.flexible_token_2_address,
                          "transfer",
                          send_tx_params)

        # failure case: input the invalid path (when from is icx)
        converting_icx_amount = 10
        invalid_path = "{0},{1}".format(self.icx_token_address,
                                        self.flexible_token_1_address)
        min_return = 1
        send_tx_params = {"_path": invalid_path,
                          "_minReturn": min_return}
        self.assertRaises(AssertionError, transaction_call,
                          super(),
                          self.network_owner_wallet,
                          self.network_score_address,
                          "convert",
                          send_tx_params,
                          converting_icx_amount)

        # failure case: input the invalid path (when from is token)
        converting_ft2_amount = 10
        invalid_path = "{0},{1}".format(self.flexible_token_2_address,
                                        self.flexible_token_1_address)
        min_return = 1
        converting_params = {"path": invalid_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}

        self.assertRaises(AssertionError, transaction_call,
                          super(),
                          self.network_owner_wallet,
                          self.flexible_token_2_address,
                          "transfer",
                          send_tx_params)

    def test_convert_less_than_min_return(self):
        # failure case: converted token amount is less than min return
        converting_icx_amount = 10
        invalid_ = "{0},{1},{2}".format(self.icx_token_address,
                                        self.flexible_token_1_address,
                                        self.flexible_token_2_address)
        min_return = 100
        send_tx_params = {"_path": invalid_,
                          "_minReturn": min_return}
        self.assertRaises(AssertionError, transaction_call,
                          super(),
                          self.network_owner_wallet,
                          self.network_score_address,
                          "convert",
                          send_tx_params,
                          converting_icx_amount)

    def test_convertFor(self):
        receiver_address: Address = Address.from_string("hx" + "0" * 40)
        # success case: icx coin convert 'for'
        before_receiver_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                              from_=self.network_owner_wallet.get_address(),
                                              to_=self.flexible_token_2_address,
                                              method="balanceOf",
                                              params={"_owner": str(receiver_address)})

        converting_icx_amount = 10
        cross_path = "{0},{1},{2}".format(self.icx_token_address,
                                          self.flexible_token_1_address,
                                          self.flexible_token_2_address)
        min_return = 1
        send_tx_params = {"_path": cross_path,
                          "_minReturn": min_return,
                          "_for": str(receiver_address)}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.network_score_address,
                         method="convertFor",
                         value=converting_icx_amount,
                         params=send_tx_params)

        # check receiver's ft2 token amount
        after_receiver_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                             from_=self.network_owner_wallet.get_address(),
                                             to_=self.flexible_token_2_address,
                                             method="balanceOf",
                                             params={"_owner": str(receiver_address)})

        received_ft2_amount = int(after_receiver_ft2_amount, 16) - int(before_receiver_ft2_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_ft2_amount, 0)

        # success case: token convert 'for'
        before_receiver_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                     address=str(receiver_address))

        converting_ft2_amount = 10
        buy_path = "{0},{1},{2}".format(str(self.flexible_token_2_address),
                                        str(self.flexible_token_1_address),
                                        str(self.icx_token_address))
        min_return = 1
        converting_params = {"path": buy_path,
                             "minReturn": min_return,
                             "for": str(receiver_address)}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        after_receiver_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                    address=str(receiver_address))

        received_icx_amount = int(after_receiver_icx_amount, 16) - int(before_receiver_icx_amount, 16)
        self.assertGreater(received_icx_amount, 0)

    def test_convert_with_short_path_buy(self):
        # test using FT1 converter
        # success case: buy ft1(flexible token) token with ft2(connector token)
        before_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        converting_ft2_amount = 10
        buy_path = "{0},{1},{2}".format(str(self.flexible_token_2_address),
                                        str(self.flexible_token_1_address),
                                        str(self.flexible_token_1_address))
        min_return = 1
        converting_params = {"path": buy_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        # check client's flexible token 1 amount after converting
        after_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})

        # todo: should check exact value
        issued_ft1_amount = int(after_client_ft1_amount, 16) - int(before_client_ft1_amount, 16)
        self.assertGreater(issued_ft1_amount, 0)

        # check client's flexible token 2 amount after converting
        after_client_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})

        self.assertEqual(self._CLIENT_FT2_TOKEN_AMOUNT - converting_ft2_amount,
                         int(after_client_ft2_amount, 16))

        # check ft1 converter's flexible token 2 amount
        converter_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                        from_=self.network_owner_wallet.get_address(),
                                        to_=self.flexible_token_2_address,
                                        method="balanceOf",
                                        params={"_owner": str(self.ft1_converter_address)})
        self.assertEqual(self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_ft2_amount,
                         int(converter_ft1_amount, 16))

        # check flexible token 1's total supply
        ft1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS + issued_ft1_amount,
                         int(ft1_total_supply, 16))

    def test_convert_with_short_path_sell(self):
        # test using FT1 converter
        # success case: sell ft1 (flexible token) token to buy ft2(connector token)
        before_client_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        converting_ft1_token_amount = 10
        sell_path = "{0},{1},{2}".format(str(self.flexible_token_1_address),
                                         str(self.flexible_token_1_address),
                                         str(self.flexible_token_2_address))
        min_return = 1
        converting_params = {"path": sell_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_ft1_token_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_1_address,
                         method="transfer",
                         params=send_tx_params)

        # check client's flexible token 2 amount after converting
        after_client_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})
        # todo: should check exact value
        received_ft2_amount = int(after_client_ft2_amount, 16) - int(before_client_ft2_amount, 16)
        self.assertGreater(received_ft2_amount, 0)

        # check client's flexible token 1 amount after converting
        after_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})
        self.assertEqual(self._CLIENT_FT1_TOKEN_AMOUNT - converting_ft1_token_amount,
                         int(after_client_ft1_amount, 16))

        # check ft1 converter's flexible token 2 amount
        converter_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                        from_=self.network_owner_wallet.get_address(),
                                        to_=self.flexible_token_2_address,
                                        method="balanceOf",
                                        params={"_owner": str(self.ft1_converter_address)})
        self.assertEqual(self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_ft2_amount,
                         int(converter_ft2_amount, 16))

        # check flexible token 1's total supply
        ft1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS - converting_ft1_token_amount,
                         int(ft1_total_supply, 16))

    def test_convert_with_short_path_cross_token_to_icx(self):
        # test using FT1 converter
        # success case: convert ft2 token to Icx coin
        before_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                   address=self.network_owner_address)

        converting_ft2_amount = 10
        cross_path = "{0},{1},{2}".format(self.flexible_token_2_address,
                                          self.flexible_token_1_address,
                                          self.icx_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        # check client's Icx coin amount
        after_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                  address=self.network_owner_address)
        received_icx_amount = int(after_client_icx_amount, 16) - int(before_client_icx_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_icx_amount, 0)

        # check client's Icx token amount (should be 0)
        client_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.icx_token_address,
                                           method="balanceOf",
                                           params={"_owner": self.network_owner_address})

        self.assertEqual(0, int(client_icx_token_amount, 16))

        # check converter's Icx token amount
        converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                              from_=self.network_owner_wallet.get_address(),
                                              to_=self.icx_token_address,
                                              method="balanceOf",
                                              params={"_owner": self.ft1_converter_address})
        self.assertEqual(self._FT1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT - received_icx_amount,
                         int(converter_icx_token_amount, 16))

        # check converter's ft2 token amount
        converter_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                        from_=self.network_owner_wallet.get_address(),
                                        to_=self.flexible_token_2_address,
                                        method="balanceOf",
                                        params={"_owner": self.ft1_converter_address})

        self.assertEqual(self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_ft2_amount,
                         int(converter_ft2_amount, 16))

        # check flexible token 1's total supply (should not be changed)
        ft1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS,
                         int(ft1_total_supply, 16))

    def test_convert_with_short_path_cross_icx_to_token(self):
        # test using FT1 converter
        # success case: convert Icx coin to ft2 token
        before_client_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": self.network_owner_address})

        converting_icx_amount = 10
        cross_path = "{0},{1},{2}".format(self.icx_token_address,
                                          self.flexible_token_1_address,
                                          self.flexible_token_2_address)
        min_return = 1
        send_tx_params = {"_path": cross_path,
                          "_minReturn": min_return}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.network_score_address,
                         method="convert",
                         value=converting_icx_amount,
                         params=send_tx_params)

        # check converter's icx token amount
        converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                              from_=self.network_owner_wallet.get_address(),
                                              to_=self.icx_token_address,
                                              method="balanceOf",
                                              params={"_owner": self.ft1_converter_address})
        self.assertEqual(self._FT1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT + converting_icx_amount,
                         int(converter_icx_token_amount, 16))

        # check client's ft2 token amount
        after_client_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": self.network_owner_address})

        received_ft2_amount = int(after_client_ft2_amount, 16) - int(before_client_ft2_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_ft2_amount, 0)

        # check converter's ft2 token amount
        converter_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                        from_=self.network_owner_wallet.get_address(),
                                        to_=self.flexible_token_2_address,
                                        method="balanceOf",
                                        params={"_owner": self.ft1_converter_address})
        self.assertEqual(self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_ft2_amount,
                         int(converter_ft2_amount, 16))

        # check flexible token 1's total supply (should not be changed)
        ft1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS,
                         int(ft1_total_supply, 16))

    def test_convert_with_long_path_sell_sell(self):
        # success case: convert ft1 - ft2 - icx
        before_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                   address=self.network_owner_address)
        converting_ft1_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.flexible_token_1_address,
                                                 self.flexible_token_1_address,
                                                 self.flexible_token_2_address,
                                                 self.flexible_token_2_address,
                                                 self.icx_token_address)
        min_return = 1
        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_ft1_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_1_address,
                         method="transfer",
                         params=send_tx_params)

        # check ft1_total supply
        ft1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_1_address,
                                    method="totalSupply",
                                    params={})

        self.assertEqual(self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS - converting_ft1_amount,
                         int(ft1_total_supply, 16))

        # check client ft1 token amount
        client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.flexible_token_1_address,
                                     method="balanceOf",
                                     params={"_owner": self.network_owner_address})

        self.assertEqual(self._CLIENT_FT1_TOKEN_AMOUNT - converting_ft1_amount,
                         int(client_ft1_amount, 16))

        # check client icx coin amount
        after_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                  address=self.network_owner_address)

        received_client_icx_amount = int(after_client_icx_amount, 16) - int(before_client_icx_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_client_icx_amount, 0)
        # check ft2 converter's icx token amount
        ft2_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.ft2_converter_address})

        self.assertEqual(self._FT2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT - received_client_icx_amount,
                         int(ft2_converter_icx_token_amount, 16))

    def test_convert_with_long_path_sell_buy(self):
        # success case: convert ft1 - icx - ft2
        converting_ft1_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.flexible_token_1_address,
                                                 self.flexible_token_1_address,
                                                 self.icx_token_address,
                                                 self.flexible_token_2_address,
                                                 self.flexible_token_2_address)
        min_return = 1
        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_ft1_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_1_address,
                         method="transfer",
                         params=send_tx_params)

        # check ft1_total supply
        ft1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_1_address,
                                    method="totalSupply",
                                    params={})

        self.assertEqual(self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS - converting_ft1_amount,
                         int(ft1_total_supply, 16))

        # check client ft1 token amount
        client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.flexible_token_1_address,
                                     method="balanceOf",
                                     params={"_owner": self.network_owner_address})

        self.assertEqual(self._CLIENT_FT1_TOKEN_AMOUNT - converting_ft1_amount,
                         int(client_ft1_amount, 16))

        # check client's ft2 amount
        client_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.flexible_token_2_address,
                                     method="balanceOf",
                                     params={"_owner": self.network_owner_address})

        received_ft2_amount = int(client_ft2_amount, 16) - self._CLIENT_FT2_TOKEN_AMOUNT
        # todo: should check exact value
        self.assertGreater(received_ft2_amount, 0)

        # check ft2 total supply
        ft2_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_2_address,
                                    method="totalSupply",
                                    params={})

        self.assertEqual(self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY * 10 ** self._FT2_DECIMALS + received_ft2_amount,
                         int(ft2_total_supply, 16))

    def test_convert_with_long_path_sell_cross(self):
        # success case: convert ft1 - icx - ft1
        converting_ft1_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.flexible_token_1_address,
                                                 self.flexible_token_1_address,
                                                 self.icx_token_address,
                                                 self.flexible_token_2_address,
                                                 self.flexible_token_1_address)
        min_return = 1
        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_ft1_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_1_address,
                         method="transfer",
                         params=send_tx_params)

        # check ft1_total supply
        ft1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_1_address,
                                    method="totalSupply",
                                    params={})

        self.assertEqual(self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS - converting_ft1_amount,
                         int(ft1_total_supply, 16))

        # check client's ft1 token amount 's difference between before with after converting
        # (should get less amount than before converting)
        client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.flexible_token_1_address,
                                     method="balanceOf",
                                     params={"_owner": self.network_owner_address})

        client_ft1_amount_except_converting = self._CLIENT_FT1_TOKEN_AMOUNT - converting_ft1_amount
        received_client_ft1_amount = int(client_ft1_amount, 16) - client_ft1_amount_except_converting
        # todo: should check exact value
        self.assertLess(received_client_ft1_amount, converting_ft1_amount)

        # check ft2 converter's ft1 token amount
        ft2_converter_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": self.ft2_converter_address})

        self.assertEqual(self._FT2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_client_ft1_amount,
                         int(ft2_converter_ft1_amount, 16))

    def test_convert_with_long_path_buy_buy(self):
        # success case: convert icx - ft2 - ft1
        # ft2 converter - ft1 converter
        before_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": self.network_owner_address})

        converting_icx_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.icx_token_address,
                                                 self.flexible_token_2_address,
                                                 self.flexible_token_2_address,
                                                 self.flexible_token_1_address,
                                                 self.flexible_token_1_address)
        min_return = 1
        send_tx_params = {"_path": long_path,
                          "_minReturn": min_return}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.network_score_address,
                         method="convert",
                         value=converting_icx_amount,
                         params=send_tx_params)

        # check ft2 converter's icx token amount
        ft2_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.ft2_converter_address})

        self.assertEqual(self._FT2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT + converting_icx_amount,
                         int(ft2_converter_icx_token_amount, 16))

        # check client's ft1 token amount
        after_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": self.network_owner_address})
        received_ft1_amount = int(after_client_ft1_amount, 16) - int(before_client_ft1_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_ft1_amount, 0)

        # check ft1 converter's ft2 token amount
        ft1_converter_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": self.ft1_converter_address})

        self.assertGreater(int(ft1_converter_ft2_amount, 16),
                           self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT)

    def test_convert_with_long_path_buy_cross(self):
        # success case: convert icx - ft1 - icx
        before_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                   address=self.network_owner_address)
        converting_icx_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.icx_token_address,
                                                 self.flexible_token_1_address,
                                                 self.flexible_token_1_address,
                                                 self.flexible_token_2_address,
                                                 self.icx_token_address)
        min_return = 1
        send_tx_params = {"_path": long_path,
                          "_minReturn": min_return}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.network_score_address,
                         method="convert",
                         value=converting_icx_amount,
                         params=send_tx_params)

        # check client's icx amount's difference between before with after converting
        # (should get less amount than before converting)
        after_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                  address=self.network_owner_address)
        client_icx_amount_except_converting = int(before_client_icx_amount, 16) - converting_icx_amount
        received_icx_amount = int(after_client_icx_amount, 16) - client_icx_amount_except_converting
        # todo: should check exact value
        self.assertLess(received_icx_amount, converting_icx_amount)

        # check ft1 converter's icx token amount
        ft1_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.ft1_converter_address})

        self.assertEqual(self._FT1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT + converting_icx_amount,
                         int(ft1_converter_icx_token_amount, 16))

        # check ft2 converter's icx token amount
        ft2_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.ft2_converter_address})

        self.assertEqual(self._FT2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT - received_icx_amount,
                         int(ft2_converter_icx_token_amount, 16))

    def test_convert_with_long_path_cross_sell(self):
        # success case: convert icx – ft2 - ft1
        before_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": self.network_owner_address})

        converting_icx_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.icx_token_address,
                                                 self.flexible_token_1_address,
                                                 self.flexible_token_2_address,
                                                 self.flexible_token_2_address,
                                                 self.flexible_token_1_address)
        min_return = 1
        send_tx_params = {"_path": long_path,
                          "_minReturn": min_return}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.network_score_address,
                         method="convert",
                         value=converting_icx_amount,
                         params=send_tx_params)

        # check ft1 converter's icx token amount
        ft1_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.ft1_converter_address})
        self.assertEqual(self._FT1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT + converting_icx_amount,
                         int(ft1_converter_icx_token_amount, 16))

        # check client's ft1 token amount
        after_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": self.network_owner_address})
        received_ft1_amount = int(after_client_ft1_amount, 16) - int(before_client_ft1_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_ft1_amount, 0)

        # check ft2 converter's ft1 token amount
        ft2_converter_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": self.ft2_converter_address})

        self.assertEqual(self._FT2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_ft1_amount,
                         int(ft2_converter_ft1_amount, 16))

    def test_convert_with_long_path_cross_buy(self):
        # success case: convert ft2 – icx - ft2
        before_client_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": self.network_owner_address})
        converting_ft2_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.flexible_token_2_address,
                                                 self.flexible_token_1_address,
                                                 self.icx_token_address,
                                                 self.flexible_token_2_address,
                                                 self.flexible_token_2_address)
        min_return = 1
        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        # check ft1 converter's ft2 amount
        ft1_converter_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": self.ft1_converter_address})
        self.assertEqual(self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_ft2_amount,
                         int(ft1_converter_ft2_amount, 16))

        # check client's ft2 amount's difference between before with after converting
        # (should get less amount than before converting)
        after_client_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": self.network_owner_address})
        client_icx_amount_except_converting = int(before_client_ft2_amount, 16) - converting_ft2_amount
        received_ft2_amount = int(after_client_ft2_amount, 16) - client_icx_amount_except_converting
        # todo: should check exact value
        self.assertLess(received_ft2_amount, converting_ft2_amount)

        # check ft2 converter's icx token amount
        ft2_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.ft2_converter_address})
        # todo: should check exact value
        self.assertGreater(int(ft2_converter_icx_token_amount, 16),
                           self._FT2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT)

        # check flexible token 2's total supply
        ft2_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_2_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS + received_ft2_amount,
                         int(ft2_total_supply, 16))

    def test_convert_with_long_path_cross_cross(self):
        # success case: convert ft2 - icx - ft1
        before_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        converting_ft2_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.flexible_token_2_address,
                                                 self.flexible_token_1_address,
                                                 self.icx_token_address,
                                                 self.flexible_token_2_address,
                                                 self.flexible_token_1_address)
        min_return = 1
        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        # check ft1 converter's flexible token 2 amount
        converter_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                        from_=self.network_owner_wallet.get_address(),
                                        to_=self.flexible_token_2_address,
                                        method="balanceOf",
                                        params={"_owner": str(self.ft1_converter_address)})
        self.assertEqual(self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_ft2_amount,
                         int(converter_ft1_amount, 16))

        after_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})

        # check client's flexible token 1 amount
        received_ft1_amount = int(after_client_ft1_amount, 16) - int(before_client_ft1_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_ft1_amount, 0)

        # check ft2 converter's flexible token 1 amount
        ft2_converter_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.ft2_converter_address)})

        self.assertEqual(self._FT2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_ft1_amount,
                         int(ft2_converter_ft1_amount, 16))

        # check flexible token 1 total supply (should not be changed)
        ft1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS,
                         int(ft1_total_supply, 16))

        # check flexible token 2 total supply (should not be changed)
        ft2_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_2_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY * 10 ** self._FT2_DECIMALS,
                         int(ft2_total_supply, 16))

    def test_tokenFallback(self):
        # success: input 'conversionResult' as a _data (token should be deposited  on network SCORE)
        token_amount = 10

        send_tx_params = {"_to": self.network_score_address,
                          "_value": token_amount,
                          "_data": b"conversionResult"}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.flexible_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        network_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                      from_=self.network_owner_wallet.get_address(),
                                      to_=self.flexible_token_2_address,
                                      method="balanceOf",
                                      params={"_owner": str(self.network_score_address)})
        self.assertEqual(token_amount, int(network_ft2_amount, 16))

        # failure case: EOA try to call tokenFallback directly
        converting_ft2_amount = 10
        valid_path = "{0},{1},{2}".format(self.flexible_token_2_address,
                                          self.flexible_token_1_address,
                                          self.icx_token_address)
        min_return = 1
        converting_params = {"path": valid_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_from": self.network_owner_address,
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}

        self.assertRaises(AssertionError, transaction_call,
                          super(),
                          self.network_owner_wallet,
                          self.network_score_address,
                          "tokenFallback",
                          send_tx_params)
