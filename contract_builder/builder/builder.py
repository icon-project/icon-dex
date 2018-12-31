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

from contract_builder.builder.writer import Writer
from contract_builder.config import config


class Builder:

    def __init__(self, contracts_path: str, contracts: list=None):
        self.path_list = []
        self._contracts_path = contracts_path
        for c in contracts if contracts else config:
            self._append_contract_on_path_list(c)
            self._append_dependencies_on_path_list(c, config[c])

    def build(self, writer: Writer):
        writer.write(self.path_list)

    def _append_contract_on_path_list(self, contract: str):
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
                self.path_list.append(path_tuple)

    def _append_dependencies_on_path_list(self, contract:str, dependencies: list):
        for dependency in dependencies:
            cur_file_path = path.join(self._contracts_path, dependency)
            new_file_path = path.join(contract, dependency)
            path_tuple = (cur_file_path, new_file_path)
            self.path_list.append(path_tuple)

