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

from os import path

from iconsdk.icon_service import IconService
from iconsdk.builder.transaction_builder import CallTransactionBuilder, DeployTransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

from contract_generator.builder import Builder
from contract_generator.writer import ZipWriter


def get_content_as_bytes(score_name: str):
    dir_path = path.abspath(path.dirname(__file__))
    root_path = path.abspath(path.join(dir_path, '../..'))
    contracts_path = path.join(root_path, 'contracts')

    builder = Builder(contracts_path, [score_name])
    zip_writer = ZipWriter()
    builder.build(zip_writer)
    contents_as_bytes = zip_writer.to_bytes()
    return contents_as_bytes


def deploy_score(icon_integrate_test_base: IconIntegrateTestBase, content_as_bytes: bytes, from_: KeyWallet,
                 to_: str = SCORE_INSTALL_ADDRESS, params: dict = None, icon_service: IconService = None) -> dict:
    # Generates an instance of transaction for deploying SCORE.
    transaction = DeployTransactionBuilder() \
        .from_(from_.get_address()) \
        .to(to_) \
        .step_limit(100_000_000_000) \
        .nid(3) \
        .nonce(100) \
        .content_type("application/zip") \
        .content(content_as_bytes) \
        .params(params) \
        .build()

    # Returns the signed transaction object having a signature
    signed_transaction = SignedTransaction(transaction, from_)

    # process the transaction
    tx_result = icon_integrate_test_base.process_transaction(signed_transaction, icon_service)

    assert 'status', 'scoreAddress' in tx_result
    assert 1 == tx_result['status']
    return tx_result


def icx_call(icon_integrate_test_base: IconIntegrateTestBase, from_: str, to_: str, method: str,
             params: dict = None, icon_service: IconService = None):
    # Generates a call instance using the CallBuilder
    call = CallBuilder().from_(from_) \
        .to(to_) \
        .method(method) \
        .params(params) \
        .build()

    # Sends the call request
    response = icon_integrate_test_base.process_call(call, icon_service)
    return response


def transaction_call(icon_integrate_test_base: IconIntegrateTestBase, from_: KeyWallet, to_: str, method: str, params: dict = None, icon_service: IconService = None) -> dict:
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
    tx_result = icon_integrate_test_base.process_transaction(signed_transaction, icon_service)

    assert 'status' in tx_result
    assert 1 == tx_result['status']

    return tx_result
