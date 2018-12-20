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

import os
from io import BytesIO
from zipfile import ZipFile
from os import walk, path, mkdir
from shutil import rmtree
from contract_builder.config import config

dir_contracts = path.abspath("..").replace('_builder', 's')
dir_build = dir_contracts.replace('contracts', 'contract_build')
dir_init = path.join(dir_contracts, '__init__.py')


class InMemoryZip:
    """
    The basic idea behind was to be able to transfer files or a folder (with sub folders) as zipped memory
    via the communication to another machine.
    """

    def __init__(self, data=None):
        """Creates an in-memory file (zip archive)

        :param data: initial data
        """
        self.in_memory = BytesIO(data)
        self.zf = ZipFile(self.in_memory, mode="w")

    def get_data_as_bytes(self) -> bytes:
        """Retrieves the whole file as buffer

        :return: bytes of the in-memory file
        """
        self.in_memory.seek(0)
        return self.in_memory.read()

    def build_in_memory_zip(self, contracts: list=None) -> bytes:
        """
        Builds the target contracts in the memory zip with the list of contracts.
        If it is empty, the target should be all of the contracts in config.
        Returns bytes of the in-memory file

        :param contracts: list of contracts
        :return: bytes of the memory file
        """
        for c in contracts if contracts is not None else config:
            self._create_contract(c)
            self._create_dependencies(c, config[c])

        return self.get_data_as_bytes()

    def extract(self) -> None:
        """
        Extracts all files in memory below given path;
        the underlying zip file module is clever enough to create the necessary path if not existing.

        :return: None
        """
        _create_build_dir()
        self.zf.extractall(dir_build)

    def list_content(self) -> list:
        """Gets the list of zip files entries (ZipInfo instances)

        :return: a list of class ZipInfo instances for files in the archive
        """
        return self.zf.infolist()

    def _create_contract(self, contract: str) -> None:
        """
        Makes the contract the in-memory file with the path.
        But package.json should be on the root directory.

        :param contract: the target contract
        :return: None
        """
        # Builds the dir of contract
        dir_contract = path.join(dir_contracts, contract)

        for root, dirs, files in walk(dir_contract):
            for file in files:
                origin_file_path = path.join(root, file)
                new_file_path = path.join(contract if not file == "package.json" else '', contract,
                                          origin_file_path[len(dir_contract) + len(os.sep):])
                self.zf.write(origin_file_path, new_file_path)

    def _create_dependencies(self, contract: str, dependencies: list) -> None:
        """Makes all of dependencies the in-memory file with the path.

        :param contract: the target contract
        :param dependencies: dependencies' paths of the contract
        :return: None
        """
        for dependency in dependencies:
            origin_file_path = dir_contracts + dependency
            new_file_path = contract + dependency
            self.zf.write(origin_file_path, new_file_path)


def _create_build_dir() -> None:
    """
    Creates the build dir with checking if it is or not.
    If it exists already, it should be removed at first.

    The directory path is as below.
    /build

    :return: None
    """
    if path.isdir(dir_build):
        rmtree(dir_build)

    mkdir(dir_build)


if __name__ == '__main__':
    contracts1 = ["smart_token", "irc_token"]

    # samples
    mz = InMemoryZip()
    # builds the in-memory zip of target contacts and returns it as bytes
    in_memory_zip_as_bytes = mz.build_in_memory_zip(contracts1)
    # extracts all files in memory below given path;
    mz.extract()
    # gets the list of the content
    print(mz.list_content())



