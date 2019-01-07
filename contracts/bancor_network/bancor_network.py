from iconservice import *
from ..interfaces.abc_bancor_network import ABCBancorNetwork
from ..interfaces.abc_score_registry import ABCScoreRegistry
from ..interfaces.abc_converter import ABCConverter
from ..interfaces.abc_icx_token import ABCIcxToken
from ..interfaces.abc_smart_token import ABCSmartToken
from ..interfaces.abc_irc_token import ABCIRCToken
from ..utility.proxy_score import ProxyScore
from ..utility.utils import Utils
from ..utility.token_holder import TokenHolder

TAG = 'BancorNetwork'

# todo: implement event log
# todo: implement getExpectedReturnByPath
# todo: implement registry related method
# todo: implement convertForMultiple
# todo: implement unit test and integration test


class BancorNetwork(IconScoreBase, TokenHolder, ABCBancorNetwork):
    _MAX_CONVERSION_FEE = 1000000
    _MAX_CONVERSION_COUNT = 10

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._icx_tokens = DictDB('icx_tokens', db, value_type=bool)
        self._registry_address = VarDB('registry_address', db, value_type=Address)

    def on_install(self, _registryAddress: 'Address') -> None:
        TokenHolder.on_install(self)
        Utils.check_valid_address(_registryAddress)
        self._registry_address.set(_registryAddress)

    def on_update(self) -> None:
        TokenHolder.on_update(self)

    @external(readonly=True)
    def getExpectedReturnByPath(self, path: str, _amount: int) -> int:
        pass

    @external
    def setRegistry(self, _registryAddress: 'Address'):
        # only owner can register registry
        # check valid address
        # check not this

        # consider emitting event log
        pass

    @external
    def registerIcxToken(self, _icxToken: 'Address', _register: bool):
        # only owner can register Icx token
        # check valid address
        # check not this
        self._icx_tokens[_icxToken] = _register
        # consider emitting event log

    def _check_valid_path(self, path: list):
        # check the path data
        path_len = len(path)
        if not 2 < path_len <= self._MAX_CONVERSION_COUNT * 2 + 1 or not path_len % 2 == 1:
            revert("invalid path")

    @external
    @payable
    def convert(self, _path: str, _minReturn: int):
        return self.convertFor(_path, self.msg.value, _minReturn, self.msg.sender)

    @external
    @payable
    def convertFor(self, _path: str, _minReturn: int, _for: 'Address'):
        path = _path.replace(" ", "").split(",")
        converted_path = [Address.from_string(address) for address in path]
        self._check_valid_path(converted_path)
        Utils.check_positive_value(_minReturn)
        icx_amount = self.msg.value

        icx_token = _path[0]
        if not self._icx_tokens[icx_token]:
            revert("wrong path, first address should be icx token")

        self.icx.transfer(icx_token, icx_amount)

        return self._convert_for_internal(converted_path, icx_amount, _minReturn, _for)

    @external
    @payable
    def convertForMultiple(self, _path: str, _amount: str, _minReturn: str, _for: 'Address'):
        # todo: check the _path data
        # todo: check the _amount

        # todo: consider to using this method only when 'from' is Icx or not
        pass

    def _convert_for_internal(self, path: list, amount: int, min_return: int, _for: 'Address'):
        # todo: verify sign address should be placed on this method
        (to_token, amount) = self._convert_by_path(path, amount, min_return, _for)

        if self._icx_tokens[to_token]:
            icx_token = self.create_interface_score(to_token, ProxyScore(ABCIcxToken))
            icx_token.withdrawTo(amount, _for)
        else:
            token = self.create_interface_score(to_token, ProxyScore(ABCIRCToken))
            token.transfer(_for, amount, b'None')

        return amount

    def _convert_by_path(self, path: list, amount: int, min_return: int, _for: 'Address'):
        # define from and to token address
        from_token_address = path[0]
        to_token_address = ZERO_SCORE_ADDRESS
        from_token = self.create_interface_score(from_token_address, ProxyScore(ABCIRCToken))

        data = {}
        for i in range(1, len(path), 2):
            smart_token_address = path[i]
            to_token_address = path[i+1]

            # todo: implement 'check whitelist'

            smart_token = self.create_interface_score(smart_token_address, ProxyScore(ABCSmartToken))
            to_token = self.create_interface_score(to_token_address, ProxyScore(ABCIRCToken))
            converter_address = smart_token.getOwner()
            amount_before_converting = to_token.balanceOf(self.address)
            data["to_token"] = str(to_token_address)
            data["min_return"] = min_return if i == len(path)-2 else 1
            encoded_data = json_dumps(data).encode()

            from_token.transfer(converter_address, amount, encoded_data)

            amount_after_converting = to_token.balanceOf(self.address)
            amount = amount_after_converting - amount_before_converting

            data = {}
            from_token = to_token
        return to_token_address, amount

    def check_and_convert_data(self, data: bytes, from_address: 'Address'):
        try:
            dict_data = json_loads(data.decode())
        except ValueError as e:
            revert(f"json format error: {e}")

        if "min_return" not in dict_data:
            revert()
        if "path" not in dict_data:
            revert()

        if "for" not in dict_data.keys() or dict_data["for"] is None:
            dict_data["for"] = from_address
        else:
            dict_data["for"] = Address.from_string(dict_data["for"])
        return dict_data

    def tokenFallback(self, _from: 'Address', _value: int, _data: bytes):
        if _data == b'None' or _data is None:
            return

        dict_data = self.check_and_convert_data(_data, _from)
        Utils.check_positive_value(dict_data["min_return"])
        Utils.check_valid_address(dict_data["for"])

        path = dict_data["path"].replace(" ", "").split(",")
        converted_path = [Address.from_string(address) for address in path]
        self._check_valid_path(converted_path)

        self._convert_for_internal(converted_path, _value, dict_data["min_return"], dict_data["for"])
