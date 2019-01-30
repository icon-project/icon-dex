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
from iconservice.base.exception import RevertException
from iconsdk.wallet.wallet import KeyWallet
from tbears.libs.icon_integrate_test import IconIntegrateTestBase

from tests.integration_tests import create_address
from tests.integration_tests.utils import get_content_as_bytes, deploy_score, icx_call, transaction_call, \
    icx_transfer_call, update_governance


class TestIcxToken(IconIntegrateTestBase):
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

        # Deploys score_registry SCORE
        tx_result = deploy_score(icon_integrate_test_base=super(),
                                 content_as_bytes=get_content_as_bytes("icx_token"), from_=self._test1, params={})

        self.icx_token_address = tx_result['scoreAddress']

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

    def test_icx_token_property(self):
        # Checks if token name is right
        actual_token_name = self._icx_call_default(to_=self.icx_token_address, method="name")
        self.assertEqual("icx_token", actual_token_name)

        # Checks if token symbol is right
        actual_token_symbol = self._icx_call_default(to_=self.icx_token_address, method="symbol")
        self.assertEqual("ICX", actual_token_symbol)

        # Checks if total supply is 0
        actual_total_supply = self._icx_call_default(self.icx_token_address, "totalSupply")
        self.assertEqual(0, int(actual_total_supply, 0))

        # Checks if decimals is right
        actual_decimals = self._icx_call_default(self.icx_token_address, "decimals")
        self.assertEqual(18, int(actual_decimals, 0))

        # Checks if result of operating method `balance of` is 0
        actual_owner_balance = self._icx_call_default(self.icx_token_address, "balanceOf",
                                                      {"_owner": str(self.icx_token_address)})
        self.assertEqual(0, int(actual_owner_balance, 0))

        # Checks if result of operating method `getOwner` is the actual owner
        actual_owner = self._icx_call_default(self.icx_token_address, "getOwner")
        self.assertEqual(self._test1.get_address(), actual_owner)

        # Checks if result of operating method `getNewOwner is the zero score address
        actual_new_owner = self._icx_call_default(self.icx_token_address, "getNewOwner")
        self.assertEqual(str(ZERO_SCORE_ADDRESS), actual_new_owner)

    def test_icx_token_deposit(self):
        initial_owner_icx_value = self._get_icx_value(Address.from_string(self._test1.get_address()))
        deposit_icx = 10 * 10 ** 18

        # Success case: deposit 10 icx to icx_token
        tx_result = self._transaction_call_default(self.icx_token_address, "deposit", {}, deposit_icx)

        # Checks event log (Issuance)
        self.assertEqual(deposit_icx, int(tx_result["eventLogs"][0]["data"][0], 0))

        # Checks event log (Transfer)
        self.assertEqual(self.icx_token_address, tx_result["eventLogs"][1]["indexed"][1])
        self.assertEqual(self._test1.get_address(), tx_result["eventLogs"][1]["indexed"][2])
        self.assertEqual(deposit_icx, int(tx_result["eventLogs"][1]["indexed"][3], 0))

        # Checks owner token balance (should be 10 * 10 ** 18)
        actual_icx_balance = self._icx_call_default(self.icx_token_address, "balanceOf",
                                                    {"_owner": self._test1.get_address()})
        self.assertEqual(deposit_icx, int(actual_icx_balance, 0))

        # Checks icx token's total supply (should be 10 * 10 ** 18)
        actual_total_supply = self._icx_call_default(self.icx_token_address, "totalSupply")
        self.assertEqual(deposit_icx, int(actual_total_supply, 0))

        owner_icx_value = self._get_icx_value(Address.from_string(self._test1.get_address()))
        icx_token_score_value = self._get_icx_value(Address.from_string(self.icx_token_address))

        # Checks real ICX coin balance
        self.assertEqual(int(initial_owner_icx_value, 0) - deposit_icx, int(owner_icx_value, 0))
        self.assertEqual(deposit_icx, int(icx_token_score_value, 0))

        # Success case: deposit 10 icx without calling deposit method by sending icx to score address
        icx_transfer_call(super(), self._test1, self.icx_token_address, deposit_icx, self.icon_service)

        # Checks owner token balance (should be 10 * 10 ** 18 * 2)
        actual_icx_balance = self._icx_call_default(self.icx_token_address, "balanceOf",
                                                    {"_owner": self._test1.get_address()})
        self.assertEqual(deposit_icx * 2, int(actual_icx_balance, 0))

        # Checks icx token's total supply (should be 10 * 10 ** 18 * 2)
        actual_total_supply = self._icx_call_default(self.icx_token_address, "totalSupply")
        self.assertEqual(deposit_icx * 2, int(actual_total_supply, 0))

    def test_icx_token_withdraw_to(self):
        initial_owner_icx_value = self._get_icx_value(Address.from_string(self._test1.get_address()))
        icx_receiver = create_address()
        deposit_icx = 10 * 10 ** 18

        # Starts setting for testing withdraw
        # Deposits 10 icx to owner
        self._transaction_call_default(self.icx_token_address, "deposit", {}, deposit_icx)

        # Checks owner token balance (should be 10 * 10 ** 18)
        actual_icx_balance = self._icx_call_default(self.icx_token_address, "balanceOf",
                                                    {"_owner": self._test1.get_address()})
        self.assertEqual(deposit_icx, int(actual_icx_balance, 0))

        # Checks icx token's total supply (should be 10 * 10 ** 18)
        actual_total_supply = self._icx_call_default(self.icx_token_address, "totalSupply")
        self.assertEqual(deposit_icx, int(actual_total_supply, 0))

        # ##### end setting for testing withdraw

        # Failure case: try to withdraw icx more than deposited icx value
        withdraw_icx = 12 * 10 ** 18
        send_tx_params = {"_amount": withdraw_icx, "_to": str(icx_receiver)}
        self.assertRaises(AssertionError, self._transaction_call_default,
                          self.icx_token_address, "withdrawTo", send_tx_params)

        # Failure case: input _amount less than 0 as a parameter
        withdraw_icx = -(10 * 10 ** 18)
        send_tx_params = {"_amount": withdraw_icx, "_to": str(icx_receiver)}
        self.assertRaises(AssertionError, self._transaction_call_default,
                          self.icx_token_address, "withdrawTo", send_tx_params)

        # Success case: withdraw 10 icx from the score to icx_receiver
        withdraw_icx = 10 * 10 ** 18
        send_tx_params = {"_amount": withdraw_icx, "_to": str(icx_receiver)}
        tx_result = self._transaction_call_default(self.icx_token_address, "withdrawTo", send_tx_params)

        # Checks event log (ICXTransfer)
        self.assertEqual(self.icx_token_address, tx_result["eventLogs"][0]["indexed"][1])
        self.assertEqual(str(icx_receiver), tx_result["eventLogs"][0]["indexed"][2])
        self.assertEqual(withdraw_icx, int(tx_result["eventLogs"][0]["indexed"][3], 0))

        # Checks event log (Destruction)
        self.assertEqual(withdraw_icx, int(tx_result["eventLogs"][1]["data"][0], 0))

        # Checks owner token balance (should be 0)
        actual_icx_balance = self._icx_call_default(self.icx_token_address, "balanceOf",
                                                    {"_owner": self._test1.get_address()})
        self.assertEqual(0, int(actual_icx_balance, 0))

        # Checks icx token's total supply (should be 0)
        actual_total_supply = self._icx_call_default(self.icx_token_address, "totalSupply")
        self.assertEqual(0, int(actual_total_supply, 0))

        # Checks real ICX coin balance
        owner_icx_value = self._get_icx_value(Address.from_string(self._test1.get_address()))
        receiver_icx_value = self._get_icx_value(icx_receiver)
        icx_token_score_value = self._get_icx_value(Address.from_string(self.icx_token_address))

        self.assertEqual(int(initial_owner_icx_value, 0) - withdraw_icx, int(owner_icx_value, 0))
        self.assertEqual(withdraw_icx, int(receiver_icx_value, 0))
        self.assertEqual(0, int(icx_token_score_value, 0))

    def test_icx_token_transfer(self):
        icx_receiver = create_address()
        deposit_icx = 10 * 10 ** 18

        # ##### start setting for testing withdraw

        # Deposits 10 icx to owner
        self._transaction_call_default(self.icx_token_address, "deposit", {}, deposit_icx)

        # Checks owner token balance (should be 10 * 10 ** 18)
        actual_icx_balance = self._icx_call_default(self.icx_token_address, "balanceOf",
                                                    {"_owner": self._test1.get_address()})
        self.assertEqual(deposit_icx, int(actual_icx_balance, 0))

        # Checks icx token's total supply (should be 10 * 10 ** 18)
        actual_total_supply = self._icx_call_default(self.icx_token_address, "totalSupply")
        self.assertEqual(deposit_icx, int(actual_total_supply, 0))

        # #### end setting for testing withdraw

        # Failure case: cannot transfer icx to icx token SCORE
        transfer_icx = 10 * 10 ** 18
        send_tx_params = {"_to": self.icx_token_address, "_value": transfer_icx}
        self.assertRaises(AssertionError, self._transaction_call_default,
                          self.icx_token_address, "transfer", send_tx_params)

        # Success case: transfer 10 icx to icx_receiver
        send_tx_params = {"_to": str(icx_receiver), "_value": hex(transfer_icx)}
        self._transaction_call_default(self.icx_token_address, "transfer", send_tx_params)

        # Checks owner token balance (should be 0)
        actual_icx_balance = self._icx_call_default(self.icx_token_address, "balanceOf",
                                                    {"_owner": self._test1.get_address()})
        self.assertEqual(0, int(actual_icx_balance, 0))

        # Checks owner token balance (should be 10 icx)
        actual_icx_balance = self._icx_call_default(self.icx_token_address, "balanceOf", {"_owner": str(icx_receiver)})
        self.assertEqual(transfer_icx, int(actual_icx_balance, 0))

        # Checks icx token's total supply (should be 10 icx)
        actual_total_supply = self._icx_call_default(self.icx_token_address, "totalSupply")
        self.assertEqual(deposit_icx, int(actual_total_supply, 0))

        # Checks real ICX coin balance
        receiver_icx_value = self._get_icx_value(icx_receiver)
        icx_token_score_value = self._get_icx_value(Address.from_string(self.icx_token_address))

        # Receiver's real ICX coin balance should be 0 until withdraw
        self.assertEqual(0, int(receiver_icx_value, 0))

        # Icx token SCORE real ICX coin balance should be 10 until withdraw
        self.assertEqual(deposit_icx, int(icx_token_score_value, 0))

    def test_icx_token_transfer_ownership(self):
        new_owner = KeyWallet.create()

        # Failure case: only owner can transfer ownership
        send_tx_params = {"_newOwner": new_owner.get_address()}
        self.assertRaises(AssertionError, transaction_call, super(), self._genesis, self.icx_token_address,
                          "transferOwnerShip", send_tx_params)

        # Failure case: cannot set new owner as previous owner
        send_tx_params = {"_newOwner": self._test1.get_address()}
        self.assertRaises(RevertException, self._icx_call_default, self.icx_token_address, "transferOwnerShip",
                          send_tx_params)

        # Success case: owner can transfer ownership
        send_tx_params = {"_newOwner": new_owner.get_address()}
        self._transaction_call_default(self.icx_token_address, "transferOwnerShip", send_tx_params)

        # Checks current owner, ownership can not be transferred until accept ownership
        actual_owner = self._icx_call_default(self.icx_token_address, "getOwner")
        self.assertEqual(self._test1.get_address(), actual_owner)

        # Failure case: except new owner, no one cannot accept ownership even owner
        self.assertRaises(AssertionError, self._transaction_call_default, self.icx_token_address, "acceptOwnerShip", {})
        self.assertRaises(AssertionError, transaction_call, super(), self._genesis, self.icx_token_address,
                          "acceptOwnerShip", {})

        # Success case: accept ownership
        tx_result = transaction_call(super(), new_owner, self.icx_token_address, "acceptOwnerShip", {})

        # Checks event log
        self.assertEqual(self._test1.get_address(), tx_result["eventLogs"][0]["indexed"][1])
        self.assertEqual(new_owner.get_address(), tx_result["eventLogs"][0]["indexed"][2])

        # Checks current owner
        actual_owner = self._icx_call_default(self.icx_token_address, "getOwner")
        self.assertEqual(new_owner.get_address(), actual_owner)
