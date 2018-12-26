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

from os import path
from shutil import rmtree
from argparse import ArgumentParser

from contract_builder.builder.builder_in_memory_zip import InMemoryZip


def parse_args() -> 'parser':
    """Gets arguments from CLI and parse the arguments.

    :return parser arguments: parser object's arguments
    """
    parser = ArgumentParser(usage='''

    ============================================================================
    CLI for building DEX contracts on the file system
    ============================================================================
        
        Commands:
            <whitespace-delimited lists of contracts>
            clean 
            
        IF YOU DO NOT INSERT ANY WHITESPACE-DELIMITED LISTS OF CONTRACTS, 
        RANGE OF TARGET CONTRACT IS ALL.
        ''')

    parser.add_argument('command', nargs='*', default="")
    return parser.parse_args()


def clean_build_dir() -> None:
    """Cleans the build directory"""
    dir_build = 'contract_build'
    if path.isdir(dir_build):
        rmtree(dir_build)
        print("Removed build directory successfully")
    else:
        print("No exist build directory")


def main():
    """Main procedure"""
    command = parse_args().command

    if command and command[0] == "clean":
        clean_build_dir()
        return

    try:
        in_memory_zip = InMemoryZip()
        # builds the in-memory zip of target contacts and returns it as bytes
        in_memory_zip.build(command)
        # extracts all files in memory below given path;
        in_memory_zip.extract()
        print("Built {0} contract successfully".format(command if command else "all"))
    except KeyError as e:
        print('Wrong contract name:', e)


if __name__ == '__main__':
    main()
