from os import path

from iconservice import ZERO_SCORE_ADDRESS

from iconsdk.builder.transaction_builder import CallTransactionBuilder, DeployTransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

from contract_generator.builder import Builder
from contract_generator.writer import ZipWriter
from contracts.interfaces.abc_score_registry import ABCScoreRegistry


class TestScoreRegistry(IconIntegrateTestBase):

    # TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"

    def setUp(self):
        super().setUp()

        self.icon_service = None
        # if you want to send request to network, uncomment next line
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        tx_result = self._deploy_score(content_as_bytes=self._get_content_as_bytes("score_registry"), params={})
        self.assertEqual(tx_result['status'], int(True))
        self.score_registry_address = tx_result['scoreAddress']

    @staticmethod
    def _get_content_as_bytes(score_name: str):
        dir_path = path.abspath(path.dirname(__file__))
        root_path = path.abspath(path.join(dir_path, '../..'))
        contracts_path = path.join(root_path, 'contracts')

        builder = Builder(contracts_path, [score_name])
        zip_writer = ZipWriter()
        builder.build(zip_writer)
        contents_as_bytes = zip_writer.to_bytes()
        return contents_as_bytes

    def _deploy_score(self, content_as_bytes: bytes, to: str = SCORE_INSTALL_ADDRESS, params: dict = None) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(content_as_bytes) \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def _icx_call(self, from_: str, to_: str, method: str, params: dict = None):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(from_) \
            .to(to_) \
            .method(method) \
            .params(params) \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        return response

    def _transaction_call(self, from_: KeyWallet, to_: str, method: str, params: dict = None) -> dict:
        # Generates an instance of transaction for calling method in SCORE.
        transaction = CallTransactionBuilder() \
            .from_(from_.get_address()) \
            .to(to_) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method(method) \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, from_)

        # Sends the transaction to the network
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        return tx_result

    def test_score_registry_property(self):
        actual_owner = self._icx_call(from_=self._test1.get_address(), to_=self.score_registry_address,
                                      method="getOwner")
        self.assertEqual(self._test1.get_address(), actual_owner)

        actual_new_owner = self._icx_call(from_=self._test1.get_address(), to_=self.score_registry_address,
                                          method="getNewOwner")
        self.assertEqual(str(ZERO_SCORE_ADDRESS), actual_new_owner)

        # when deploy ScoreRegistry, score registry address should be registered by default
        score_registry_id = ABCScoreRegistry.SCORE_REGISTRY
        score_registry_address = self._icx_call(from_=self._test1.get_address(), to_=self.score_registry_address,
                                                method="getAddress", params={"_scoreName": score_registry_id})
        self.assertEqual(self.score_registry_address, score_registry_address)

    def test_score_registry_register_and_unregister_address(self):
        network_id = ABCScoreRegistry.BANCOR_NETWORK
        network_address = "cx" + "1" * 40

        # success case: register network address
        send_tx_params = {"_scoreName": network_id, "_scoreAddress": network_address}
        tx_result = self._transaction_call(from_=self._test1, to_=self.score_registry_address, method="registerAddress", params=send_tx_params)
        self.assertEqual(True, tx_result['status'])

        # check registered network address
        actual_registered_address = self._icx_call(from_=self._test1.get_address(), to_=self.score_registry_address,
                                                      method="getAddress",
                                                      params={"_scoreName": network_id})
        self.assertEqual(network_address, actual_registered_address)

        # success case: overwrite network address
        new_network_address = "cx" + "2" * 40
        send_tx_params = {"_scoreName": network_id, "_scoreAddress": new_network_address}

        tx_result = self._transaction_call(from_=self._test1, to_=self.score_registry_address, method="registerAddress",
                                           params=send_tx_params)
        self.assertEqual(True, tx_result['status'])

        # check registered new network address
        actual_registered_address = self._icx_call(from_=self._test1.get_address(), to_=self.score_registry_address,
                                                   method="getAddress",
                                                   params={"_scoreName": network_id})
        self.assertEqual(new_network_address, actual_registered_address)

        # failure case: non_owner try to register address
        non_owner = KeyWallet.create()
        send_tx_params = {"_scoreName": network_id, "_scoreAddress": network_address}
        self.assertRaises(AssertionError, self._transaction_call, from_=non_owner, to_=self.score_registry_address, method="registerAddress",
                                           params=send_tx_params)

        # failure case: try to register invalid address
        send_tx_params = {"_scoreName": network_id, "_scoreAddress": str(ZERO_SCORE_ADDRESS)}
        self.assertRaises(AssertionError, self._transaction_call, from_=self._test1, to_=self.score_registry_address,
                          method="registerAddress",
                          params=send_tx_params)

        # failure case: try to register eoa address
        eoa_address = KeyWallet.create().get_address()
        send_tx_params = {"_scoreName": network_id, "_scoreAddress": eoa_address}
        self.assertRaises(AssertionError, self._transaction_call, from_=self._test1, to_=self.score_registry_address,
                          method="registerAddress",
                          params=send_tx_params)

        # failure case: non_owner try to unregister network address
        send_tx_params = {"_scoreName": network_id}
        self.assertRaises(AssertionError, self._transaction_call, from_=non_owner, to_=self.score_registry_address,
                          method="unregisterAddress",
                          params=send_tx_params)

        # failure case: try to unregister address which has not been registered
        non_registered_id = ABCScoreRegistry.BANCOR_FORMULA
        send_tx_params = {"_scoreName": non_registered_id}
        self.assertRaises(AssertionError, self._transaction_call, from_=self._test1, to_=self.score_registry_address,
                          method="unregisterAddress", params=send_tx_params)

        # success case: unregister network address
        send_tx_params = {"_scoreName": network_id}

        tx_result = self._transaction_call(from_=self._test1, to_=self.score_registry_address,
                                           method="unregisterAddress", params=send_tx_params)
        self.assertEqual(True, tx_result['status'])

        network_address = self._icx_call(from_=self._test1.get_address(), to_=self.score_registry_address,
                                         method="getAddress", params={"_scoreName": network_id})
        self.assertEqual(str(ZERO_SCORE_ADDRESS), network_address)
