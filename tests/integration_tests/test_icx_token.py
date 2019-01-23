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

from typing import TYPE_CHECKING, Any

from iconservice import ZERO_SCORE_ADDRESS

from tests.integration_tests import create_address
from tests.integration_tests.test_integrate_base import TestIntegrateBase

if TYPE_CHECKING:
    from iconservice.base.address import Address


class TestIcxToken(TestIntegrateBase):
    _TOKEN_INITIAL_TOTAL_SUPPLY_WITH_DECIMALS = 10000 * 10 ** 18

    def setUp(self):
        super().setUp()
        deploy_result = self._deploy_score("icx_token")
        self.assertEqual(deploy_result.status, int(True))
        self.icx_token_address = deploy_result.score_address

    def _deploy_score(self, score_path: str, deploy_params: dict = {}, update_score_addr: 'Address' = None) -> Any:
        address = ZERO_SCORE_ADDRESS
        if update_score_addr:
            address = update_score_addr

        tx = self._make_deploy_tx("",
                                  score_path,
                                  self._owner,
                                  address,
                                  deploy_params=deploy_params)

        prev_block, tx_results = self._make_and_req_block([tx])
        self._write_precommit_state(prev_block)
        return tx_results[0]

    def _query_score(self, score_address: 'Address', method: str, params: dict = None):
        query_request = {
            "version": self._version,
            "from": self._owner,
            "to": score_address,
            "dataType": "call",
            "data": {
                "method": method,
                "params": {} if params is None else params
            }
        }
        return self._query(query_request)

    def _get_icx_value(self, address: 'Address'):
        query_request = {
            "address": address
        }
        return self._query(query_request, "icx_getBalance")

    def _call_score(self,
                    score_address: 'Address',
                    sender_address: 'Address',
                    method: str = "",
                    params: dict = {},
                    value: int = 0):
        tx = self._make_score_call_tx(sender_address,
                                      score_address,
                                      method,
                                      params,
                                      value)

        prev_block, tx_results = self._make_and_req_block([tx])
        self._write_precommit_state(prev_block)
        return tx_results[0]

    def test_icx_token_property(self):
        actual_token_name = self._query_score(self.icx_token_address, "name")
        self.assertEqual("icx_token", actual_token_name)

        actual_token_symbol = self._query_score(self.icx_token_address, "symbol")
        self.assertEqual("ICX", actual_token_symbol)

        actual_total_supply = self._query_score(self.icx_token_address, "totalSupply")
        self.assertEqual(0, actual_total_supply)

        actual_decimals = self._query_score(self.icx_token_address, "decimals")
        self.assertEqual(18, actual_decimals
                         )
        actual_owner_balance = self._query_score(self.icx_token_address, "balanceOf", {"_owner": str(self._owner)})
        self.assertEqual(0, actual_owner_balance)

        actual_owner = self._query_score(self.icx_token_address, "getOwner")
        self.assertEqual(self._owner, actual_owner)

        actual_new_owner = self._query_score(self.icx_token_address, "getNewOwner")
        self.assertEqual(ZERO_SCORE_ADDRESS, actual_new_owner)

    def test_icx_token_deposit(self):
        initial_owner_icx_value = self._get_icx_value(self._owner)
        deposit_icx = 10 * 10 ** 18

        # success case: deposit 10 icx to icx_token
        tx_result = self._call_score(self.icx_token_address, self._owner, "deposit", {}, deposit_icx)
        self.assertEqual(True, tx_result.status)

        # check event log (Issuance)
        self.assertEqual(deposit_icx, tx_result.event_logs[0].data[0])

        # check event log (Transfer)
        self.assertEqual(self.icx_token_address, tx_result.event_logs[1].indexed[1])
        self.assertEqual(self._owner, tx_result.event_logs[1].indexed[2])
        self.assertEqual(deposit_icx, tx_result.event_logs[1].indexed[3])

        # check owner token balance (should be 10 * 10 ** 18)
        actual_icx_balance = self._query_score(self.icx_token_address, "balanceOf", {"_owner": str(self._owner)})
        self.assertEqual(deposit_icx, actual_icx_balance)

        # check icx token's total supply (should be 10 * 10 ** 18)
        actual_total_supply = self._query_score(self.icx_token_address, "totalSupply")
        self.assertEqual(deposit_icx, actual_total_supply)

        owner_icx_value = self._get_icx_value(self._owner)
        icx_token_score_value = self._get_icx_value(self.icx_token_address)
        # check real ICX coin balance
        self.assertEqual(initial_owner_icx_value - deposit_icx, owner_icx_value)
        self.assertEqual(deposit_icx, icx_token_score_value)

        # success case: deposit 10 icx without calling deposit method by sending icx to score address
        tx = self._make_icx_send_tx(self._owner, self.icx_token_address, deposit_icx)
        prev_block, tx_results = self._make_and_req_block([tx])
        self._write_precommit_state(prev_block)

        self.assertEqual(True, tx_results[0].status)

        # check owner token balance (should be 10 * 10 ** 18 * 2)
        actual_icx_balance = self._query_score(self.icx_token_address, "balanceOf", {"_owner": str(self._owner)})
        self.assertEqual(deposit_icx * 2, actual_icx_balance)

        # check icx token's total supply (should be 10 * 10 ** 18 * 2)
        actual_total_supply = self._query_score(self.icx_token_address, "totalSupply")
        self.assertEqual(deposit_icx * 2, actual_total_supply)

    def test_icx_token_withdraw_to(self):
        initial_owner_icx_value = self._get_icx_value(self._owner)
        icx_receiver = create_address()
        deposit_icx = 10 * 10 ** 18

        # ##### start setting for testing withdraw

        # deposit 10 icx to owner
        tx_result = self._call_score(self.icx_token_address, self._owner, "deposit", {}, deposit_icx)
        self.assertEqual(True, tx_result.status)

        # check owner token balance (should be 10 * 10 ** 18)
        actual_icx_balance = self._query_score(self.icx_token_address, "balanceOf", {"_owner": str(self._owner)})
        self.assertEqual(deposit_icx, actual_icx_balance)

        # check icx token's total supply (should be 10 * 10 ** 18)
        actual_total_supply = self._query_score(self.icx_token_address, "totalSupply")
        self.assertEqual(deposit_icx, actual_total_supply)

        # ##### end setting for testing withdraw

        # failure case: try to withdraw icx more than deposited icx value
        withdraw_icx = 12 * 10 ** 18
        send_tx_params = {"_amount": hex(withdraw_icx), "_to": str(icx_receiver)}
        tx_result = self._call_score(self.icx_token_address, self._owner, "withdrawTo", send_tx_params)
        self.assertEqual(False, tx_result.status)
        self.assertEqual("Out of balance", tx_result.failure.message)

        # failure case: input _amount less than 0 as a parameter
        withdraw_icx = -(10 * 10 ** 18)
        send_tx_params = {"_amount": hex(withdraw_icx), "_to": str(icx_receiver)}
        tx_result = self._call_score(self.icx_token_address, self._owner, "withdrawTo", send_tx_params)
        self.assertEqual(False, tx_result.status)
        self.assertEqual("Amount should be greater than 0", tx_result.failure.message)

        # success case: withdraw 10 icx from the score to icx_receiver
        withdraw_icx = 10 * 10 ** 18
        send_tx_params = {"_amount": hex(withdraw_icx), "_to": str(icx_receiver)}
        tx_result = self._call_score(self.icx_token_address, self._owner, "withdrawTo", send_tx_params)
        self.assertEqual(True, tx_result.status)

        # check event log (ICXTransfer)
        self.assertEqual(self.icx_token_address, tx_result.event_logs[0].indexed[1])
        self.assertEqual(icx_receiver, tx_result.event_logs[0].indexed[2])
        self.assertEqual(withdraw_icx, tx_result.event_logs[0].indexed[3])
        # check event log (Destruction)
        self.assertEqual(withdraw_icx, tx_result.event_logs[1].data[0])

        # check owner token balance (should be 0)
        actual_icx_balance = self._query_score(self.icx_token_address, "balanceOf", {"_owner": str(self._owner)})
        self.assertEqual(0, actual_icx_balance)

        # check icx token's total supply (should be 0)
        actual_total_supply = self._query_score(self.icx_token_address, "totalSupply")
        self.assertEqual(0, actual_total_supply)

        # check real ICX coin balance
        owner_icx_value = self._get_icx_value(self._owner)
        receiver_icx_value = self._get_icx_value(icx_receiver)
        icx_token_score_value = self._get_icx_value(self.icx_token_address)

        self.assertEqual(initial_owner_icx_value - withdraw_icx, owner_icx_value)
        self.assertEqual(withdraw_icx, receiver_icx_value)
        self.assertEqual(0, icx_token_score_value)

    def test_icx_token_transfer(self):
        icx_receiver = create_address()
        deposit_icx = 10 * 10 ** 18

        # ##### start setting for testing withdraw

        # deposit 10 icx to owner
        tx_result = self._call_score(self.icx_token_address, self._owner, "deposit", {}, deposit_icx)
        self.assertEqual(True, tx_result.status)

        # check owner token balance (should be 10 * 10 ** 18)
        actual_icx_balance = self._query_score(self.icx_token_address, "balanceOf", {"_owner": str(self._owner)})
        self.assertEqual(deposit_icx, actual_icx_balance)

        # check icx token's total supply (should be 10 * 10 ** 18)
        actual_total_supply = self._query_score(self.icx_token_address, "totalSupply")
        self.assertEqual(deposit_icx, actual_total_supply)

        # ##### end setting for testing withdraw

        # failure case: cannot transfer icx to icx token SCORE
        transfer_icx = 10 * 10 ** 18
        send_tx_params = {"_to": str(self.icx_token_address), "_value": hex(transfer_icx)}
        tx_result = self._call_score(self.icx_token_address, self._owner, "transfer", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # success case: transfer 10 icx to icx_receiver
        send_tx_params = {"_to": str(icx_receiver), "_value": hex(transfer_icx)}
        tx_result = self._call_score(self.icx_token_address, self._owner, "transfer", send_tx_params)
        self.assertEqual(True, tx_result.status)

        # check owner token balance (should be 0)
        actual_icx_balance = self._query_score(self.icx_token_address, "balanceOf", {"_owner": str(self._owner)})
        self.assertEqual(0, actual_icx_balance)

        # check owner token balance (should be 10 icx)
        actual_icx_balance = self._query_score(self.icx_token_address, "balanceOf", {"_owner": str(icx_receiver)})
        self.assertEqual(transfer_icx, actual_icx_balance)

        # check icx token's total supply (should be 10 icx)
        actual_total_supply = self._query_score(self.icx_token_address, "totalSupply")
        self.assertEqual(deposit_icx, actual_total_supply)

        # check real ICX coin balance
        receiver_icx_value = self._get_icx_value(icx_receiver)
        icx_token_score_value = self._get_icx_value(self.icx_token_address)

        # receiver's real ICX coin balance should be 0 until withdraw
        self.assertEqual(0, receiver_icx_value)
        # icx token SCORE real ICX coin balance should be 10 until withdraw
        self.assertEqual(deposit_icx, icx_token_score_value)

    def test_icx_token_transfer_ownership(self):
        new_owner = create_address()

        # failure case: only owner can transfer ownership
        send_tx_params = {"_newOwner": str(new_owner)}
        tx_result = self._call_score(self.icx_token_address, self._genesis, "transferOwnerShip", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # failure case: cannot set new owner as previous owner
        send_tx_params = {"_newOwner": str(self._owner)}
        tx_result = self._call_score(self.icx_token_address, self._owner, "transferOwnerShip", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # success case: owner can transfer ownership
        send_tx_params = {"_newOwner": str(new_owner)}
        tx_result = self._call_score(self.icx_token_address, self._owner, "transferOwnerShip", send_tx_params)
        self.assertEqual(True, tx_result.status)

        # check current owner, ownership can not be transferred until accept ownership
        actual_owner = self._query_score(self.icx_token_address, "getOwner")
        self.assertEqual(self._owner, actual_owner)

        # failure case: except new owner, no one cannot accept ownership even owner
        tx_result = self._call_score(self.icx_token_address, self._owner, "acceptOwnerShip", {})
        self.assertEqual(False, tx_result.status)

        tx_result = self._call_score(self.icx_token_address, self._genesis, "acceptOwnerShip", {})
        self.assertEqual(False, tx_result.status)

        # success case: accept ownership
        tx_result = self._call_score(self.icx_token_address, new_owner, "acceptOwnerShip", {})
        self.assertEqual(True, tx_result.status)

        # check event log
        self.assertEqual(self._owner, tx_result.event_logs[0].indexed[1])
        self.assertEqual(new_owner, tx_result.event_logs[0].indexed[2])

        # check current owner
        actual_owner = self._query_score(self.icx_token_address, "getOwner")
        self.assertEqual(new_owner, actual_owner)
