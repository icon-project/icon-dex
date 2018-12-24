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
import sys

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(CUR_DIR, '..')))
if ROOT_DIR not in sys.path:
    # add parent dir to paths
    sys.path.append(ROOT_DIR)

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
            
        IF YOU DO NOT INSERT ANY WHITESPACE-DELIMITED LISTS OF CONTRACTS, 
        RANGE OF TARGET CONTRACT IS ALL.
        ''')

    parser.add_argument('contracts', nargs='*', default="")
    return parser.parse_args()


def main():
    """Main procedure"""
    contracts = parse_args().contracts
    in_memory_zip = InMemoryZip()

    try:
        # builds the in-memory zip of target contacts and returns it as bytes
        in_memory_zip.build(contracts)
        # extracts all files in memory below given path;
        in_memory_zip.extract()
    except KeyError as e:
        print('Wrong contract name:', e)


if __name__ == '__main__':
    main()


