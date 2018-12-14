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

from os import path, mkdir, makedirs
from shutil import copytree, rmtree, move, copy

from contract_builder.config import config

dir_contracts = path.abspath("..").replace('_builder', 's')
dir_build = dir_contracts.replace('contracts', 'contract_build')


def _create_build_dir():
    """
    Creates the build dir with checking if it is or not.
    If it exists already, it should be removed at first.

    The directory path is as below.
    /build

    :return:
    """
    if path.isdir(dir_build):
        rmtree(dir_build)

    mkdir(dir_build)


def build_contracts_on_file_system(contracts: list =None) -> None:
    """
    Builds contracts fully on the file system with the list of contracts
    if it is empty, target should be all of contracts.

    :param contracts: list of contracts
    :return: None
    """
    _create_build_dir()

    for c in contracts if contracts is not None else config:
        _create_contract(c)
        _create_dependencies(c, config[c])


def _create_contract(contract: str) -> None:
    """
    Creates the contract fully.
    But package.json should be on root directory.

    :param contract: the target contract
    :return: None
    """
    # Builds the dir of contract
    dir_contract = path.join(dir_contracts, contract)
    new_dir_contract = path.join(dir_build, contract)
    mkdir(new_dir_contract)

    # Builds the sub dir of contract
    new_sub_dir_contract = path.join(new_dir_contract, contract)

    # Copies the contract
    copytree(dir_contract, new_sub_dir_contract)

    # Moves the package.json file to the parent dir
    dir_package_json = path.join(new_sub_dir_contract, 'package.json')
    new_dir_package_json = path.join(new_dir_contract, 'package.json')
    move(dir_package_json, new_dir_package_json)


def _create_dependencies(contract: str, dependencies: list) -> None:
    """Creates all of dependencies from the file paths.

    :param contract: the target contract
    :param dependencies: dependencies' paths of the contract
    :return: None
    """
    new_dir_contract = path.join(dir_build, contract)

    for file in dependencies:
        path_file = dir_contracts + file
        new_path_file = new_dir_contract + file

        # Creates directories at first.
        new_dir_file = new_path_file.rsplit('/', 1)[0]
        makedirs(new_dir_file, exist_ok=True)

        # Copies files then.
        copy(path_file, new_path_file)


# samples
contracts1 = ["smart_token", "irc_token"]
contracts2 = ["smart_token"]

build_contracts_on_file_system(contracts1)
build_contracts_on_file_system(contracts2)
# builds all of contracts in config
build_contracts_on_file_system()
