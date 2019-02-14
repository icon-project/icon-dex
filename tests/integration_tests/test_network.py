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

from contracts.interfaces.abc_score_registry import ABCScoreRegistry
from tests.integration_tests.utils import *


class TestNetwork(IconIntegrateTestBase):
    _INITIAL_ICX_SEND_AMOUNT = 5000
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

        self.additional_wallets = [KeyWallet.create() for i in range(5)]
        additional_accounts = [
            Account(wallet.address, Address.from_string(wallet.address),
                    1_000_000 * self._icx_factor)
            for wallet in self.additional_wallets]

        genesis_account_list = [
                                   Account("network_owner",
                                           Address.from_string(self.network_owner_address),
                                           1_000_000 * self._icx_factor)
                               ] + additional_accounts
        super().setUp(genesis_account_list)

        update_governance(icon_integrate_test_base=super(), from_=self._test1, params={})

        # if you want to send request to network, uncomment next line
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # # setting Icx token SCORE
        self.icx_token_address = self.setup_icx_token(
            self.network_owner_wallet, self._INITIAL_ICX_SEND_AMOUNT * self._ICX_DECIMALS)

        # # setting network SCORE
        self.network_score_address = self.setup_network(
            self.network_owner_wallet, self.icx_token_address)

        # # setting registry SCORE
        self.score_registry_address = self.setup_registry(
            self.network_owner_wallet, self.network_score_address)

        # # setting flexible token SCOREs

        # deploy FT1, FT2 token
        self.flexible_token_1_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_1',
            'FT1',
            self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY,
            self._FT1_DECIMALS
        )

        self.flexible_token_2_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_2',
            'FT2',
            self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY,
            self._FT2_DECIMALS
        )

        # # setting FT1 converter SCORE
        self.ft1_converter_address = self.init_converter(
            self.network_owner_wallet,
            self.flexible_token_1_address,
            self.score_registry_address,
            self.icx_token_address,
            self.flexible_token_2_address,
            self._FT1_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT,
            self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT,
            True
        )

        # # setting FT2 converter SCORE
        self.ft2_converter_address = self.init_converter(
            self.network_owner_wallet,
            self.flexible_token_2_address,
            self.score_registry_address,
            self.icx_token_address,
            self.flexible_token_1_address,
            self._FT2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT,
            self._FT2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT,
            True
        )

    def setup_network(self, deploy_key, icx_token_address):
        # deploy network
        tx_result = deploy_score(self, get_content_as_bytes("network"), deploy_key, params={})
        score_address = tx_result['scoreAddress']

        # register icx token
        send_tx_params = {"_icxToken": icx_token_address, "_register": int(True)}
        transaction_call(icon_integrate_test_base=super(),
                         from_=deploy_key,
                         to_=score_address,
                         method="registerIcxToken",
                         params=send_tx_params)

        actual_icx_token_registered = icx_call(icon_integrate_test_base=super(),
                                               from_=deploy_key.get_address(),
                                               to_=score_address,
                                               method="getIcxTokenRegistered",
                                               params={"_icxToken": str(icx_token_address)})
        self.assertEqual(hex(True), actual_icx_token_registered)

        return score_address

    def setup_registry(self, deploy_key, network_address):
        tx_result = deploy_score(self, get_content_as_bytes("score_registry"), deploy_key,
                                 params={})
        score_address = tx_result['scoreAddress']

        transaction_call(self, deploy_key, score_address, 'registerAddress',
                         {
                             '_scoreName': ABCScoreRegistry.NETWORK,
                             '_scoreAddress': network_address
                         })

        # check if the network score registered correctly
        actual_registered_network_address = icx_call(icon_integrate_test_base=super(),
                                                     from_=deploy_key.get_address(),
                                                     to_=score_address,
                                                     method="getAddress",
                                                     params={"_scoreName": "Network"})
        self.assertEqual(str(self.network_score_address), actual_registered_network_address)

        return score_address

    def setup_irc_token(
            self, deploy_key, name: str, symbol: str, initial_supply: int, decimals: int):
        tx_result = deploy_score(self, get_content_as_bytes("irc_token"), deploy_key,
                                 params={
                                     '_name': name,
                                     '_symbol': symbol,
                                     '_initialSupply': initial_supply,
                                     '_decimals': decimals
                                 })

        return tx_result['scoreAddress']

    def setup_icx_token(self, deploy_key, initial_icx_amount):
        # deploy Icx token
        tx_result = deploy_score(icon_integrate_test_base=super(),
                                 content_as_bytes=get_content_as_bytes("icx_token"),
                                 from_=deploy_key,
                                 params={})
        score_address = tx_result['scoreAddress']

        # send Icx to Icx token (issue icx token)
        icx_transfer_call(icon_integrate_test_base=super(),
                          from_=deploy_key,
                          to_=score_address,
                          value=initial_icx_amount)

        actual_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=deploy_key.get_address(),
                                           to_=score_address,
                                           method="balanceOf",
                                           params={"_owner": deploy_key.get_address()})
        self.assertEqual(hex(initial_icx_amount), actual_icx_token_amount)

        return score_address

    def setup_flexible_token(self, deploy_key, name, symbol, initial_supply, decimals):
        tx_result = deploy_score(self, get_content_as_bytes("flexible_token"), deploy_key,
                                 params={
                                     '_name': name,
                                     '_symbol': symbol,
                                     '_initialSupply': initial_supply,
                                     '_decimals': decimals
                                 })

        return tx_result['scoreAddress']

    def setup_converter(self,
                        deploy_key,
                        flexible_token,
                        registry,
                        max_conversion_fee,
                        connector_token,
                        connector_wight):
        tx_result = deploy_score(self, get_content_as_bytes("converter"), deploy_key,
                                 params={
                                     '_token': str(flexible_token),
                                     '_registry': str(registry),
                                     '_maxConversionFee': max_conversion_fee,
                                     '_connectorToken': str(connector_token),
                                     '_connectorWeight': connector_wight
                                 })

        return tx_result['scoreAddress']

    def init_converter(self,
                       deploy_key,
                       flexible_token_address,
                       score_registry_address,
                       initial_connector_address,
                       additional_connector_address,
                       initial_connector_balance,
                       additional_connector_balance,
                       activate):
        # deploy converter
        converter_address = self.setup_converter(
            deploy_key,
            flexible_token_address,
            score_registry_address,
            1000000,
            initial_connector_address,
            500000
        )

        # send initial connector token to converter
        send_tx_params = {"_to": converter_address,
                          "_value": initial_connector_balance}
        transaction_call(icon_integrate_test_base=super(),
                         from_=deploy_key,
                         to_=initial_connector_address,
                         method="transfer",
                         params=send_tx_params)

        connector_balance = icx_call(icon_integrate_test_base=super(),
                                     from_=deploy_key.get_address(),
                                     to_=initial_connector_address,
                                     method="balanceOf",
                                     params={"_owner": converter_address})
        self.assertEqual(hex(initial_connector_balance), connector_balance)

        if additional_connector_address:
            # add additional connector
            send_tx_params = {"_token": additional_connector_address,
                              "_weight": 500000,
                              "_enableVirtualBalance": int(False)}
            transaction_call(icon_integrate_test_base=super(),
                             from_=deploy_key,
                             to_=converter_address,
                             method="addConnector",
                             params=send_tx_params)

            # send additional connector token to converter
            send_tx_params = {"_to": converter_address,
                              "_value": additional_connector_balance}
            transaction_call(icon_integrate_test_base=super(),
                             from_=deploy_key,
                             to_=additional_connector_address,
                             method="transfer",
                             params=send_tx_params)

            connector_balance = icx_call(icon_integrate_test_base=super(),
                                         from_=deploy_key.get_address(),
                                         to_=additional_connector_address,
                                         method="balanceOf",
                                         params={"_owner": converter_address})
            self.assertEqual(hex(additional_connector_balance), connector_balance)

        if activate:
            # transfer ownership of flexible token 1 to ft1 converter
            send_tx_params = {"_newOwner": converter_address}
            transaction_call(icon_integrate_test_base=super(),
                             from_=deploy_key,
                             to_=flexible_token_address,
                             method="transferOwnerShip",
                             params=send_tx_params)

            # accept ownership of flexible token 1
            transaction_call(icon_integrate_test_base=super(),
                             from_=deploy_key,
                             to_=converter_address,
                             method="acceptTokenOwnership",
                             params={})

            # check if the converter activated
            actual_activation = icx_call(icon_integrate_test_base=super(),
                                         from_=deploy_key.get_address(),
                                         to_=converter_address,
                                         method="isActive",
                                         params={})
            self.assertEqual(hex(True), actual_activation)

        return converter_address

    def test_getExpectedReturn_short_path(self):
        # success case: check if the expected return amount is equal to actual converting result (short path)
        converting_ft2_amount = 1 * self._ICX_DECIMALS
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

        actual_issued_ft1_amount = int(after_client_ft1_amount, 16) - int(before_client_ft1_amount,
                                                                          16)
        self.assertEqual(int(expected_return_amount, 16), actual_issued_ft1_amount)

    def test_getExpectedReturn_long_path(self):
        # success case: check if the expected return amount is equal to actual converting result (long path)
        converting_ft2_amount = 1 * self._ICX_DECIMALS
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

        actual_received_ft1_amount = int(after_client_ft1_amount, 16) - int(
            before_client_ft1_amount, 16)
        self.assertEqual(int(expected_return_amount, 16), actual_received_ft1_amount)

    def test_getExpectedReturn_input_invalid_convert_path(self):
        # failure case: input path which invalid length
        converting_ft2_amount = 1 * self._ICX_DECIMALS
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

        converting_icx_amount = 1 * self._ICX_DECIMALS
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
        converting_ft2_amount = 1 * self._ICX_DECIMALS
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
        converting_icx_amount = 1 * self._ICX_DECIMALS
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
        converting_ft2_amount = 1 * self._ICX_DECIMALS
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
        converting_icx_amount = 1 * self._ICX_DECIMALS
        invalid_ = "{0},{1},{2}".format(self.icx_token_address,
                                        self.flexible_token_1_address,
                                        self.flexible_token_2_address)
        min_return = 10 * self._ICX_DECIMALS
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

        converting_icx_amount = 1 * self._ICX_DECIMALS
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

        received_ft2_amount = int(after_receiver_ft2_amount, 16) - int(before_receiver_ft2_amount,
                                                                       16)
        # todo: should check exact value
        self.assertGreater(received_ft2_amount, 0)

        # success case: token convert 'for'
        before_receiver_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                     address=str(receiver_address))

        converting_ft2_amount = 1 * self._ICX_DECIMALS
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

        received_icx_amount = int(after_receiver_icx_amount, 16) - int(before_receiver_icx_amount,
                                                                       16)
        self.assertGreater(received_icx_amount, 0)

    def test_convert_with_short_path_buy(self):
        # test using FT1 converter
        # success case: buy ft1(flexible token) token with ft2(connector token)
        before_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        converting_ft2_amount = 1 * self._ICX_DECIMALS
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
        self.assertEqual(
            self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_ft2_amount,
            int(converter_ft1_amount, 16))

        # check flexible token 1's total supply
        ft1_total_supply = icx_call(icon_integrate_test_base=super(),
                                    from_=self.network_owner_wallet.get_address(),
                                    to_=self.flexible_token_1_address,
                                    method="totalSupply",
                                    params={})
        self.assertEqual(
            self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS + issued_ft1_amount,
            int(ft1_total_supply, 16))

    def test_convert_with_short_path_sell(self):
        # test using FT1 converter
        # success case: sell ft1 (flexible token) token to buy ft2(connector token)
        before_client_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_2_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        converting_ft1_token_amount = 1 * self._ICX_DECIMALS
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
        self.assertEqual(
            self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS - converting_ft1_token_amount,
            int(ft1_total_supply, 16))

    def test_convert_with_short_path_cross_token_to_icx(self):
        # test using FT1 converter
        # success case: convert ft2 token to Icx coin
        before_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                   address=self.network_owner_address)

        before_client_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_address,
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.network_owner_address})

        converting_ft2_amount = 1 * self._ICX_DECIMALS
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

        self.assertEqual(before_client_icx_token_amount, client_icx_token_amount)

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

        self.assertEqual(
            self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_ft2_amount,
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

        converting_icx_amount = 1 * self._ICX_DECIMALS
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
        converting_ft1_amount = 1 * self._ICX_DECIMALS
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

        self.assertEqual(
            self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS - converting_ft1_amount,
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

        received_client_icx_amount = int(after_client_icx_amount, 16) - int(
            before_client_icx_amount, 16)
        # todo: should check exact value
        self.assertGreater(received_client_icx_amount, 0)
        # check ft2 converter's icx token amount
        ft2_converter_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                                  from_=self.network_owner_wallet.get_address(),
                                                  to_=self.icx_token_address,
                                                  method="balanceOf",
                                                  params={"_owner": self.ft2_converter_address})

        self.assertEqual(
            self._FT2_CONVERTER_DEPOSITED_ICX_TOKEN_AMOUNT - received_client_icx_amount,
            int(ft2_converter_icx_token_amount, 16))

    def test_convert_with_long_path_sell_buy(self):
        # success case: convert ft1 - icx - ft2
        converting_ft1_amount = 1 * self._ICX_DECIMALS
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

        self.assertEqual(
            self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS - converting_ft1_amount,
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

        self.assertEqual(
            self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY * 10 ** self._FT2_DECIMALS + received_ft2_amount,
            int(ft2_total_supply, 16))

    def test_convert_with_long_path_sell_cross(self):
        # success case: convert ft1 - icx - ft1
        converting_ft1_amount = 1 * self._ICX_DECIMALS
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

        self.assertEqual(
            self._INITIAL_FT2_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS - converting_ft1_amount,
            int(ft1_total_supply, 16))

        # check client's ft1 token amount 's difference between before with after converting
        # (should get less amount than before converting)
        client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=self.flexible_token_1_address,
                                     method="balanceOf",
                                     params={"_owner": self.network_owner_address})

        client_ft1_amount_except_converting = self._CLIENT_FT1_TOKEN_AMOUNT - converting_ft1_amount
        received_client_ft1_amount = int(client_ft1_amount,
                                         16) - client_ft1_amount_except_converting
        # todo: should check exact value
        self.assertLess(received_client_ft1_amount, converting_ft1_amount)

        # check ft2 converter's ft1 token amount
        ft2_converter_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": self.ft2_converter_address})

        self.assertEqual(
            self._FT2_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT - received_client_ft1_amount,
            int(ft2_converter_ft1_amount, 16))

    def test_convert_with_long_path_buy_buy(self):
        # success case: convert icx - ft2 - ft1
        # ft2 converter - ft1 converter
        before_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": self.network_owner_address})

        converting_icx_amount = 1 * self._ICX_DECIMALS
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
        converting_icx_amount = 1 * self._ICX_DECIMALS
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
        client_icx_amount_except_converting = int(before_client_icx_amount,
                                                  16) - converting_icx_amount
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

        converting_icx_amount = 1 * self._ICX_DECIMALS
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
        converting_ft2_amount = 1 * self._ICX_DECIMALS
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
        self.assertEqual(
            self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_ft2_amount,
            int(ft1_converter_ft2_amount, 16))

        # check client's ft2 amount's difference between before with after converting
        # (should get less amount than before converting)
        after_client_ft2_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.flexible_token_2_address,
                                           method="balanceOf",
                                           params={"_owner": self.network_owner_address})
        client_icx_amount_except_converting = int(before_client_ft2_amount,
                                                  16) - converting_ft2_amount
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
        self.assertEqual(
            self._INITIAL_FT1_TOKEN_TOTAL_SUPPLY * 10 ** self._FT1_DECIMALS + received_ft2_amount,
            int(ft2_total_supply, 16))

    def test_convert_with_long_path_cross_cross(self):
        # success case: convert ft2 - icx - ft1
        before_client_ft1_amount = icx_call(icon_integrate_test_base=super(),
                                            from_=self.network_owner_wallet.get_address(),
                                            to_=self.flexible_token_1_address,
                                            method="balanceOf",
                                            params={"_owner": str(self.network_owner_address)})

        converting_ft2_amount = 1 * self._ICX_DECIMALS
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
        self.assertEqual(
            self._FT1_CONVERTER_DEPOSITED_CONNECTOR_TOKEN_AMOUNT + converting_ft2_amount,
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
        token_amount = 1 * self._ICX_DECIMALS

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
        converting_ft2_amount = 1 * self._ICX_DECIMALS
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

    def test_convert_with_inactive_flexible_token(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            1000 * self._ICX_DECIMALS,
            False
        )

        # check if the converter inactive
        actual_activation = icx_call(icon_integrate_test_base=super(),
                                     from_=self.network_owner_wallet.get_address(),
                                     to_=converter_address,
                                     method="isActive",
                                     params={})
        self.assertEqual(hex(False), actual_activation)

        converting_ft2_amount = 1 * self._ICX_DECIMALS
        cross_path = "{0},{1},{2}".format(irc_token_address,
                                          flexible_token_address,
                                          self.icx_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": converting_ft2_amount,
                          "_data": encoded_converting_params}
        with self.assertRaises(AssertionError):
            transaction_call(icon_integrate_test_base=super(),
                             from_=self.network_owner_wallet,
                             to_=irc_token_address,
                             method="transfer",
                             params=send_tx_params)

    def test_convert_with_fee(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            1000 * self._ICX_DECIMALS,
            True
        )
        convert_amount = 1 * self._ICX_DECIMALS

        return_without_fee = icx_call(self, self.network_owner_address, converter_address,
                                      'getReturn', {
                                          '_fromToken': irc_token_address,
                                          '_toToken': self.icx_token_address,
                                          '_amount': convert_amount
                                      })

        self.assertEqual(0, return_without_fee['fee'])

        # sets conversion fee as 1%
        transaction_call(self, self.network_owner_wallet, converter_address,
                         'setConversionFee', {'_conversionFee': 10000})

        return_with_fee = icx_call(self, self.network_owner_address, converter_address,
                                   'getReturn', {
                                       '_fromToken': irc_token_address,
                                       '_toToken': self.icx_token_address,
                                       '_amount': convert_amount
                                   })

        self.assertGreater(return_with_fee['fee'], 0)
        self.assertLess(return_with_fee['amount'], return_without_fee['amount'])

        before_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                   address=self.network_owner_address)

        cross_path = "{0},{1},{2}".format(irc_token_address,
                                          flexible_token_address,
                                          self.icx_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=irc_token_address,
                         method="transfer",
                         params=send_tx_params)

        after_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                  address=self.network_owner_address)

        received_icx_amount = int(after_client_icx_amount, 16) - int(before_client_icx_amount, 16)
        self.assertEqual(return_with_fee['amount'], received_icx_amount)

    def test_convert_buy_with_fee(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            1000 * self._ICX_DECIMALS,
            True
        )
        convert_amount = 1 * self._ICX_DECIMALS

        return_without_fee = icx_call(self, self.network_owner_address, converter_address,
                                      'getReturn', {
                                          '_fromToken': irc_token_address,
                                          '_toToken': flexible_token_address,
                                          '_amount': convert_amount
                                      })

        self.assertEqual(0, return_without_fee['fee'])

        # sets conversion fee as 1%
        transaction_call(self, self.network_owner_wallet, converter_address,
                         'setConversionFee', {'_conversionFee': 10000})

        return_with_fee = icx_call(self, self.network_owner_address, converter_address,
                                   'getReturn', {
                                       '_fromToken': irc_token_address,
                                       '_toToken': flexible_token_address,
                                       '_amount': convert_amount
                                   })

        self.assertGreater(return_with_fee['fee'], 0)
        self.assertLess(return_with_fee['amount'], return_without_fee['amount'])

        before_amount = icx_call(icon_integrate_test_base=super(),
                                 from_=self.network_owner_address,
                                 to_=flexible_token_address,
                                 method="balanceOf",
                                 params={"_owner": self.network_owner_address})

        cross_path = "{0},{1},{2}".format(irc_token_address,
                                          flexible_token_address,
                                          flexible_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        # success case if purchases disabled of from token`s connector
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=irc_token_address,
                         method="transfer",
                         params=send_tx_params)

        after_amount = icx_call(icon_integrate_test_base=super(),
                                from_=self.network_owner_address,
                                to_=flexible_token_address,
                                method="balanceOf",
                                params={"_owner": self.network_owner_address})

        received_amount = int(after_amount, 16) - int(before_amount, 16)
        self.assertEqual(return_with_fee['amount'], received_amount)

    def test_convert_sell_with_fee(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            1000 * self._ICX_DECIMALS,
            True
        )
        convert_amount = 1 * self._ICX_DECIMALS

        return_without_fee = icx_call(self, self.network_owner_address, converter_address,
                                      'getReturn', {
                                          '_fromToken': flexible_token_address,
                                          '_toToken': irc_token_address,
                                          '_amount': convert_amount
                                      })

        self.assertEqual(0, return_without_fee['fee'])

        # sets conversion fee as 1%
        transaction_call(self, self.network_owner_wallet, converter_address,
                         'setConversionFee', {'_conversionFee': 10000})

        return_with_fee = icx_call(self, self.network_owner_address, converter_address,
                                   'getReturn', {
                                       '_fromToken': flexible_token_address,
                                       '_toToken': irc_token_address,
                                       '_amount': convert_amount
                                   })

        self.assertGreater(return_with_fee['fee'], 0)
        self.assertLess(return_with_fee['amount'], return_without_fee['amount'])

        before_amount = icx_call(icon_integrate_test_base=super(),
                                 from_=self.network_owner_address,
                                 to_=irc_token_address,
                                 method="balanceOf",
                                 params={"_owner": self.network_owner_address})

        cross_path = "{0},{1},{2}".format(flexible_token_address,
                                          flexible_token_address,
                                          irc_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        # success case if purchases disabled of from token`s connector
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=flexible_token_address,
                         method="transfer",
                         params=send_tx_params)

        after_amount = icx_call(icon_integrate_test_base=super(),
                                from_=self.network_owner_address,
                                to_=irc_token_address,
                                method="balanceOf",
                                params={"_owner": self.network_owner_address})

        received_amount = int(after_amount, 16) - int(before_amount, 16)
        self.assertEqual(return_with_fee['amount'], received_amount)

    def test_convert_with_conversion_disabled(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            1000 * self._ICX_DECIMALS,
            True
        )

        transaction_call(self, self.network_owner_wallet, converter_address,
                         'disableConversions',
                         {'_disable': 1})

        conversion_enabled = icx_call(self, self.network_owner_address, converter_address,
                                      'isConversionsEnabled', {})

        self.assertEqual(False, int(conversion_enabled, 16))

        convert_amount = 1 * self._ICX_DECIMALS
        cross_path = "{0},{1},{2}".format(self.icx_token_address,
                                          flexible_token_address,
                                          irc_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        with self.assertRaises(AssertionError):
            transaction_call(icon_integrate_test_base=super(),
                             from_=self.network_owner_wallet,
                             to_=self.icx_token_address,
                             method="transfer",
                             params=send_tx_params)

    def test_convert_with_virtual_balance_enabled_buy(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            1000 * self._ICX_DECIMALS,
            True
        )

        transaction_call(self, self.network_owner_wallet, converter_address,
                         'updateConnector',
                         {
                             '_connectorToken': irc_token_address,
                             '_weight': 500000,
                             '_enableVirtualBalance': 1,
                             '_virtualBalance': 1000 * self._ICX_DECIMALS,
                         })

        connector = icx_call(self, self.network_owner_wallet.get_address(), converter_address,
                             'getConnector', {'_address': irc_token_address})
        self.assertEqual(1000 * self._ICX_DECIMALS, connector['virtualBalance'])
        self.assertEqual(True, connector['isVirtualBalanceEnabled'])

        convert_amount = 1 * self._ICX_DECIMALS
        cross_path = "{0},{1},{2}".format(irc_token_address,
                                          flexible_token_address,
                                          flexible_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        # success case if purchases disabled of from token`s connector
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=irc_token_address,
                         method="transfer",
                         params=send_tx_params)

        connector_balance = icx_call(self, self.network_owner_address, converter_address,
                                     'getConnectorBalance', {'_connectorToken': irc_token_address})

        connector = icx_call(self, self.network_owner_address, converter_address,
                             'getConnector', {'_address': irc_token_address})

        real_balance = icx_call(self, self.network_owner_address, irc_token_address,
                                'balanceOf', {'_owner': converter_address})

        self.assertEqual(int(connector_balance, 16), connector['virtualBalance'])
        self.assertEqual(int(real_balance, 16), connector['virtualBalance'])

    def test_convert_with_virtual_balance_enabled_sell(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            1000 * self._ICX_DECIMALS,
            True
        )

        transaction_call(self, self.network_owner_wallet, converter_address,
                         'updateConnector',
                         {
                             '_connectorToken': irc_token_address,
                             '_weight': 500000,
                             '_enableVirtualBalance': 1,
                             '_virtualBalance': 1000 * self._ICX_DECIMALS,
                         })

        connector = icx_call(self, self.network_owner_wallet.get_address(), converter_address,
                             'getConnector', {'_address': irc_token_address})
        self.assertEqual(1000 * self._ICX_DECIMALS, connector['virtualBalance'])
        self.assertEqual(True, connector['isVirtualBalanceEnabled'])

        convert_amount = 1 * self._ICX_DECIMALS
        cross_path = "{0},{1},{2}".format(flexible_token_address,
                                          flexible_token_address,
                                          irc_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        # success case if purchases disabled of from token`s connector
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=flexible_token_address,
                         method="transfer",
                         params=send_tx_params)

        connector_balance = icx_call(self, self.network_owner_address, converter_address,
                                     'getConnectorBalance', {'_connectorToken': irc_token_address})

        connector = icx_call(self, self.network_owner_address, converter_address,
                             'getConnector', {'_address': irc_token_address})

        real_balance = icx_call(self, self.network_owner_address, irc_token_address,
                                'balanceOf', {'_owner': converter_address})

        self.assertEqual(int(connector_balance, 16), connector['virtualBalance'])
        self.assertEqual(int(real_balance, 16), connector['virtualBalance'])

    def test_convert_with_virtual_balance_enabled_cross_connector(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            1000 * self._ICX_DECIMALS,
            True
        )

        transaction_call(self, self.network_owner_wallet, converter_address,
                         'updateConnector',
                         {
                             '_connectorToken': irc_token_address,
                             '_weight': 500000,
                             '_enableVirtualBalance': 1,
                             '_virtualBalance': 1000 * self._ICX_DECIMALS,
                         })

        transaction_call(self, self.network_owner_wallet, converter_address,
                         'updateConnector',
                         {
                             '_connectorToken': self.icx_token_address,
                             '_weight': 500000,
                             '_enableVirtualBalance': 1,
                             '_virtualBalance': 1000 * self._ICX_DECIMALS,
                         })

        connector = icx_call(self, self.network_owner_wallet.get_address(), converter_address,
                             'getConnector', {'_address': irc_token_address})
        self.assertEqual(1000 * self._ICX_DECIMALS, connector['virtualBalance'])
        self.assertEqual(True, connector['isVirtualBalanceEnabled'])

        connector = icx_call(self, self.network_owner_wallet.get_address(), converter_address,
                             'getConnector', {'_address': self.icx_token_address})
        self.assertEqual(1000 * self._ICX_DECIMALS, connector['virtualBalance'])
        self.assertEqual(True, connector['isVirtualBalanceEnabled'])

        convert_amount = 1 * self._ICX_DECIMALS
        cross_path = "{0},{1},{2}".format(irc_token_address,
                                          flexible_token_address,
                                          self.icx_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        # success case if purchases disabled of from token`s connector
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=irc_token_address,
                         method="transfer",
                         params=send_tx_params)

        connector_balance = icx_call(self, self.network_owner_address, converter_address,
                                     'getConnectorBalance', {'_connectorToken': irc_token_address})

        connector = icx_call(self, self.network_owner_address, converter_address,
                             'getConnector', {'_address': irc_token_address})

        real_balance = icx_call(self, self.network_owner_address, irc_token_address,
                                'balanceOf', {'_owner': converter_address})

        self.assertEqual(int(connector_balance, 16), connector['virtualBalance'])
        self.assertEqual(int(real_balance, 16), connector['virtualBalance'])

        connector_balance = icx_call(self, self.network_owner_address, converter_address,
                                     'getConnectorBalance',
                                     {'_connectorToken': self.icx_token_address})

        connector = icx_call(self, self.network_owner_address, converter_address,
                             'getConnector', {'_address': self.icx_token_address})

        real_balance = icx_call(self, self.network_owner_address, self.icx_token_address,
                                'balanceOf', {'_owner': converter_address})

        self.assertEqual(int(connector_balance, 16), connector['virtualBalance'])
        self.assertEqual(int(real_balance, 16), connector['virtualBalance'])

    def test_convert_with_virtual_balance_enabled_sell_insufficient_real_balance(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            10 * self._ICX_DECIMALS,
            True
        )

        transaction_call(self, self.network_owner_wallet, converter_address,
                         'updateConnector',
                         {
                             '_connectorToken': irc_token_address,
                             '_weight': 500000,
                             '_enableVirtualBalance': 1,
                             '_virtualBalance': 1000 * self._ICX_DECIMALS,
                         })

        connector = icx_call(self, self.network_owner_wallet.get_address(), converter_address,
                             'getConnector', {'_address': irc_token_address})
        self.assertEqual(1000 * self._ICX_DECIMALS, connector['virtualBalance'])
        self.assertEqual(True, connector['isVirtualBalanceEnabled'])

        convert_amount = 15 * self._ICX_DECIMALS
        cross_path = "{0},{1},{2}".format(flexible_token_address,
                                          flexible_token_address,
                                          irc_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        # Raise exception because the real balance is less than returning amount.
        with self.assertRaises(AssertionError):
            transaction_call(icon_integrate_test_base=super(),
                             from_=self.network_owner_wallet,
                             to_=flexible_token_address,
                             method="transfer",
                             params=send_tx_params)

    def test_convert_with_purchase_disabled_of_from_token(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            1000 * self._ICX_DECIMALS,
            True
        )

        transaction_call(self, self.network_owner_wallet, converter_address,
                         'disableConnectorPurchases',
                         {'_connectorToken': irc_token_address, '_disable': 1})

        connector = icx_call(self, self.network_owner_wallet.get_address(), converter_address,
                             'getConnector', {'_address': irc_token_address})

        self.assertEqual(False, connector['isPurchaseEnabled'])

        before_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                   address=self.network_owner_address)

        convert_amount = 1 * self._ICX_DECIMALS
        cross_path = "{0},{1},{2}".format(irc_token_address,
                                          flexible_token_address,
                                          self.icx_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        # success case if purchases disabled of from token`s connector
        transaction_call(icon_integrate_test_base=super(),
                         from_=self.network_owner_wallet,
                         to_=irc_token_address,
                         method="transfer",
                         params=send_tx_params)

        after_client_icx_amount = get_icx_balance(icon_integrate_test_base=super(),
                                                  address=self.network_owner_address)

        received_icx_amount = int(after_client_icx_amount, 16) - int(before_client_icx_amount, 16)
        self.assertGreater(received_icx_amount, 0)

    def test_convert_with_purchase_disabled_of_to_token(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        converter_address = self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            irc_token_address,
            1000 * self._ICX_DECIMALS,
            1000 * self._ICX_DECIMALS,
            True
        )

        transaction_call(self, self.network_owner_wallet, converter_address,
                         'disableConnectorPurchases',
                         {'_connectorToken': irc_token_address, '_disable': 1})

        connector = icx_call(self, self.network_owner_wallet.get_address(), converter_address,
                             'getConnector', {'_address': irc_token_address})

        self.assertEqual(False, connector['isPurchaseEnabled'])

        convert_amount = 1 * self._ICX_DECIMALS
        cross_path = "{0},{1},{2}".format(self.icx_token_address,
                                          flexible_token_address,
                                          irc_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        # Raise exception if purchases disabled of to token`s connector
        with self.assertRaises(AssertionError):
            transaction_call(icon_integrate_test_base=super(),
                             from_=self.network_owner_wallet,
                             to_=self.icx_token_address,
                             method="transfer",
                             params=send_tx_params)

    def test_convert_with_invalid_connector(self):
        flexible_token_address = self.setup_flexible_token(
            self.network_owner_wallet,
            'flexible_token_3',
            'FT3',
            2000,
            18
        )

        irc_token_address = self.setup_irc_token(
            self.network_owner_wallet, 'IRC Token 1', 'IRC1', 10000, 18)

        self.init_converter(
            self.network_owner_wallet,
            flexible_token_address,
            self.score_registry_address,
            self.icx_token_address,
            None,
            1000 * self._ICX_DECIMALS,
            None,
            True
        )

        convert_amount = 1 * self._ICX_DECIMALS
        cross_path = "{0},{1},{2}".format(self.icx_token_address,
                                          flexible_token_address,
                                          irc_token_address)
        min_return = 1
        converting_params = {"path": cross_path,
                             "minReturn": min_return}
        stringed_converting_params = json_dumps(converting_params)
        encoded_converting_params = stringed_converting_params.encode(encoding="utf-8")
        send_tx_params = {"_to": str(self.network_score_address),
                          "_value": convert_amount,
                          "_data": encoded_converting_params}

        # Raise an exception because connector token is invalid
        with self.assertRaises(AssertionError):
            transaction_call(icon_integrate_test_base=super(),
                             from_=self.network_owner_wallet,
                             to_=self.icx_token_address,
                             method="transfer",
                             params=send_tx_params)
