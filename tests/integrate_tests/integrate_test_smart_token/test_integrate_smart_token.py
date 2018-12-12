# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
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

from tests.integrate_tests import create_address
from tests.integrate_tests.test_integrate_base import TestIntegrateBase

if TYPE_CHECKING:
    from iconservice.base.address import Address


class TestIntegrateSmartToken(TestIntegrateBase):
    _TOKEN_INITIAL_TOTAL_SUPPLY_WITH_DECIMALS = 10000 * 10 ** 18

    def setUp(self):
        super().setUp()
        self.st_token_name = 'test_token'
        self.st_token_symbol = 'TST'
        self.st_token_init_supply = hex(10000)
        self.st_token_decimals = hex(18)
        deploy_params = {"_name": self.st_token_name,
                         "_symbol": self.st_token_symbol,
                         "_initialSupply": self.st_token_init_supply,
                         "_decimals": self.st_token_decimals}
        deploy_result = self._deploy_score("integrate_test_smart_token/smart_token", deploy_params)
        self.assertEqual(deploy_result.status, int(True))
        self.smart_token_address = deploy_result.score_address

    def _deploy_score(self, score_path: str, deploy_params: dict, update_score_addr: 'Address' = None) -> Any:
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

    def _call_score(self, score_address: 'Address', sender_address: 'Address', method: str, params: dict = {}):
        tx = self._make_score_call_tx(sender_address,
                                      score_address,
                                      method,
                                      params)

        prev_block, tx_results = self._make_and_req_block([tx])
        self._write_precommit_state(prev_block)
        return tx_results[0]

    def test_smart_token_property(self):
        actual_token_name = self._query_score(self.smart_token_address, "name")
        self.assertEqual(self.st_token_name, actual_token_name)

        actual_token_symbol = self._query_score(self.smart_token_address, "symbol")
        self.assertEqual(self.st_token_symbol, actual_token_symbol)

        actual_total_supply = self._query_score(self.smart_token_address, "totalSupply")
        self.assertEqual(self._TOKEN_INITIAL_TOTAL_SUPPLY_WITH_DECIMALS, actual_total_supply)

        actual_owner_balance = self._query_score(self.smart_token_address, "balanceOf", {"_owner": str(self._owner)})
        self.assertEqual(self._TOKEN_INITIAL_TOTAL_SUPPLY_WITH_DECIMALS, actual_owner_balance)

        actual_owner = self._query_score(self.smart_token_address, "getOwner")
        self.assertEqual(self._owner, actual_owner)

        actual_new_owner = self._query_score(self.smart_token_address, "getNewOwner")
        self.assertEqual(ZERO_SCORE_ADDRESS, actual_new_owner)

    def test_smart_token_disable_transfer(self):
        # success case: transfer_possibility's initial setting should be True
        actual_transfer_possibility = self._query_score(self.smart_token_address, "getTransferPossibility")
        self.assertEqual(True, actual_transfer_possibility)

        # failure case: only owner can disable transfer
        send_tx_params = {"_disable": "0x1"}
        tx_result = self._call_score(self.smart_token_address, self._genesis, "disableTransfer", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # success case: owner can change transfer_possibility True -> False
        send_tx_params = {"_disable": "0x1"}
        tx_result = self._call_score(self.smart_token_address, self._owner, "disableTransfer", send_tx_params)
        self.assertEqual(True, tx_result.status)

        actual_transfer_possibility = self._query_score(self.smart_token_address, "getTransferPossibility")
        self.assertEqual(False, actual_transfer_possibility)

        # success case: owner can change transfer_possibility False -> True
        send_tx_params = {"_disable": "0x0"}
        tx_result = self._call_score(self.smart_token_address, self._owner, "disableTransfer", send_tx_params)
        self.assertEqual(True, tx_result.status)

        actual_transfer_possibility = self._query_score(self.smart_token_address, "getTransferPossibility")
        self.assertEqual(True, actual_transfer_possibility)

    def test_smart_token_issue(self):
        issue_balance = 10 * 10 ** 18
        # failure case: only owner can issue the smart token
        send_tx_params = {"_to": str(self._fee_treasury), "_amount": hex(issue_balance)}
        tx_result = self._call_score(self.smart_token_address, self._genesis, "issue", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # failure case: try to issue and transfer to invalid address
        send_tx_params = {"_to": str(ZERO_SCORE_ADDRESS), "_amount": hex(issue_balance)}
        tx_result = self._call_score(self.smart_token_address, self._owner, "issue", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # success case: owner can issue smart token
        send_tx_params = {"_to": str(self._fee_treasury), "_amount": hex(issue_balance)}
        tx_result = self._call_score(self.smart_token_address, self._owner, "issue", send_tx_params)
        self.assertEqual(True, tx_result.status)

        # check the issued balance and total supply
        actual_owner_balance = self._query_score(self.smart_token_address,
                                                 "balanceOf",
                                                 {"_owner": str(self._fee_treasury)})
        self.assertEqual(issue_balance, actual_owner_balance)
        actual_total_supply = self._query_score(self.smart_token_address, "totalSupply")
        self.assertEqual(self._TOKEN_INITIAL_TOTAL_SUPPLY_WITH_DECIMALS + issue_balance, actual_total_supply)

    def test_smart_token_destroy(self):
        destroy_balance = 10 * 10 ** 18
        issue_balance = 10 * 10 ** 18
        # issue smart token to fee treasury
        send_tx_params = {"_to": str(self._fee_treasury), "_amount": hex(issue_balance)}
        tx_result = self._call_score(self.smart_token_address, self._owner, "issue", send_tx_params)
        self.assertEqual(True, tx_result.status)

        # failure case: try to input negative amount
        send_tx_params = {"_from": str(self._owner), "_amount": hex(-1)}
        tx_result = self._call_score(self.smart_token_address, self._owner, "destroy", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # failure case: address who has insufficient amount of token can not destroy
        actual_owner_balance = self._query_score(self.smart_token_address,
                                                 "balanceOf",
                                                 {"_owner": str(self._genesis)})
        self.assertEqual(0, actual_owner_balance)

        send_tx_params = {"_from": str(self._genesis), "_amount": hex(destroy_balance)}
        tx_result = self._call_score(self.smart_token_address, self._genesis, "destroy", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # failure case: if transaction sender and _from is different and not owner, should raise error
        send_tx_params = {"_from": str(self._fee_treasury), "_amount": hex(destroy_balance)}
        tx_result = self._call_score(self.smart_token_address, self._genesis, "destroy", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # success case: owner can destroy their own token
        owner_balance_before_destroy = self._query_score(self.smart_token_address,
                                                         "balanceOf",
                                                         {"_owner": str(self._owner)})
        total_supply_before_destroy = self._query_score(self.smart_token_address, "totalSupply")

        send_tx_params = {"_from": str(self._owner), "_amount": hex(destroy_balance)}
        tx_result = self._call_score(self.smart_token_address, self._owner, "destroy", send_tx_params)
        self.assertEqual(True, tx_result.status)

        owner_balance_after_destroy = self._query_score(self.smart_token_address,
                                                        "balanceOf",
                                                        {"_owner": str(self._owner)})
        self.assertEqual(owner_balance_before_destroy - destroy_balance, owner_balance_after_destroy)

        total_supply_after_destroy = self._query_score(self.smart_token_address, "totalSupply")
        self.assertEqual(total_supply_before_destroy - destroy_balance, total_supply_after_destroy)

        # success case: owner can destroy others token (other address has sufficient amount of token)
        other_balance_before_destroy = self._query_score(self.smart_token_address,
                                                         "balanceOf",
                                                         {"_owner": str(self._fee_treasury)})
        self.assertEqual(issue_balance, other_balance_before_destroy)
        total_supply_before_destroy = self._query_score(self.smart_token_address, "totalSupply")

        send_tx_params = {"_from": str(self._fee_treasury), "_amount": hex(issue_balance)}
        tx_result = self._call_score(self.smart_token_address, self._owner, "destroy", send_tx_params)
        self.assertEqual(True, tx_result.status)

        other_balance_after_destroy = self._query_score(self.smart_token_address,
                                                        "balanceOf",
                                                        {"_owner": str(self._fee_treasury)})
        total_supply_after_destroy = self._query_score(self.smart_token_address, "totalSupply")

        self.assertEqual(0, other_balance_after_destroy)
        self.assertEqual(total_supply_before_destroy - issue_balance, total_supply_after_destroy)

    def test_smart_token_transfer_ownership(self):
        new_owner = create_address()

        # failure case: only owner can transfer ownership
        send_tx_params = {"_newOwner": str(new_owner)}
        tx_result = self._call_score(self.smart_token_address, self._genesis, "transferOwnerShip", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # failure case: cannot set new owner as previous owner
        send_tx_params = {"_newOwner": str(self._owner)}
        tx_result = self._call_score(self.smart_token_address, self._owner, "transferOwnerShip", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # success case: owner can transfer ownership
        send_tx_params = {"_newOwner": str(new_owner)}
        tx_result = self._call_score(self.smart_token_address, self._owner, "transferOwnerShip", send_tx_params)
        self.assertEqual(True, tx_result.status)

        # check current owner, ownership can not be transferred until accept ownership
        actual_owner = self._query_score(self.smart_token_address, "getOwner")
        self.assertEqual(self._owner, actual_owner)

        # failure case: except new owner, no one cannot accept ownership even owner
        tx_result = self._call_score(self.smart_token_address, self._owner, "acceptOwnerShip", {})
        self.assertEqual(False, tx_result.status)

        tx_result = self._call_score(self.smart_token_address, self._genesis, "acceptOwnerShip", {})
        self.assertEqual(False, tx_result.status)

        # success case: accept ownership
        tx_result = self._call_score(self.smart_token_address, new_owner, "acceptOwnerShip", {})
        self.assertEqual(True, tx_result.status)

        # check event log
        self.assertEqual(self._owner, tx_result.event_logs[0].indexed[1])
        self.assertEqual(new_owner, tx_result.event_logs[0].indexed[2])

        # check current owner
        actual_owner = self._query_score(self.smart_token_address, "getOwner")
        self.assertEqual(new_owner, actual_owner)

