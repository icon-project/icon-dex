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

from os import path, walk
from collections import namedtuple

from contract_generator.writer import Writer
from contract_generator.config import config


class Builder:

    def __init__(self, contracts_path: str, contracts: list = None):
        """
        1. Reads the contract and its dependencies info on config
        2. Sets Contract in namedtuple
            - name : contract name
            - path_list : contract's files and its dependencies path list in tuple
            ex. [(current_file_path, new_file_path), (..), ..]

        :param contracts_path: contracts path
        :param contracts: contracts list
        """
        self.contract_list = []
        self._contracts_path = contracts_path
        Contract = namedtuple("Contract", "name path_list")
        for c in contracts if contracts else config:
            self.contract = Contract(name=c, path_list=[])
            self._append_contract_on_path_list(c)
            self._append_dependencies_on_path_list(c, config[c])
            self.contract_list.append(self.contract)

    def build(self, writer: Writer) -> None:
        """Builds contracts by calling writer's write method

        :param writer: FileWriter or ZipWriter
        :return: None
        """
        writer.write(self.contract_list)

    def _append_contract_on_path_list(self, contract: str) -> None:
        """Appends the contract and its files on path list as a tuple

        :param contract: contract name
        :return: None
        """
        cur_contract_dir = path.join(self._contracts_path, contract)

        for file_path, dirs, files in walk(cur_contract_dir):
            # Skips for tests dir because of only for testing
            if path.basename(file_path) == 'tests':
                continue

            for filename in files:
                if file_path.find('__pycache__') != -1:
                    continue

                cur_file_path = path.join(file_path, filename)
                if filename == 'package.json':
                    new_file_path = path.join(contract, filename)
                else:
                    new_file_path = cur_file_path.replace(self._contracts_path, str(contract))
                path_tuple = (cur_file_path, new_file_path)
                self.contract.path_list.append(path_tuple)

    def _append_dependencies_on_path_list(self, contract: str, dependencies: list) -> None:
        """Appends the contract dependencies on path list as a tuple

        :param contract: contract name
        :param dependencies: its dependencies list
        :return: None
        """
        for dependency in dependencies:
            cur_file_path = path.join(self._contracts_path, dependency)
            new_file_path = path.join(contract, dependency)
            path_tuple = (cur_file_path, new_file_path)
            self.contract.path_list.append(path_tuple)

