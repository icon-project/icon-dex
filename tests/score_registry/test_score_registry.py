import unittest

from iconservice import *
from iconservice.base.exception import RevertException
from iconservice.base.message import Message

from contracts.utility.owned import Owned
from contracts.score_registry.score_registry import ScoreRegistry
from tests import patch, ScorePatcher, create_db


# noinspection PyUnresolvedReferences
class TestScoreRegistry(unittest.TestCase):

    def setUp(self):
        self.patcher = ScorePatcher(ScoreRegistry)
        self.patcher.start()

        self.score_address = Address.from_string("cx" + "1" * 40)
        self.registry_score = ScoreRegistry(create_db(self.score_address))

        self.registry_owner = Address.from_string("hx" + "1" * 40)
        with patch([(IconScoreBase, 'msg', Message(self.registry_owner))]):
            self.registry_score.on_install()
            Owned.on_install.assert_called_with(self.registry_score)

            # success case: when deploy ScoreRegistry, score registry address should be registered by default
            self.assertEqual \
                (self.score_address,
                 self.registry_score._score_address[self.registry_score.SCORE_REGISTRY.encode()])

    def tearDown(self):
        self.patcher.stop()

    def test_getAddressFromBytesName(self):
        # success case: search the registered score address
        registered_score_name_bytes = self.registry_score.SCORE_REGISTRY.encode()
        actual_address = self.registry_score.getAddressFromBytesName(registered_score_name_bytes)
        self.assertEqual(self.score_address, actual_address)

        # success case: search the score address which has not been registered (should return zero score address)
        unregistered_score_name_bytes = self.registry_score.BANCOR_NETWORK.encode()
        actual_address = self.registry_score.getAddressFromBytesName(unregistered_score_name_bytes)
        self.assertEqual(ZERO_SCORE_ADDRESS, actual_address)

    def test_getAddressFromStringName(self):
        # success case: search the registered score address
        registered_score_name = self.registry_score.SCORE_REGISTRY
        actual_address = self.registry_score.getAddressFromStringName(registered_score_name)
        self.assertEqual(self.score_address, actual_address)

        # success case: search the score address which has not been registered (should return zero score address)
        unregistered_score_name = self.registry_score.BANCOR_NETWORK
        actual_address = self.registry_score.getAddressFromStringName(unregistered_score_name)
        self.assertEqual(ZERO_SCORE_ADDRESS, actual_address)

    def test_registerAddress(self):
        eoa_address = Address.from_string("hx" + "3" * 40)
        bancor_network_id = self.registry_score.BANCOR_NETWORK
        bancor_network_address = Address.from_string("cx" + "2" * 40)

        with patch([(IconScoreBase, 'msg', Message(self.registry_owner))]):
            # failure case: invalid register score address
            self.assertRaises(RevertException,
                              self.registry_score.registerAddress,
                              bancor_network_id, ZERO_SCORE_ADDRESS)

            # failure case: try to register eoa address
            self.assertRaises(RevertException,
                              self.registry_score.registerAddress,
                              bancor_network_id, eoa_address)

            # success case : register bancor network
            self.registry_score.registerAddress(bancor_network_id, bancor_network_address)
            encoded_bancor_network_id = bancor_network_id.encode()
            self.assertEqual(bancor_network_address,
                             self.registry_score._score_address[encoded_bancor_network_id])
            self.registry_score.AddressUpdate.assert_called_with(bancor_network_id, bancor_network_address)

    def test_unregisterAddress(self):
        bancor_network_id = self.registry_score.BANCOR_NETWORK
        encoded_bancor_network_id = bancor_network_id.encode()
        bancor_network_address = Address.from_string("cx" + "2" * 40)

        # register bancor network
        self.registry_score._score_address[encoded_bancor_network_id] = bancor_network_address

        with patch([(IconScoreBase, 'msg', Message(self.registry_owner))]):
            # failure case: try to unregister not recorded score address
            non_registered_id = self.registry_score.BANCOR_FORMULA
            self.assertRaises(RevertException,
                              self.registry_score.unregisterAddress,
                              non_registered_id)

            # success case: unregister score address which has been registered
            self.registry_score.unregisterAddress(bancor_network_id)
            self.assertEqual(None, self.registry_score._score_address[encoded_bancor_network_id])

            self.registry_score.AddressUpdate.assert_called_with(bancor_network_id, ZERO_SCORE_ADDRESS)
