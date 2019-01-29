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
from iconsdk.wallet.wallet import KeyWallet
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, Account

from contracts.interfaces.abc_score_registry import ABCScoreRegistry
from tests.integration_tests.utils import *


class TestNetwork(IconIntegrateTestBase):
    _INITIAL_ICX_SEND_AMOUNT = 2000
    _ICX_DECIMALS = 10 ** 18

    _INITIAL_ST1_TOKEN_TOTAL_SUPPLY = 2000
    _ST1_DECIMALS = 18

    _INITIAL_ST2_TOKEN_TOTAL_SUPPLY = 2000
    _ST2_DECIMALS = 18

    _ST1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT = 1000 * _ICX_DECIMALS
    _ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT = 1000 * 10 ** _ST1_DECIMALS

    _ST2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT = 1000 * _ICX_DECIMALS
    _ST2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT = 1000 * 10 ** _ST2_DECIMALS

    _CLIENT_ST1_TOKEN_AMOUNT = _INITIAL_ST1_TOKEN_TOTAL_SUPPLY * 10 ** _ST1_DECIMALS - \
                               _ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT
    _CLIENT_ST2_TOKEN_AMOUNT = _INITIAL_ST2_TOKEN_TOTAL_SUPPLY * 10 ** _ST2_DECIMALS - \
                               _ST2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT

    # TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"

    def setUp(self):
        self.network_owner_wallet = KeyWallet.create()
        self.network_owner_address = self.network_owner_wallet.get_address()

        genesis_account_list = [
            Account("network_owner", Address.from_string(self.network_owner_address), 1_000_000 * self._icx_factor)
        ]
        super().setUp(genesis_account_list)

        self.icon_service = None
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

        # # setting smart token SCOREs

        # deploy ST1, ST2 token
        self.st1_token_name = 'smart_token_1'
        self.st1_token_symbol = 'ST1'
        self.st1_token_init_supply = hex(self._INITIAL_ST1_TOKEN_TOTAL_SUPPLY)
        self.st1_token_decimals = hex(self._ST1_DECIMALS)
        deploy_params = {"_name": self.st1_token_name,
                         "_symbol": self.st1_token_symbol,
                         "_initialSupply": self.st1_token_init_supply,
                         "_decimals": self.st1_token_decimals}

        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("smart_token"),
                                        from_=self.network_owner_wallet,
                                        params=deploy_params)

        self.smart_token_1_address = deploy_tx_result["scoreAddress"]

        self.st2_token_name = 'smart_token_2'
        self.st2_token_symbol = 'ST2'
        self.st2_token_init_supply = hex(self._INITIAL_ST2_TOKEN_TOTAL_SUPPLY)
        self.st2_token_decimals = hex(self._ST2_DECIMALS)
        deploy_params = {"_name": self.st2_token_name,
                         "_symbol": self.st2_token_symbol,
                         "_initialSupply": self.st2_token_init_supply,
                         "_decimals": self.st2_token_decimals}

        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("smart_token"),
                                        from_=self.network_owner_wallet,
                                        params=deploy_params)

        self.smart_token_2_address = deploy_tx_result["scoreAddress"]

        # # setting ST1 converter SCORE

        # deploy ST1 converter
        deploy_params = {"_token": str(self.smart_token_1_address),
                         "_registry": str(self.score_registry_address),
                         "_maxConversionFee": 0,
                         "_connectorToken": str(self.icx_token_address),
                         "_connectorWeight": 500000}

        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("converter"),
                                        from_=self.network_owner_wallet,
                                        params=deploy_params)
        self.st1_converter_address = deploy_tx_result['scoreAddress']

        # add connector (st2 token)
        send_tx_params = {"_token": str(self.smart_token_2_address),
                          "_weight": 500000,
                          "_enableVirtualBalance": int(False)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.st1_converter_address,
                         method="addConnector",
                         params=send_tx_params)

        # send icx_token to st1 converter
        send_tx_params = {"_to": str(self.st1_converter_address),
                          "_value": self._ST1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.icx_token_address,
                         method="transfer",
                         params=send_tx_params)

        actual_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.icx_token_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.st1_converter_address)})
        self.assertEqual(hex(self._ST1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT), actual_icx_token_amount)

        # send st2 token to st1 converter
        send_tx_params = {"_to": str(self.st1_converter_address),
                          "_value": self._ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        actual_st2_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.st1_converter_address)})
        self.assertEqual(hex(self._ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT), actual_st2_token_amount)

        # transfer ownership of smart token 1 to st1 converter
        send_tx_params = {"_newOwner": str(self.st1_converter_address)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_1_address,
                         method="transferOwnerShip",
                         params=send_tx_params)

        # accept ownership of smart token 1
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.st1_converter_address,
                         method="acceptTokenOwnership",
                         params={})

        # check if the converter activated
        actual_activation = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.st1_converter_address,
                                     method="isActive",
                                     params={})
        self.assertEqual(hex(True), actual_activation)

        # # setting ST2 converter SCORE

        # deploy ST2 converter
        deploy_params = {"_token": str(self.smart_token_2_address),
                         "_registry": str(self.score_registry_address),
                         "_maxConversionFee": 0,
                         "_connectorToken": str(self.icx_token_address),
                         "_connectorWeight": 500000}

        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("converter"),
                                        from_=self.network_owner_wallet,
                                        params=deploy_params)
        self.st2_converter_address = deploy_tx_result['scoreAddress']

        # add connector (st1 token)
        send_tx_params = {"_token": str(self.smart_token_1_address),
                          "_weight": 500000,
                          "_enableVirtualBalance": int(False)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.st2_converter_address,
                         method="addConnector",
                         params=send_tx_params)

        # send icx_token and st1 token to st2 converter
        send_tx_params = {"_to": str(self.st2_converter_address),
                          "_value": self._ST2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.icx_token_address,
                         method="transfer",
                         params=send_tx_params)

        actual_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.icx_token_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.st2_converter_address)})
        self.assertEqual(hex(self._ST2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT), actual_icx_token_amount)

        # send st1 token to st2 converter
        send_tx_params = {"_to": str(self.st2_converter_address),
                          "_value": self._ST2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_1_address,
                         method="transfer",
                         params=send_tx_params)

        actual_st1_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.st2_converter_address)})
        self.assertEqual(hex(self._ST2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT), actual_st1_token_amount)

        # transfer ownership of smart token 2 to st2 converter
        send_tx_params = {"_newOwner": str(self.st2_converter_address)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_2_address,
                         method="transferOwnerShip",
                         params=send_tx_params)

        # accept ownership of smart token 2
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.st2_converter_address,
                         method="acceptTokenOwnership",
                         params={})

        # check if the converter activated
        actual_activation = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.st2_converter_address,
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
        send_tx_params = {"_scoreName": "BancorNetwork", "_scoreAddress": str(self.network_score_address)}
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
                                                     params={"_scoreName": "BancorNetwork"})
        self.assertEqual(str(self.network_score_address), actual_registered_network_address)

    def test_convert(self):
        pass

    def test_getExpectedReturn(self):
        pass

    def test_registerIcxToken(self):
        pass

    def test_convert_with_short_path_buy(self):
        # test using ST1 converter
        # success case: buy st1(smart token) token with st2(connector token)
        before_client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        converting_st2_amount = 10
        buy_path = "{0},{1},{2}".format(str(self.smart_token_2_address),
                                        str(self.smart_token_1_address),
                                        str(self.smart_token_1_address))
        min_return = 1
        converting_params = {"path": buy_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_st2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        # check client's smart token 1 amount after converting
        after_client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})

        # todo: should check exact value
        issued_st1_amount = int(after_client_st1_amount, 16) - int(before_client_st1_amount, 16)
        self.assertGreater(issued_st1_amount, 0)

        # check client's smart token 2 amount after converting
        after_client_st2_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})

        self.assertEqual(self._CLIENT_ST2_TOKEN_AMOUNT - converting_st2_amount,
                         int(after_client_st2_amount, 16))

        # check st1 converter's smart token 2 amount
        converter_st1_amount = icx_call(icon_integrate_test_base=super(),
                                        from_=self.network_owner_wallet.get_address(),
                                        to_=self.smart_token_2_address,
                                        method="balanceOf",
                                        params={"_owner": str(self.st1_converter_address)})
        self.assertEqual(self._ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_st2_amount,
                         int(converter_st1_amount, 16))

        # check smart token 1's total supply
        st1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.smart_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_ST1_TOKEN_TOTAL_SUPPLY * 10 ** self._ST1_DECIMALS + issued_st1_amount,
                         int(st1_total_supply, 16))

    def test_convert_with_short_path_sell(self):
        # test using ST1 converter
        # success case: sell st1 (smart token) token to buy st2(connector token)
        before_client_st2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        converting_st1_token_amount = 10
        sell_path = "{0},{1},{2}".format(str(self.smart_token_1_address),
                                         str(self.smart_token_1_address),
                                         str(self.smart_token_2_address))
        min_return = 1
        converting_params = {"path": sell_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_st1_token_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_1_address,
                         method="transfer",
                         params=send_tx_params)

        # check client's smart token 2 amount after converting
        after_client_st2_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})
        # todo: should check exact value
        received_st2_amount = int(after_client_st2_amount, 16) - int(before_client_st2_amount, 16)
        self.assertGreater(received_st2_amount, 0)

        # check client's smart token 1 amount after converting
        after_client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})
        self.assertEqual(self._CLIENT_ST1_TOKEN_AMOUNT - converting_st1_token_amount,
                         int(after_client_st1_amount, 16))

        # check st1 converter's smart token 2 amount
        converter_st2_amount = icx_call(icon_integrate_test_base=super(),
                                        from_=self.network_owner_wallet.get_address(),
                                        to_=self.smart_token_2_address,
                                        method="balanceOf",
                                        params={"_owner": str(self.st1_converter_address)})
        self.assertEqual(self._ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_st2_amount,
                         int(converter_st2_amount, 16))

        # check smart token 1's total supply
        st1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.smart_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_ST1_TOKEN_TOTAL_SUPPLY * 10 ** self._ST1_DECIMALS - converting_st1_token_amount,
                         int(st1_total_supply, 16))

    def test_convert_with_short_path_cross_token_to_icx(self):
        # test using ST1 converter
        # success case: convert st2 token to Icx coin
        before_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                   address=Address.from_string(self.network_owner_address))

        converting_st2_amount = 10
        cross_path = "{0},{1},{2}".format(self.smart_token_2_address,
                                          self.smart_token_1_address,
                                          self.icx_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_st2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        # check client's Icx coin amount
        after_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                  address=Address.from_string(self.network_owner_address))
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
                                              params={"_owner": self.st1_converter_address})
        self.assertEqual(self._ST1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT - received_icx_amount,
                         int(converter_icx_token_amount, 16))

        # check converter's st2 token amount
        converter_st2_amount = icx_call(icon_integrate_test_base=super(),
                                        from_=self.network_owner_wallet.get_address(),
                                        to_=self.smart_token_2_address,
                                        method="balanceOf",
                                        params={"_owner": self.st1_converter_address})

        self.assertEqual(self._ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_st2_amount,
                         int(converter_st2_amount, 16))

        # check smart token 1's total supply (should not be changed)
        st1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.smart_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_ST1_TOKEN_TOTAL_SUPPLY * 10 ** self._ST1_DECIMALS,
                         int(st1_total_supply, 16))

    def test_convert_with_short_path_cross_icx_to_token(self):
        # test using ST1 converter
        # success case: convert Icx coin to st2 token
        before_client_st2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": self.network_owner_address})

        converting_icx_amount = 10
        cross_path = "{0},{1},{2}".format(self.icx_token_address,
                                          self.smart_token_1_address,
                                          self.smart_token_2_address)
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
                                              params={"_owner": self.st1_converter_address})
        self.assertEqual(self._ST1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT + converting_icx_amount,
                         int(converter_icx_token_amount, 16))

        # check client's st2 token amount
        after_client_st2_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": self.network_owner_address})

        received_st2_amount = int(after_client_st2_amount, 16) - int(before_client_st2_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_st2_amount, 0)

        # check converter's st2 token amount
        converter_st2_amount = icx_call(icon_integrate_test_base=super(),
                                        from_=self.network_owner_wallet.get_address(),
                                        to_=self.smart_token_2_address,
                                        method="balanceOf",
                                        params={"_owner": self.st1_converter_address})
        self.assertEqual(self._ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_st2_amount,
                         int(converter_st2_amount, 16))

        # check smart token 1's total supply (should not be changed)
        st1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.smart_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_ST1_TOKEN_TOTAL_SUPPLY * 10 ** self._ST1_DECIMALS,
                         int(st1_total_supply, 16))

    def test_convert_with_long_path_sell_sell(self):
        # success case: convert st1 - st2 - icx
        before_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                   address=Address.from_string(self.network_owner_address))
        converting_st1_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.smart_token_1_address,
                                                 self.smart_token_1_address,
                                                 self.smart_token_2_address,
                                                 self.smart_token_2_address,
                                                 self.icx_token_address)
        min_return = 1
        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_st1_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_1_address,
                         method="transfer",
                         params=send_tx_params)

        # check st1_total supply
        st1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.smart_token_1_address,
                                    method="totalSupply",
                                    params={})

        self.assertEqual(self._INITIAL_ST2_TOKEN_TOTAL_SUPPLY * 10 ** self._ST1_DECIMALS - converting_st1_amount,
                         int(st1_total_supply, 16))

        # check client st1 token amount
        client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.smart_token_1_address,
                                     method="balanceOf",
                                     params={"_owner": self.network_owner_address})

        self.assertEqual(self._CLIENT_ST1_TOKEN_AMOUNT - converting_st1_amount,
                         int(client_st1_amount, 16))

        # check client icx coin amount
        after_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                  address=Address.from_string(self.network_owner_address))

        received_client_icx_amount = int(after_client_icx_amount, 16) - int(before_client_icx_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_client_icx_amount, 0)
        # check st2 converter's icx token amount
        st2_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.st2_converter_address})

        self.assertEqual(self._ST2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT - received_client_icx_amount,
                         int(st2_converter_icx_token_amount, 16))

    def test_convert_with_long_path_sell_buy(self):
        # success case: convert st1 - icx - st2
        converting_st1_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.smart_token_1_address,
                                                 self.smart_token_1_address,
                                                 self.icx_token_address,
                                                 self.smart_token_2_address,
                                                 self.smart_token_2_address)
        min_return = 1
        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_st1_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_1_address,
                         method="transfer",
                         params=send_tx_params)

        # check st1_total supply
        st1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.smart_token_1_address,
                                    method="totalSupply",
                                    params={})

        self.assertEqual(self._INITIAL_ST2_TOKEN_TOTAL_SUPPLY * 10 ** self._ST1_DECIMALS - converting_st1_amount,
                         int(st1_total_supply, 16))

        # check client st1 token amount
        client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.smart_token_1_address,
                                     method="balanceOf",
                                     params={"_owner": self.network_owner_address})

        self.assertEqual(self._CLIENT_ST1_TOKEN_AMOUNT - converting_st1_amount,
                         int(client_st1_amount, 16))

        # check client's st2 amount
        client_st2_amount = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.smart_token_2_address,
                                     method="balanceOf",
                                     params={"_owner": self.network_owner_address})

        received_st2_amount = int(client_st2_amount, 16) - self._CLIENT_ST2_TOKEN_AMOUNT
        # todo: should check exact value
        self.assertGreater(received_st2_amount, 0)

        # check st2 total supply
        st2_total_supply = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_2_address,
                                            method="totalSupply",
                                            params={})

        self.assertEqual(self._INITIAL_ST2_TOKEN_TOTAL_SUPPLY * 10 ** self._ST2_DECIMALS + received_st2_amount,
                         int(st2_total_supply, 16))

    def test_convert_with_long_path_sell_cross(self):
        # success case: convert st1 - icx - st1
        converting_st1_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.smart_token_1_address,
                                                 self.smart_token_1_address,
                                                 self.icx_token_address,
                                                 self.smart_token_2_address,
                                                 self.smart_token_1_address)
        min_return = 1
        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_st1_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_1_address,
                         method="transfer",
                         params=send_tx_params)

        # check st1_total supply
        st1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.smart_token_1_address,
                                    method="totalSupply",
                                    params={})

        self.assertEqual(self._INITIAL_ST2_TOKEN_TOTAL_SUPPLY * 10 ** self._ST1_DECIMALS - converting_st1_amount,
                         int(st1_total_supply, 16))

        # check client's st1 token amount 's difference between before with after converting
        # (should get less amount than before converting)
        client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.smart_token_1_address,
                                     method="balanceOf",
                                     params={"_owner": self.network_owner_address})

        client_st1_amount_except_converting = self._CLIENT_ST1_TOKEN_AMOUNT - converting_st1_amount
        received_client_st1_amount = int(client_st1_amount, 16) - client_st1_amount_except_converting
        # todo: should check exact value
        self.assertLess(received_client_st1_amount, converting_st1_amount)

        # check st2 converter's st1 token amount
        st2_converter_st1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": self.st2_converter_address})

        self.assertEqual(self._ST2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_client_st1_amount,
                         int(st2_converter_st1_amount, 16))

    def test_convert_with_long_path_buy_buy(self):
        # success case: convert icx - st2 - st1
        # st2 converter - st1 converter
        before_client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": self.network_owner_address})

        converting_icx_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.icx_token_address,
                                                 self.smart_token_2_address,
                                                 self.smart_token_2_address,
                                                 self.smart_token_1_address,
                                                 self.smart_token_1_address)
        min_return = 1
        send_tx_params = {"_path": long_path,
                          "_minReturn": min_return}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.network_score_address,
                         method="convert",
                         value=converting_icx_amount,
                         params=send_tx_params)

        # check st2 converter's icx token amount
        st2_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.st2_converter_address})

        self.assertEqual(self._ST2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT + converting_icx_amount,
                         int(st2_converter_icx_token_amount, 16))

        # check client's st1 token amount
        after_client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": self.network_owner_address})
        received_st1_amount = int(after_client_st1_amount, 16) - int(before_client_st1_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_st1_amount, 0)

        # check st1 converter's st2 token amount
        st1_converter_st2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": self.st1_converter_address})

        self.assertGreater(int(st1_converter_st2_amount, 16),
                           self._ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT)

    def test_convert_with_long_path_buy_cross(self):
        # success case: convert icx - st1 - icx
        before_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                   address=Address.from_string(self.network_owner_address))
        converting_icx_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.icx_token_address,
                                                 self.smart_token_1_address,
                                                 self.smart_token_1_address,
                                                 self.smart_token_2_address,
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
                                                  address=Address.from_string(self.network_owner_address))
        client_icx_amount_except_converting = int(before_client_icx_amount, 16) - converting_icx_amount
        received_icx_amount = int(after_client_icx_amount, 16) - client_icx_amount_except_converting
        # todo: should check exact value
        self.assertLess(received_icx_amount, converting_icx_amount)

        # check st1 converter's icx token amount
        st1_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.st1_converter_address})

        self.assertEqual(self._ST1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT + converting_icx_amount,
                         int(st1_converter_icx_token_amount, 16))

        # check st2 converter's icx token amount
        st2_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.st2_converter_address})

        self.assertEqual(self._ST2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT - received_icx_amount,
                         int(st2_converter_icx_token_amount, 16))

    def test_convert_with_long_path_cross_sell(self):
        # success case: convert icx – st2 - st1
        before_client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": self.network_owner_address})

        converting_icx_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.icx_token_address,
                                                 self.smart_token_1_address,
                                                 self.smart_token_2_address,
                                                 self.smart_token_2_address,
                                                 self.smart_token_1_address)
        min_return = 1
        send_tx_params = {"_path": long_path,
                          "_minReturn": min_return}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.network_score_address,
                         method="convert",
                         value=converting_icx_amount,
                         params=send_tx_params)

        # check st1 converter's icx token amount
        st1_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.st1_converter_address})
        self.assertEqual(self._ST1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT + converting_icx_amount,
                         int(st1_converter_icx_token_amount, 16))

        # check client's st1 token amount
        after_client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": self.network_owner_address})
        received_st1_amount = int(after_client_st1_amount, 16) - int(before_client_st1_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_st1_amount, 0)

        # check st2 converter's st1 token amount
        st2_converter_st1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": self.st2_converter_address})

        self.assertEqual(self._ST2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_st1_amount,
                         int(st2_converter_st1_amount, 16))

    def test_convert_with_long_path_cross_buy(self):
        # success case: convert st2 – icx - st2
        before_client_st2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": self.network_owner_address})
        converting_st2_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.smart_token_2_address,
                                                 self.smart_token_1_address,
                                                 self.icx_token_address,
                                                 self.smart_token_2_address,
                                                 self.smart_token_2_address)
        min_return = 1
        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_st2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        # check st1 converter's st2 amount
        st1_converter_st2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": self.st1_converter_address})
        self.assertEqual(self._ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_st2_amount,
                         int(st1_converter_st2_amount, 16))

        # check client's st2 amount's difference between before with after converting
        # (should get less amount than before converting)
        after_client_st2_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": self.network_owner_address})
        client_icx_amount_except_converting = int(before_client_st2_amount, 16) - converting_st2_amount
        received_st2_amount = int(after_client_st2_amount, 16) - client_icx_amount_except_converting
        # todo: should check exact value
        self.assertLess(received_st2_amount, converting_st2_amount)

        # check st2 converter's icx token amount
        st2_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.st2_converter_address})
        # todo: should check exact value
        self.assertGreater(int(st2_converter_icx_token_amount, 16),
                           self._ST2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT)

        # check smart token 2's total supply
        st2_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.smart_token_2_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_ST1_TOKEN_TOTAL_SUPPLY * 10 ** self._ST1_DECIMALS + received_st2_amount,
                         int(st2_total_supply, 16))

    def test_convert_with_long_path_cross_cross(self):
        # success case: convert st2 - icx - st1
        before_client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        converting_st2_amount = 10
        long_path = "{0},{1},{2},{3},{4}".format(self.smart_token_2_address,
                                                 self.smart_token_1_address,
                                                 self.icx_token_address,
                                                 self.smart_token_2_address,
                                                 self.smart_token_1_address)
        min_return = 1
        converting_params = {"path": long_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": self.network_score_address,
                          "_value": converting_st2_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=self.smart_token_2_address,
                         method="transfer",
                         params=send_tx_params)

        # check st1 converter's smart token 2 amount
        converter_st1_amount = icx_call(icon_integrate_test_base=super(),
                                        from_=self.network_owner_wallet.get_address(),
                                        to_=self.smart_token_2_address,
                                        method="balanceOf",
                                        params={"_owner": str(self.st1_converter_address)})
        self.assertEqual(self._ST1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_st2_amount,
                         int(converter_st1_amount, 16))

        after_client_st1_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.smart_token_1_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})

        # check client's smart token 1 amount
        received_st1_amount = int(after_client_st1_amount, 16) - int(before_client_st1_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_st1_amount, 0)

        # check st2 converter's smart token 1 amount
        st2_converter_st1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.smart_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.st2_converter_address)})

        self.assertEqual(self._ST2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_st1_amount,
                         int(st2_converter_st1_amount, 16))

        # check smart token 1 total supply (should not be changed)
        st1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.smart_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_ST1_TOKEN_TOTAL_SUPPLY * 10 ** self._ST1_DECIMALS,
                         int(st1_total_supply, 16))

        # check smart token 2 total supply (should not be changed)
        st2_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.smart_token_2_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(self._INITIAL_ST2_TOKEN_TOTAL_SUPPLY * 10 ** self._ST2_DECIMALS,
                         int(st2_total_supply, 16))

    def test_tokenFallback(self):

        pass
