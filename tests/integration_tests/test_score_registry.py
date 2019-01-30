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

from iconservice import ZERO_SCORE_ADDRESS
from iconservice.base.address import GOVERNANCE_SCORE_ADDRESS
from iconsdk.wallet.wallet import KeyWallet
from tbears.libs.icon_integrate_test import IconIntegrateTestBase

from contracts.interfaces.abc_score_registry import ABCScoreRegistry
from tests.integration_tests.utils import get_content_as_bytes, deploy_score, icx_call, transaction_call, update_governance


class TestScoreRegistry(IconIntegrateTestBase):

    # TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"

    def setUp(self):
        super().setUp()

        self.icon_service = None
        # If you want to send request to network, uncomment next line
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        update_governance(icon_integrate_test_base=super(), from_=self._test1, params={})

        # Adds import white list
        params = {"importStmt": "{'iconservice.iconscore.icon_score_constant' : ['T']}"}
        transaction_call(icon_integrate_test_base=super(),
                         from_=self._test1,
                         to_=str(GOVERNANCE_SCORE_ADDRESS),
                         method="addImportWhiteList",
                         params=params,
                         icon_service=self.icon_service)

        # Deploys score_registry SCORE
        tx_result = deploy_score(icon_integrate_test_base=super(),
                                 content_as_bytes=get_content_as_bytes("score_registry"), from_=self._test1, params={})

        self.score_registry_address = tx_result['scoreAddress']

    def test_score_registry_property(self):
        actual_owner = icx_call(icon_integrate_test_base=super(), from_=self._test1.get_address(),
                                to_=self.score_registry_address, method="getOwner", icon_service=self.icon_service)
        self.assertEqual(self._test1.get_address(), actual_owner)

        actual_new_owner = icx_call(icon_integrate_test_base=super(), from_=self._test1.get_address(),
                                    to_=self.score_registry_address, method="getNewOwner", icon_service=self.icon_service)
        self.assertEqual(str(ZERO_SCORE_ADDRESS), actual_new_owner)

        # when deploy ScoreRegistry, score registry address should be registered by default
        score_registry_id = ABCScoreRegistry.SCORE_REGISTRY
        score_registry_address = icx_call(icon_integrate_test_base=super(), from_=self._test1.get_address(),
                                          to_=self.score_registry_address, method="getAddress",
                                          params={"_scoreName": score_registry_id}, icon_service=self.icon_service)
        self.assertEqual(self.score_registry_address, score_registry_address)

    def test_score_registry_register_and_unregister_address(self):
        network_id = ABCScoreRegistry.BANCOR_NETWORK
        network_address = "cx" + "1" * 40

        # success case: register network address
        send_tx_params = {"_scoreName": network_id, "_scoreAddress": network_address}
        tx_result = transaction_call(icon_integrate_test_base=super(), from_=self._test1,
                                     to_=self.score_registry_address, method="registerAddress", params=send_tx_params,
                                     icon_service=self.icon_service)
        self.assertEqual(True, tx_result['status'])

        # check registered network address
        actual_registered_address = icx_call(icon_integrate_test_base=super(), from_=self._test1.get_address(), to_=self.score_registry_address,
                                             method="getAddress", params={"_scoreName": network_id}, icon_service=self.icon_service)
        self.assertEqual(network_address, actual_registered_address)

        # success case: overwrite network address
        new_network_address = "cx" + "2" * 40
        send_tx_params = {"_scoreName": network_id, "_scoreAddress": new_network_address}

        tx_result = transaction_call(icon_integrate_test_base=super(), from_=self._test1,
                                     to_=self.score_registry_address, method="registerAddress",
                                     params=send_tx_params, icon_service=self.icon_service)
        self.assertEqual(True, tx_result['status'])

        # check registered new network address
        actual_registered_address = icx_call(icon_integrate_test_base=super(), from_=self._test1.get_address(),
                                             to_=self.score_registry_address, method="getAddress",
                                             params={"_scoreName": network_id}, icon_service=self.icon_service)
        self.assertEqual(new_network_address, actual_registered_address)

        # failure case: non_owner try to register address
        non_owner = KeyWallet.create()
        send_tx_params = {"_scoreName": network_id, "_scoreAddress": network_address}
        self.assertRaises(AssertionError, transaction_call, icon_integrate_test_base=super(), from_=non_owner,
                          to_=self.score_registry_address, method="registerAddress", params=send_tx_params,
                          icon_service=self.icon_service)

        # failure case: try to register invalid address
        send_tx_params = {"_scoreName": network_id, "_scoreAddress": str(ZERO_SCORE_ADDRESS)}
        self.assertRaises(AssertionError, transaction_call, icon_integrate_test_base=super(), from_=self._test1,
                          to_=self.score_registry_address, method="registerAddress", params=send_tx_params,
                          icon_service=self.icon_service)

        # failure case: try to register eoa address
        eoa_address = KeyWallet.create().get_address()
        send_tx_params = {"_scoreName": network_id, "_scoreAddress": eoa_address}
        self.assertRaises(AssertionError, transaction_call, icon_integrate_test_base=super(), from_=self._test1,
                          to_=self.score_registry_address, method="registerAddress", params=send_tx_params,
                          icon_service=self.icon_service)

        # failure case: non_owner try to unregister network address
        send_tx_params = {"_scoreName": network_id}
        self.assertRaises(AssertionError, transaction_call, icon_integrate_test_base=super(), from_=non_owner,
                          to_=self.score_registry_address, method="unregisterAddress", params=send_tx_params,
                          icon_service=self.icon_service)

        # failure case: try to unregister address which has not been registered
        non_registered_id = ABCScoreRegistry.BANCOR_FORMULA
        send_tx_params = {"_scoreName": non_registered_id}
        self.assertRaises(AssertionError, transaction_call, icon_integrate_test_base=super(), from_=self._test1,
                          to_=self.score_registry_address, method="unregisterAddress", params=send_tx_params,
                          icon_service=self.icon_service)

        # success case: unregister network address
        send_tx_params = {"_scoreName": network_id}
        tx_result = transaction_call(icon_integrate_test_base=super(), from_=self._test1,
                                     to_=self.score_registry_address, method="unregisterAddress", params=send_tx_params,
                                     icon_service=self.icon_service)
        self.assertEqual(True, tx_result['status'])

        network_address = icx_call(icon_integrate_test_base=super(), from_=self._test1.get_address(),
                                   to_=self.score_registry_address, method="getAddress",
                                   params={"_scoreName": network_id}, icon_service=self.icon_service)
        self.assertEqual(str(ZERO_SCORE_ADDRESS), network_address)
