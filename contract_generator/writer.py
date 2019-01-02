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

from io import BytesIO
from os import path, makedirs
from abc import ABCMeta, abstractmethod
from shutil import rmtree, copy
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED, ZIP_BZIP2, ZIP_LZMA


class Writer(metaclass=ABCMeta):
    """Interface Writer"""

    @abstractmethod
    def write(self, path_list: list):
        pass


class FileWriter(Writer):

    def __init__(self, output_root_dir: str) -> None:
        """Initializes FileWriter with setting output root dir

        :param output_root_dir: the output root directory where contracts are set
        :return: None
        """
        self.output_root_dir = output_root_dir

    def write(self, contract_list: list) -> None:
        """Writes all of the files on path list to the file system

        :param contract_list: contracts list composed of contracts in namedtuple
                    - contract.name is contract name
                    - contract.path_list is contracts path list in tuples
                        ex. [(current_file_path, new_file_path), (..), ..]
        :return: None
        """
        for contract in contract_list:
            contract_path = path.join(self.output_root_dir, contract.name)
            if path.isdir(contract_path):
                rmtree(contract_path)
            for path_tuple in contract.path_list:
                cur_file_path = path_tuple[0]
                new_file_path = path.join(self.output_root_dir, path_tuple[1])
                makedirs(path.dirname(new_file_path), exist_ok=True)
                copy(cur_file_path, new_file_path)

    def clean(self) -> bool:
        """Cleans output root directory

        :return bool: True for success on cleaning it and False for fail
        """
        if path.isdir(self.output_root_dir):
            rmtree(self.output_root_dir)
            return True
        else:
            return False


class ZipWriter(Writer):

    @staticmethod
    def _convert_compression(compression_as_str):
        """Converts compression as string into compression as int with zipfile module"""
        if compression_as_str == 'ZIP_STORED':
            return ZIP_STORED
        elif compression_as_str == 'ZIP_DEFLATED':
            return ZIP_DEFLATED
        elif compression_as_str == 'ZIP_BZIP2':
            return ZIP_BZIP2
        elif compression_as_str == 'ZIP_LZMA':
            return ZIP_LZMA
        else:
            raise ValueError("{0} is wrong compression type".format(compression_as_str))

    def __init__(self, compression: str = 'ZIP_STORED'):
        """Initializes ZipWriter with setting compression type which default is ZIP_STORED

        :param compression: ZIP compression
        """
        self.in_memory = BytesIO()
        self.zf = ZipFile(self.in_memory, mode="w", compression=self._convert_compression(compression))

    def write(self, contract_list: list) -> None:
        """
        Builds the target contracts in the memory zip with the list of contracts.
        If it is empty, the target should be all of the contracts in config.
        Returns bytes of the in-memory file

        :param contract_list: contracts list having contract namedtuple
        :return: bytes of the memory file
        """
        try:
            for contract in contract_list:
                for path_tuple in contract.path_list:
                    cur_file_path = path_tuple[0]
                    new_file_path = path_tuple[1]
                    self.zf.write(cur_file_path, new_file_path)
        finally:
            self.zf.close()

    def to_bytes(self) -> bytes:
        """Retrieves the whole file as buffer

        :return: bytes of the in-memory file
        """
        self.in_memory.seek(0)
        return self.in_memory.read()

    def store_to_file(self, output_root_dir: str) -> None:
        """
        Extracts all files in memory below given path;
        the underlying zip file module is clever enough to create the necessary path if not existing.

        :param output_root_dir: the output root directory where contracts are set
        :return: None
        """
        with ZipFile(self.in_memory, mode="r") as z:
            if path.isdir(output_root_dir):
                rmtree(output_root_dir)
            z.extractall(output_root_dir)

    def list_content(self) -> list:
        """Returns a list of class ZipInfo instances for files in the archive

        :return: the list of zip files entries
        """
        return self.zf.infolist()

