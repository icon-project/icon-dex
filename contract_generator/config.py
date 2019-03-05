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

"""
It is configuration file about Dex SCOREs and their dependencies.
The config is the dictionary of which key is the main SCORE name
and value is the list of the paths of the dependencies.

In case of the key, although not writing on paths, all of its files will be imported later.

key: contract name
value: list of dependency file paths

"""

config = {
    "flexible_token": [
        "interfaces/__init__.py",
        "interfaces/abc_irc_token.py",
        "interfaces/abc_token_holder.py",
        "interfaces/abc_owned.py",
        "interfaces/abc_flexible_token.py",
        "irc_token/__init__.py",
        "irc_token/irc_token.py",
        "utility/__init__.py",
        "utility/owned.py",
        "utility/token_holder.py",
        "utility/utils.py",
        "utility/proxy_score.py",
        "NOTICE"
    ],
    "icx_token": [
        "interfaces/__init__.py",
        "interfaces/abc_icx_token.py",
        "interfaces/abc_irc_token.py",
        "interfaces/abc_token_holder.py",
        "interfaces/abc_owned.py",
        "irc_token/__init__.py",
        "irc_token/irc_token.py",
        "utility/__init__.py",
        "utility/owned.py",
        "utility/token_holder.py",
        "utility/utils.py",
        "utility/proxy_score.py",
        "NOTICE"
    ],
    "irc_token": [
        "interfaces/__init__.py",
        "interfaces/abc_irc_token.py",
    ],
    "score_registry": [
        "interfaces/__init__.py",
        "interfaces/abc_score_registry.py",
        "interfaces/abc_owned.py",
        "utility/__init__.py",
        "utility/owned.py",
        "utility/utils.py",
        "utility/proxy_score.py",
        "NOTICE"
    ],
    "network": [
        "interfaces/__init__.py",
        "interfaces/abc_flexible_token.py",
        "interfaces/abc_irc_token.py",
        "interfaces/abc_icx_token.py",
        "interfaces/abc_token_holder.py",
        "interfaces/abc_owned.py",
        "interfaces/abc_converter.py",
        "utility/__init__.py",
        "utility/owned.py",
        "utility/token_holder.py",
        "utility/utils.py",
        "utility/proxy_score.py",
        "NOTICE"
    ],
    "converter": [
        "formula/__init__.py",
        "formula/fixed_map_formula.py",
        "interfaces/__init__.py",
        "interfaces/abc_formula.py",
        "interfaces/abc_converter.py",
        "interfaces/abc_irc_token.py",
        "interfaces/abc_score_registry.py",
        "interfaces/abc_flexible_token.py",
        "interfaces/abc_token_holder.py",
        "interfaces/abc_owned.py",
        "utility/__init__.py",
        "utility/managed.py",
        "utility/owned.py",
        "utility/utils.py",
        "utility/proxy_score.py",
        "utility/flexible_token_controller.py",
        "utility/token_holder.py",
        "NOTICE"
    ]
}
