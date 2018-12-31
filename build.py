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

from argparse import ArgumentParser
from os import path

from contract_generator.builder import Builder
from contract_generator.writer import FileWriter

CURRENT_PATH = path.dirname(__file__)
CONTRACTS_DIR = 'contracts'
OUTPUT_ROOT_DIR = 'build'


def parse_args() -> 'parser':
    """Gets arguments from CLI and parse the arguments.

    :return parser arguments: parser object's arguments
    """
    parser = ArgumentParser(usage='''

    ============================================================================
    CLI for building DEX contracts to the file system
    ============================================================================
        
        Commands:
            <whitespace-delimited lists of contracts>
            clean 
            
        IF YOU DO NOT INSERT ANY WHITESPACE-DELIMITED LISTS OF CONTRACTS, 
        RANGE OF TARGET CONTRACT IS ALL.
        ''')

    parser.add_argument('command', nargs='*', default="")
    return parser.parse_args()


def clean_build_dir(file_writer: FileWriter) -> None:
    """Cleans output root directory; build

    :param file_writer: FileWrite instance
    :return: None
    """
    if file_writer.clean():
        print("Removed build directory successfully")
    else:
        print("No exist build directory")


def write_contracts_to_file_system(file_writer: FileWriter, contracts: list) -> None:
    """Writes all of the files on path list to the file system

    :param file_writer: FileWrite instance
    :param contracts: list of contracts
    :return: None
    """
    try:
        builder = Builder(path.join(CURRENT_PATH, CONTRACTS_DIR), contracts)
        builder.build(file_writer)
        print("Built {0} contract successfully".format(contracts if contracts else "all"))
    except KeyError as e:
        print('Wrong contract name:', e)


def main():
    """Main procedure"""
    command = parse_args().command
    output_root_path = path.join(CURRENT_PATH, OUTPUT_ROOT_DIR)
    file_writer = FileWriter(output_root_path)

    if command and command[0] == "clean":
        clean_build_dir(file_writer)
        return

    write_contracts_to_file_system(file_writer, command)


if __name__ == '__main__':
    main()
