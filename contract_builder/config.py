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

"""
It is configuration file about Dex SCOREs and their dependencies.
The config is the dictionary of which key is the main SCORE name
and value is the list of the paths of the dependencies.

In case of the key, although not writing on paths, all of its files will be imported later.

key: contract name
value: list of dependency file paths

TODO: If you want to use it, update it correctly by adding contract name and list of dependency file path.
"""

config = {
    "smart_token": [
        "irc_token/irc_token.py",
        "utility/token_holder.py",
        "interfaces/__init__.py",
        "interfaces/abc_irc_token.py",
        "interfaces/abc_owned.py",
        "interfaces/abc_smart_token.py",
        "interfaces/abc_token_holder.py"
    ],
    "irc_token": [
        "smart_token/smart_token.py",
        "utility/owned.py",
        "utility/proxy_score.py",
        "interfaces/abc_icx_token.py",
        "interfaces/abc_owned.py",
        "interfaces/abc_smart_token.py",
        "interfaces/abc_token_holder.py"
    ],
    "icx_token": [
        "smart_token/smart_token.py",
        "utility/owned.py",
        "utility/proxy_score.py",
        "utility/token_holder.py",
        "interfaces/abc_icx_token.py",
        "interfaces/abc_owned.py",
        "interfaces/abc_smart_token.py",
        "interfaces/abc_token_holder.py"
    ]
}
