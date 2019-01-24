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
    _TOKEN_INITIAL_TOTAL_SUPPLY_WITH_DECIMALS = 10000 * 10 ** 18
    _INITIAL_ICX_SEND_AMOUNT = 100
    _ICX_DECIMALS = 10 ** 18

    _INITIAL_ST1_TOKEN_TOTAL_SUPPLY = 100
    _ST1_DECIMALS = 18

    _INITIAL_ST2_TOKEN_TOTAL_SUPPLY = 100
    _ST2_DECIMALS = 18

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

        # deploy registry score
        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("score_registry"),
                                        from_=self.network_owner_wallet,
                                        params={})
        self.assertEqual(deploy_tx_result["status"], int(True))
        self.score_registry_address = deploy_tx_result["scoreAddress"]

        # deploy Icx token
        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("icx_token"),
                                        from_=self.network_owner_wallet,
                                        params={})
        self.assertEqual(int(True), deploy_tx_result["status"])
        self.icx_token_address = deploy_tx_result["scoreAddress"]

        # send Icx to Icx token
        tx_result = icx_transfer_call(icon_integrate_test_base=super(),
                                      from_=self.network_owner_wallet,
                                      to_=self.icx_token_address,
                                      value=self._INITIAL_ICX_SEND_AMOUNT * self._ICX_DECIMALS)
        self.assertEqual(True, tx_result['status'])

        actual_icx_token_amount = icx_call(icon_integrate_test_base=super(),
                                           from_=self.network_owner_wallet.get_address(),
                                           to_=self.icx_token_address,
                                           method="balanceOf",
                                           params={"_owner": str(self.network_owner_address)})
        self.assertEqual(hex(self._INITIAL_ICX_SEND_AMOUNT * self._ICX_DECIMALS), actual_icx_token_amount)

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

        self.assertEqual(True, deploy_tx_result["status"])
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

        self.assertEqual(True, deploy_tx_result["status"])
        self.smart_token_2_address = deploy_tx_result["scoreAddress"]

        # deploy ST1 converter
        deploy_params = {"_token": str(self.smart_token_1_address),
                         "_registry": str(self.score_registry_address),
                         "_maxConversionFee": 0,
                         "_connectorToken": str(self.icx_token_address),
                         "_connectorWeight": 50}

        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("converter"),
                                        from_=self.network_owner_wallet,
                                        params=deploy_params)
        self.assertEqual(int(True), deploy_tx_result['status'])
        self.st1_converter = deploy_tx_result['scoreAddress']

        # deploy ST2 converter
        deploy_params = {"_token": str(self.smart_token_2_address),
                         "_registry": str(self.score_registry_address),
                         "_maxConversionFee": 0,
                         "_connectorToken": str(self.icx_token_address),
                         "_connectorWeight": 50}

        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("converter"),
                                        from_=self.network_owner_wallet,
                                        params=deploy_params)
        self.assertEqual(int(True), deploy_tx_result['status'])
        self.st2_converter = deploy_tx_result['scoreAddress']

        # deploy network
        deploy_tx_result = deploy_score(icon_integrate_test_base=super(),
                                        content_as_bytes=get_content_as_bytes("network"),
                                        from_=self.network_owner_wallet,
                                        params={})
        self.assertEqual(int(True), deploy_tx_result['status'])
        self.score_registry_address = deploy_tx_result['scoreAddress']

    def test_convert(self):
        pass

    def test_getExpectedReturn(self):
        pass

    def test_registerIcxToken(self):
        pass

    def test_convert_with_short_path(self):
        pass

    def test_convert_with_long_path(self):
        pass

    def test_tokenFallback(self):
        pass
