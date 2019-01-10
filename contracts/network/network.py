from iconservice import *
from ..interfaces.abc_network import ABCNetwork
from ..interfaces.abc_converter import ABCConverter
from ..interfaces.abc_icx_token import ABCIcxToken
from ..interfaces.abc_smart_token import ABCSmartToken
from ..interfaces.abc_irc_token import ABCIRCToken
from ..utility.proxy_score import ProxyScore
from ..utility.utils import Utils
from ..utility.token_holder import TokenHolder

TAG = 'Network'

# todo: implement unit test and integration test
# todo: implement convertForMultiple ( decided not to implement this method)


class Network(IconScoreBase, TokenHolder, ABCNetwork):
    _MAX_CONVERSION_FEE = 1000000
    _MAX_CONVERSION_COUNT = 10

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._icx_tokens = DictDB('icx_tokens', db, value_type=bool)

    def on_install(self) -> None:
        TokenHolder.on_install(self)

    def on_update(self) -> None:
        TokenHolder.on_update(self)

    @external(readonly=True)
    def getExpectedReturnByPath(self, _path: str, _amount: int) -> int:
        path = _path.replace(" ", "").split(",")
        converted_path = [Address.from_string(address) for address in path]
        self._check_valid_path(converted_path)
        Utils.check_positive_value(_amount)

        amount = _amount
        from_token = converted_path[0]
        for i in range(1, len(converted_path), 2):
            smart_token = converted_path[i]
            to_token = converted_path[i + 1]
            converter = self.create_interface_score(smart_token, ProxyScore(ABCConverter))
            (amount, _) = converter.getReturn(from_token, to_token, amount).values()
            from_token = to_token

        return amount

    @external(readonly=True)
    def getIcxTokenRegistered(self, _icxToken: 'Address') -> bool:
        return self._icx_tokens[_icxToken]

    @external
    def registerIcxToken(self, _icxToken: 'Address', _register: bool):
        self.owner_only()
        Utils.check_valid_address(_icxToken)
        Utils.check_not_this(self.address, _icxToken)

        self._icx_tokens[_icxToken] = _register

    def _check_valid_path(self, path: list):
        path_set = {address for i, address in enumerate(path) if i % 2 == 1}
        if len(path_set) != len(path) // 2:
            revert("do not support circular path")

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
            revert("wrong path, first address must be icx token")

        # transfer ICX coin to IcxToken SCORE. network will get same amount of icx token instead
        self.icx.transfer(icx_token, icx_amount)

        return self._convert_for_internal(converted_path, icx_amount, _minReturn, _for)

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

            smart_token = self.create_interface_score(smart_token_address, ProxyScore(ABCSmartToken))
            to_token = self.create_interface_score(to_token_address, ProxyScore(ABCIRCToken))
            converter_address = smart_token.getOwner()

            amount_before_converting = to_token.balanceOf(self.address)
            data["toToken"] = str(to_token_address)
            data["minReturn"] = min_return if i == len(path)-2 else 1
            encoded_data = json_dumps(data).encode()

            from_token.transfer(converter_address, amount, encoded_data)

            amount_after_converting = to_token.balanceOf(self.address)
            amount = amount_after_converting - amount_before_converting
            from_token = to_token

        return to_token_address, amount

    @staticmethod
    def check_and_convert_bytes_data(data: bytes, from_address: 'Address'):
        try:
            dict_data = json_loads(data.decode())
        except ValueError as e:
            revert(f"json format error: {e}")

        # todo: need to refactoring
        if "min_return" not in dict_data:
            revert("")
        if "path" not in dict_data:
            revert("")

        path = dict_data["path"].replace(" ", "").split(",")
        dict_data["path"] = [Address.from_string(address) for address in path]

        if "for" not in dict_data.keys() or dict_data["for"] is None:
            dict_data["for"] = from_address
        else:
            dict_data["for"] = Address.from_string(dict_data["for"])
        return dict_data

    def tokenFallback(self, _from: 'Address', _value: int, _data: bytes):
        # if _data is None, this regard as normal token transfer
        if _data == b'None' or _data is None:
            return

        dict_data = self.check_and_convert_bytes_data(_data, _from)
        # check the value of dict_data
        Utils.check_positive_value(dict_data["minReturn"])
        Utils.check_valid_address(dict_data["for"])
        self._check_valid_path(dict_data["path"])

        self._convert_for_internal(dict_data["path"], _value, dict_data["minReturn"], dict_data["for"])
