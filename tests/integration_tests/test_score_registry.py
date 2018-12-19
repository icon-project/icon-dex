from typing import TYPE_CHECKING, Any

from iconservice import ZERO_SCORE_ADDRESS

from tests.integration_tests import create_address
from tests.integration_tests.test_integrate_base import TestIntegrateBase
from iconservice.base.address import Address

if TYPE_CHECKING:
    from iconservice.base.address import Address


class TestScoreRegistry(TestIntegrateBase):
    def setUp(self):
        super().setUp()
        deploy_result = self._deploy_score("score_registry", {})
        self.assertEqual(deploy_result.status, int(True))
        self.score_registry_address = deploy_result.score_address

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

    def test_score_registry_property(self):
        actual_owner = self._query_score(self.score_registry_address, "getOwner")
        self.assertEqual(self._owner, actual_owner)

        actual_new_owner = self._query_score(self.score_registry_address, "getNewOwner")
        self.assertEqual(ZERO_SCORE_ADDRESS, actual_new_owner)

        score_registry_id = "ScoreRegistry"
        score_registry_address = self._query_score(self.score_registry_address,
                                                   "getAddressFromStringName",
                                                   {"_scoreName": score_registry_id})
        self.assertEqual(self.score_registry_address, score_registry_address)

    def test_score_registry_register_and_unregister(self):
        bancor_network_id = "BancorNetwork"
        bancor_network_address = Address.from_string("cx" + "1" * 40)

        # success case: register bancor network address
        send_tx_params = {"_scoreName": bancor_network_id, "_scoreAddress": str(bancor_network_address)}
        tx_result = self._call_score(self.score_registry_address, self._owner, "registerAddress", send_tx_params)
        self.assertEqual(True, tx_result.status)

        # check registered bancor network address
        actual_bancor_network_address = self._query_score(self.score_registry_address,
                                                          "getAddressFromStringName",
                                                          {"_scoreName": bancor_network_id})
        self.assertEqual(bancor_network_address, actual_bancor_network_address)

        # success case: overwrite bancor network address
        new_bancor_network_address = Address.from_string("cx" + "2" * 40)
        send_tx_params = {"_scoreName": bancor_network_id, "_scoreAddress": str(new_bancor_network_address)}
        tx_result = self._call_score(self.score_registry_address, self._owner, "registerAddress", send_tx_params)
        self.assertEqual(True, tx_result.status)

        # check registered new bancor network address
        actual_bancor_network_address = self._query_score(self.score_registry_address,
                                                          "getAddressFromStringName",
                                                          {"_scoreName": bancor_network_id})
        self.assertEqual(new_bancor_network_address, actual_bancor_network_address)

        # failure case: non_owner try to register address
        non_owner = create_address()
        send_tx_params = {"_scoreName": bancor_network_id, "_scoreAddress": str(bancor_network_address)}
        tx_result = self._call_score(self.score_registry_address, non_owner, "registerAddress", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # failure case: try to register invalid address
        send_tx_params = {"_scoreName": bancor_network_id, "_scoreAddress": str(ZERO_SCORE_ADDRESS)}
        tx_result = self._call_score(self.score_registry_address, self._owner, "registerAddress", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # failure case: try to register eoa address
        eoa_address = create_address()
        send_tx_params = {"_scoreName": bancor_network_id, "_scoreAddress": str(eoa_address)}
        tx_result = self._call_score(self.score_registry_address, self._owner, "registerAddress", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # failure case: non_owner try to unregister bancor network address
        send_tx_params = {"_scoreName": bancor_network_id}
        tx_result = self._call_score(self.score_registry_address, non_owner, "unregisterAddress", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # failure case: try to unregister address which has not been registered
        non_registered_id = "BancorForMula"
        send_tx_params = {"_scoreName": non_registered_id}
        tx_result = self._call_score(self.score_registry_address, self._owner, "unregisterAddress", send_tx_params)
        self.assertEqual(False, tx_result.status)

        # success case: unregister bancor network address
        send_tx_params = {"_scoreName": bancor_network_id}
        tx_result = self._call_score(self.score_registry_address, self._owner, "unregisterAddress", send_tx_params)
        self.assertEqual(True, tx_result.status)

        actual_bancor_network_address = self._query_score(self.score_registry_address,
                                                          "getAddressFromStringName",
                                                          {"_scoreName": bancor_network_id})
        self.assertEqual(ZERO_SCORE_ADDRESS, actual_bancor_network_address)
