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
from iconservice.base.address import Address, GOVERNANCE_SCORE_ADDRESS
from iconsdk.wallet.wallet import KeyWallet
from tbears.libs.icon_integrate_test import IconIntegrateTestBase

from tests.integration_tests import create_address
from tests.integration_tests.utils import get_content_as_bytes, deploy_score, icx_call, transaction_call, \
    update_governance


class TestSmartToken(IconIntegrateTestBase):
    _TOKEN_INITIAL_TOTAL_SUPPLY_WITH_DECIMALS = 10000 * 10 ** 18

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

        self.st_token_name = 'test_token'
        self.st_token_symbol = 'TST'
        self.st_token_init_supply = hex(10000)
        self.st_token_decimals = hex(18)
        deploy_params = {"_name": self.st_token_name,
                         "_symbol": self.st_token_symbol,
                         "_initialSupply": self.st_token_init_supply,
                         "_decimals": self.st_token_decimals}

        # Deploys smart_token SCORE
        tx_result = deploy_score(icon_integrate_test_base=super(), content_as_bytes=get_content_as_bytes("smart_token"),
                                 from_=self._test1, params=deploy_params)

        self.smart_token_address = tx_result['scoreAddress']

    def _get_icx_value(self, address: 'Address'):
        query_request = {
            "address": address
        }
        return self._query(query_request, "icx_getBalance")

    def _icx_call_default(self, to_: str = None, method: str = None, params: dict = None):
        return icx_call(icon_integrate_test_base=super(), from_=self._test1.get_address(),
                        to_=to_, method=method, params=params, icon_service=self.icon_service)

    def _transaction_call_default(self, to_: str = None, method: str = None, params: dict = None, value: int = 0):
        return transaction_call(icon_integrate_test_base=super(), from_=self._test1, to_=to_,
                                method=method, params=params, value=value, icon_service=self.icon_service)

    def test_smart_token_property(self):
        actual_token_name = self._icx_call_default(self.smart_token_address, "name")
        self.assertEqual(self.st_token_name, actual_token_name)

        actual_token_symbol = self._icx_call_default(self.smart_token_address, "symbol")
        self.assertEqual(self.st_token_symbol, actual_token_symbol)

        actual_total_supply = self._icx_call_default(self.smart_token_address, "totalSupply")
        self.assertEqual(self._TOKEN_INITIAL_TOTAL_SUPPLY_WITH_DECIMALS, int(actual_total_supply, 0))

        actual_owner_balance = self._icx_call_default(self.smart_token_address, "balanceOf",
                                                      {"_owner": self._test1.get_address()})
        self.assertEqual(self._TOKEN_INITIAL_TOTAL_SUPPLY_WITH_DECIMALS, int(actual_owner_balance, 0))

        actual_owner = self._icx_call_default(self.smart_token_address, "getOwner")
        self.assertEqual(self._test1.get_address(), actual_owner)

        actual_new_owner = self._icx_call_default(self.smart_token_address, "getNewOwner")
        self.assertEqual(str(ZERO_SCORE_ADDRESS), actual_new_owner)

    def test_smart_token_disable_transfer(self):
        # Success case: transfer_possibility's initial setting should be True
        actual_transfer_possibility = self._icx_call_default(self.smart_token_address, "getTransferPossibility")
        self.assertTrue(int(actual_transfer_possibility, 0))

        # Failure case: only owner can disable transfer
        send_tx_params = {"_disable": "0x1"}
        self.assertRaises(AssertionError, transaction_call, super(), self._genesis, self.smart_token_address,
                          "disableTransfer", send_tx_params)

        # Success case: owner can change transfer_possibility True -> False
        send_tx_params = {"_disable": "0x1"}
        transaction_call(super(), self._test1, self.smart_token_address,
                         "disableTransfer", send_tx_params)

        actual_transfer_possibility = self._icx_call_default(self.smart_token_address, "getTransferPossibility")
        self.assertFalse(int(actual_transfer_possibility, 0))

        # Success case: owner can change transfer_possibility False -> True
        send_tx_params = {"_disable": "0x0"}
        transaction_call(super(), self._test1, self.smart_token_address, "disableTransfer", send_tx_params)
        actual_transfer_possibility = self._icx_call_default(self.smart_token_address, "getTransferPossibility")
        self.assertTrue(int(actual_transfer_possibility, 0))

    def test_smart_token_transfer(self):
        token_receiver = create_address()
        transfer_token = 10

        # Success case: transfer 10 smart token to receiver
        send_tx_params = {"_to": str(token_receiver), "_value": hex(transfer_token)}
        self._transaction_call_default(self.smart_token_address, "transfer", send_tx_params)

        # Failure case: try to transfer when transfer possibility is False

        # Changes transfer possibility
        send_tx_params = {"_disable": "0x1"}
        self._transaction_call_default(self.smart_token_address, "disableTransfer", send_tx_params)

        # Transfers 10 smart token to receiver
        send_tx_params = {"_to": str(token_receiver), "_value": hex(transfer_token)}
        self.assertRaises(AssertionError, self._transaction_call_default, self.smart_token_address, "transfer",
                          send_tx_params)

    def test_smart_token_issue(self):
        issue_balance = 10 * 10 ** 18
        # Failure case: only owner can issue the smart token
        send_tx_params = {"_to": self._fee_treasury.get_address(), "_amount": hex(issue_balance)}
        self.assertRaises(AssertionError, transaction_call, super(), self._genesis, self.smart_token_address, "issue",
                          send_tx_params)

        # Failure case: try to issue and transfer to invalid address
        send_tx_params = {"_to": str(ZERO_SCORE_ADDRESS), "_amount": hex(issue_balance)}
        self.assertRaises(AssertionError, self._transaction_call_default, self.smart_token_address, "issue",
                          send_tx_params)

        # Success case: owner can issue smart token
        send_tx_params = {"_to": self._fee_treasury.get_address(), "_amount": hex(issue_balance)}
        self._transaction_call_default(self.smart_token_address, "issue", send_tx_params)

        # Checks the issued balance and total supply
        actual_owner_balance = self._icx_call_default(self.smart_token_address, "balanceOf",
                                                      {"_owner": self._fee_treasury.get_address()})
        self.assertEqual(issue_balance, int(actual_owner_balance, 0))

        actual_total_supply = self._icx_call_default(self.smart_token_address, "totalSupply")
        self.assertEqual(self._TOKEN_INITIAL_TOTAL_SUPPLY_WITH_DECIMALS + issue_balance, int(actual_total_supply, 0))

    def test_smart_token_destroy(self):
        destroy_balance = 10 * 10 ** 18
        issue_balance = 10 * 10 ** 18

        # Issues smart token to fee treasury
        send_tx_params = {"_to": self._fee_treasury.get_address(), "_amount": hex(issue_balance)}
        tx_result = self._transaction_call_default(self.smart_token_address, "issue", send_tx_params)

        # Failure case: try to input negative amount
        send_tx_params = {"_from": self._test1.get_address(), "_amount": hex(-1)}
        self.assertRaises(AssertionError, self._transaction_call_default, self.smart_token_address,
                          "destroy", send_tx_params)

        # Failure case: address who has insufficient amount of token can not destroy
        actual_owner_balance = self._icx_call_default(self.smart_token_address, "balanceOf",
                                                      {"_owner": self._genesis.get_address()})
        self.assertEqual(0, int(actual_owner_balance, 0))

        send_tx_params = {"_from": self._genesis.get_address(), "_amount": hex(destroy_balance)}
        self.assertRaises(AssertionError, transaction_call, super(), self._genesis, self.smart_token_address, "destroy",
                          send_tx_params)

        # Failure case: if transaction sender and _from is different and not owner, should raise error
        send_tx_params = {"_from": self._fee_treasury.get_address(), "_amount": hex(destroy_balance)}
        self.assertRaises(AssertionError, transaction_call, super(), self._genesis, self.smart_token_address, "destroy",
                          send_tx_params)

        # Success case: owner can destroy their own token
        owner_balance_before_destroy = self._icx_call_default(self.smart_token_address, "balanceOf",
                                                              {"_owner": self._test1.get_address()})
        total_supply_before_destroy = self._icx_call_default(self.smart_token_address, "totalSupply")

        send_tx_params = {"_from": self._test1.get_address(), "_amount": hex(destroy_balance)}
        self._transaction_call_default(self.smart_token_address, "destroy", send_tx_params)

        owner_balance_after_destroy = self._icx_call_default(self.smart_token_address, "balanceOf",
                                                             {"_owner": self._test1.get_address()})
        self.assertEqual(int(owner_balance_before_destroy, 0) - destroy_balance, int(owner_balance_after_destroy, 0))

        total_supply_after_destroy = self._icx_call_default(self.smart_token_address, "totalSupply")
        self.assertEqual(int(total_supply_before_destroy, 0) - destroy_balance, int(total_supply_after_destroy, 0))

        # Success case: owner can destroy others token (other address has sufficient amount of token)
        other_balance_before_destroy = self._icx_call_default(self.smart_token_address, "balanceOf",
                                                              {"_owner": self._fee_treasury.get_address()})
        self.assertEqual(issue_balance, int(other_balance_before_destroy, 0))
        total_supply_before_destroy = self._icx_call_default(self.smart_token_address, "totalSupply")

        send_tx_params = {"_from": self._fee_treasury.get_address(), "_amount": hex(issue_balance)}
        self._transaction_call_default(self.smart_token_address, "destroy", send_tx_params)

        other_balance_after_destroy = self._icx_call_default(self.smart_token_address, "balanceOf",
                                                             {"_owner": self._fee_treasury.get_address()})
        total_supply_after_destroy = self._icx_call_default(self.smart_token_address, "totalSupply")

        self.assertEqual(0, int(other_balance_after_destroy, 0))
        self.assertEqual(int(total_supply_before_destroy, 0) - issue_balance, int(total_supply_after_destroy, 0))

    def test_smart_token_transfer_ownership(self):
        new_owner = KeyWallet.create()

        # Failure case: only owner can transfer ownership
        send_tx_params = {"_newOwner": new_owner.get_address()}
        self.assertRaises(AssertionError, transaction_call, super(), self._genesis, self.smart_token_address,
                          "transferOwnerShip", send_tx_params)

        # Failure case: cannot set new owner as previous owner
        send_tx_params = {"_newOwner": self._test1.get_address()}
        self.assertRaises(AssertionError, transaction_call, super(), self._genesis, self.smart_token_address,
                          "transferOwnerShip", send_tx_params)

        # Success case: owner can transfer ownership
        send_tx_params = {"_newOwner": new_owner.get_address()}
        self._transaction_call_default(self.smart_token_address, "transferOwnerShip", send_tx_params)

        # Checks current owner, ownership can not be transferred until accept ownership
        actual_owner = self._icx_call_default(self.smart_token_address, "getOwner")
        self.assertEqual(self._test1.get_address(), actual_owner)

        # Failure case: except new owner, no one cannot accept ownership even owner
        self.assertRaises(AssertionError, self._transaction_call_default, self.smart_token_address, "acceptOwnerShip",
                          {})

        self.assertRaises(AssertionError, transaction_call, super(), self._genesis, self.smart_token_address,
                          "acceptOwnerShip", {})

        # Success case: accept ownership
        tx_result = transaction_call(super(), new_owner, self.smart_token_address, "acceptOwnerShip", {})

        # Checks event log
        self.assertEqual(self._test1.get_address(), tx_result["eventLogs"][0]["indexed"][1])
        self.assertEqual(new_owner.get_address(), tx_result["eventLogs"][0]["indexed"][2])

        # Checks current owner
        actual_owner = self._icx_call_default(self.smart_token_address, "getOwner")
        self.assertEqual(new_owner.get_address(), actual_owner)
