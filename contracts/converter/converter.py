from iconservice import *

from contracts.interfaces.abc_converter import ABCConverter
from contracts.interfaces.abc_formula import ABCFormula
from contracts.interfaces.abc_irc_token import ABCIRCToken
from contracts.interfaces.abc_score_registry import ABCScoreRegistry
from contracts.interfaces.abc_smart_token import ABCSmartToken
from contracts.utility.managed import Managed
from contracts.utility.proxy_score import ProxyScore
from contracts.utility.smart_token_controller import SmartTokenController
from ..utility.utils import Utils

TAG = 'Converter'
TRANSFER_DATA = b'conversionResult'
CONNECTOR_DB_PREFIX = b'\x03'

# interface SCOREs
SmartToken = ProxyScore(ABCSmartToken)
ScoreRegistry = ProxyScore(ABCScoreRegistry)
IRCToken = ProxyScore(ABCIRCToken)
Formula = ProxyScore(ABCFormula)


class Connector:
    """
    Wrapper class that contains DBs of connector information
    """

    def __init__(self, db: IconScoreDatabase):
        # connector virtual balance
        self.virtual_balance = VarDB('virtual_balance', db, int)
        # connector weight, represented in ppm, 1-1000000
        self.weight = VarDB('weight', db, int)
        # true if virtual balance is enabled, false if not
        self.is_virtual_balance_enabled = VarDB('is_virtual_balance_enabled', db, bool)
        # is purchase of the smart token enabled with the connector, can be set by the owner
        self.is_purchase_enabled = VarDB('is_purchase_enabled', db, bool)
        # used to tell if the mapping element is defined
        self.is_set = VarDB('is_set', db, bool)


class ConnectorDict:
    """
    Dict container Address-Connector pair
    """

    def __init__(self, db: IconScoreDatabase):
        self._db = db
        self._items = {}

    def __getitem__(self, key: Address) -> Connector:
        if key not in self._items:
            sub_db = self._db.get_sub_db(b'|'.join([CONNECTOR_DB_PREFIX, key.to_bytes()]))
            self._items[key] = Connector(sub_db)

        return self._items[key]

    def __setitem__(self, key, value):
        revert('illegal access')


# noinspection PyPep8Naming,PyMethodOverriding
class Converter(ABCConverter, SmartTokenController, Managed):
    """
    Converter

    The token converter, allows conversion between a smart token and other IRC2 tokens and between
    different IRC2 tokens and themselves.

    IRC2 connector balance can be virtual, meaning that the calculations are based on the virtual
    balance instead of relying on the actual connector balance. This is a security mechanism that
    prevents the need to keep a very large (and valuable) balance in a single contract.

    The converter is upgradable (just like any SmartTokenController).

    WARNING: It is NOT RECOMMENDED to use the converter with Smart Tokens that have less than
    8 decimal digits or with very small numbers because of precision loss
    """

    _REVISION = 0
    _MAX_WEIGHT = 1000000
    _MAX_CONVERSION_FEE = 1000000

    # triggered when a conversion between two tokens occurs
    @eventlog(indexed=3)
    def Conversion(self,
                   _fromToken: Address,
                   _toToken: Address,
                   _trader: Address,
                   _amount: int,
                   _return: int,
                   _conversionFee: int):
        pass

    # triggered after a conversion with new price data
    @eventlog(indexed=1)
    def PriceDataUpdate(self,
                        _connectorToken: Address,
                        _tokenSupply: int,
                        _connectorBalance: int,
                        _connectorWeight: int):
        pass

    # triggered when the conversion fee is updated
    @eventlog
    def ConversionFeeUpdate(self, _prevFee: int, _newFee: int):
        pass

    # triggered when conversions are enabled/disabled
    @eventlog
    def ConversionsEnable(self, _conversionsEnabled: bool):
        pass

    # verifies that the address belongs to one of the connector tokens
    def _require_valid_connector(self, address: Address):
        Utils.require(self._connectors[address].is_set.get())

    # verifies that the address belongs to one of the convertible tokens
    def _require_valid_token(self, address: Address):
        Utils.require(address == self.token.get() or self._connectors[address].is_set.get())

    # verifies maximum conversion fee
    def _require_valid_max_conversion_fee(self, conversion_fee: int):
        Utils.require(0 <= conversion_fee <= self._MAX_CONVERSION_FEE)

    # verifies conversion fee
    def _require_valid_conversion_fee(self, conversion_fee: int):
        Utils.require(0 <= conversion_fee <= self._max_conversion_fee.get())

    # verifies connector weight range
    def _require_valid_connector_weight(self, weight: int):
        Utils.require(0 < weight <= self._MAX_WEIGHT)

    # verifies the total weight is 100%
    def _require_max_total_weight_only(self):
        Utils.require(self._total_connector_weight.get() == self._MAX_WEIGHT)

    # verifies conversions aren't disabled
    def _require_conversions_allowed(self):
        Utils.require(self._conversions_enabled.get())

    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)
        # allows the owner to prevent/allow the registry to be updated
        self._allow_registry_update = VarDB('allow_registry_update', db, bool)
        # address of previous registry as security mechanism
        self._prev_registry = VarDB('prev_registry', db, Address)
        # contract registry contract
        self._registry = VarDB('registry', db, Address)
        # IRC standard token addresses
        self._connector_tokens = ArrayDB('connector_tokens', db, Address)
        # used to efficiently prevent increasing the total connector weight above 100%
        self._total_connector_weight = VarDB('total_connector_weight', db, int)
        # maximum conversion fee for the lifetime of the contract,
        # represented in ppm, 0...1000000 (0 = no fee, 100 = 0.01%, 1000000 = 100%)
        self._max_conversion_fee = VarDB('max_conversion_fee', db, int)
        # current conversion fee, represented in ppm, 0...maxConversionFee
        self._conversion_fee = VarDB('conversion_fee', db, int)
        # true if token conversions is enabled, false if not
        self._conversions_enabled = VarDB('conversions_enabled', db, bool)
        # connector token addresses -> connector data
        self._connectors = ConnectorDict(db)

    def on_install(self,
                   _token: Address,
                   _registry: Address,
                   _maxConversionFee: int,
                   _connectorToken: Address,
                   _connectorWeight: int):
        """
        invoked when install

        :param _token: smart token governed by the converter
        :param _registry: address of a contract registry contract
        :param _maxConversionFee: maximum conversion fee, represented in ppm
        :param _connectorToken: optional,
                    initial connector, allows defining the first connector at deployment time
        :param _connectorWeight: optional, weight for the initial connector
        """
        Utils.check_valid_address(_registry)
        self._require_valid_max_conversion_fee(_maxConversionFee)
        SmartTokenController.on_install(self, _token)
        self._registry.set(_registry)
        self._prev_registry.set(_registry)

        self._max_conversion_fee.set(_maxConversionFee)
        if Utils.is_valid_address(_connectorToken):
            self.addConnector(_connectorToken, _connectorWeight, False)

    def on_update(self) -> None:
        SmartTokenController.on_update(self)

    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        """
        invoked when the contract receives tokens.
        if the data param is parsed as conversion format,
        token conversion is executed.
        conversion format is:
        ```
        {
            'toToken': [STR_ADDRESS],
            'minReturn': [INT]
        }
        ```

        :param _from: token sender. should be network
        :param _value: amount of tokens
        :param _data: additional data
        """
        Utils.check_positive_value(_value)
        from_token = self.msg.sender

        if (_from == self.getOwner() or _from == self.getManager) \
                and self._connectors[from_token].is_set.get() \
                and not self.is_active():
            # If the token sender is the owner and sent token is a connector token, receives tokens
            # Otherwise tries to parse whether the data is conversion request
            pass
        else:
            # verifies whether the token sender is the network
            registry = self.create_interface_score(self._registry.get(), ScoreRegistry)
            network = registry.getAddress(ScoreRegistry.BANCOR_NETWORK)
            Utils.require(_from == network)

            # noinspection PyBroadException
            try:
                conversion_params = json_loads(_data.decode("utf-8"))
                to_token = Address.from_string(conversion_params['toToken'])
                min_return = conversion_params['minReturn']
                return self._convert(_from, from_token, to_token, _value, min_return)
            except Exception as e:
                revert(str(e))

    def _convert(self,
                 trader: Address,
                 from_token: Address,
                 to_token: Address,
                 amount: int,
                 min_return: int) -> int:
        """
        converts a specific amount of _fromToken to _toToken

        :param trader: convert requester. must be Network
        :param from_token: IRC2 token to convert from
        :param to_token: IRC2 token to convert to
        :param amount: amount to convert, in fromToken
        :param min_return: if the conversion results in an amount smaller than the minimum return
            - it is cancelled, must be nonzero
        :return: conversion return amount
        """
        self._require_conversions_allowed()
        Utils.check_positive_value(min_return)
        Utils.require(from_token != to_token)

        smart_token = self.token.get()
        # conversion between the token and one of its connectors
        if to_token == smart_token:
            return self._buy(trader, from_token, amount, min_return)
        elif from_token == smart_token:
            return self._sell(trader, to_token, amount, min_return)

        # conversion between 2 connectors
        return self._convert_cross_connector(trader, from_token, to_token, amount, min_return)

    def _buy(self, trader: Address, connector_token: Address, amount: int, min_return: int) -> int:
        """
        buys the token by depositing one of its connector tokens

        :param trader: convert requester. must be Network
        :param connector_token: connector token contract address
        :param amount: amount to deposit (in the connector token)
        :param min_return: if the conversion results in an amount smaller than the minimum return
            - it is cancelled, must be nonzero
        :return: buy return amount
        """
        returns = self.getPurchaseReturn(connector_token, amount)
        return_amount = returns['amount']
        fee_amount = returns['fee']
        # ensure the trade gives something in return and meets the minimum requested amount
        Utils.require(return_amount >= min_return)

        # update virtual balance if relevant
        connector = self._connectors[connector_token]
        if connector.is_virtual_balance_enabled.get():
            connector.virtual_balance.set(connector.virtual_balance.get() + return_amount)

        smart_token_address = self.token.get()
        smart_token = self.create_interface_score(smart_token_address, SmartToken)

        # issue new funds to the caller in the smart token
        smart_token.issue(trader, return_amount)

        # dispatch the conversion event
        self.Conversion(
            connector_token, smart_token_address, trader, amount, return_amount, fee_amount)

        # dispatch price data update for the smart token/connector
        self.PriceDataUpdate(connector_token,
                             smart_token.totalSupply(),
                             self.getConnectorBalance(connector_token),
                             connector.weight.get())

        return return_amount

    def _sell(self, trader: Address, connector_token: Address, amount: int, min_return: int) -> int:
        """
        sells the token by withdrawing from one of its connector tokens

        :param trader: convert requester. must be Network
        :param connector_token: connector token contract address
        :param amount: amount to sell (in the smart token)
        :param min_return: if the conversion results in an amount smaller the minimum return
            - it is cancelled, must be nonzero
        :return: sell return amount
        """
        returns = self.getSaleReturn(connector_token, amount)
        return_amount = returns['amount']
        fee_amount = returns['fee']
        # ensure the trade gives something in return and meets the minimum requested amount
        Utils.require(return_amount >= min_return)

        smart_token_address = self.token.get()
        smart_token = self.create_interface_score(smart_token_address, SmartToken)

        # ensure that the trade will only deplete the connector balance if the total supply is
        # depleted as well
        token_supply = smart_token.totalSupply()
        connector_balance = self.getConnectorBalance(connector_token)
        Utils.require(return_amount < connector_balance or
                      (return_amount == connector_balance and amount == token_supply))

        # update virtual balance if relevant
        connector = self._connectors[connector_token]
        if connector.is_virtual_balance_enabled.get():
            connector.virtual_balance.set(connector.virtual_balance.get() - return_amount)

        # destroy _sellAmount from the caller's balance in the smart token
        smart_token.destroy(self.address, amount)

        # transfer funds to the caller in the connector token
        # the transfer might fail if the actual connector balance is smaller than
        # the virtual balance
        irc_token = self.create_interface_score(connector_token, IRCToken)
        irc_token.transfer(trader, return_amount, TRANSFER_DATA)

        # dispatch the conversion event
        self.Conversion(
            smart_token_address, connector_token, trader, amount, return_amount, fee_amount)

        # dispatch price data update for the smart token/connector
        self.PriceDataUpdate(connector_token,
                             smart_token.totalSupply(),
                             self.getConnectorBalance(connector_token),
                             connector.weight.get())

        return return_amount

    def _convert_cross_connector(self,
                                 trader: Address,
                                 from_token: Address,
                                 to_token: Address,
                                 amount: int,
                                 min_return: int):
        """
        Converts between 2 connectors

        :param trader: convert requester. must be Network
        :param from_token: IRC2 token to convert from
        :param to_token: IRC2 token to convert to
        :param amount: amount to deposit (in the connector token)
        :param min_return: if the conversion results in an amount smaller than the minimum return
            - it is cancelled, must be nonzero
        :return: return amount
        """
        returns = self.getCrossConnectorReturn(from_token, to_token, amount)
        return_amount = returns['amount']
        fee_amount = returns['fee']
        # ensure the trade gives something in return and meets the minimum requested amount
        Utils.require(return_amount >= min_return)
        # update the source token virtual balance if relevant
        from_connector = self._connectors[from_token]
        if from_connector.is_virtual_balance_enabled.get():
            from_connector.virtual_balance.set(from_connector.virtual_balance.get() + return_amount)
        # update the target token virtual balance if relevant
        to_connector = self._connectors[to_token]
        if to_connector.is_virtual_balance_enabled.get():
            to_connector.virtual_balance.set(to_connector.virtual_balance.get() + return_amount)
        # ensure that the trade won't deplete the connector balance
        to_connector_balance = self.getConnectorBalance(to_token)
        Utils.require(return_amount < to_connector_balance)
        # transfer funds to the caller in the to connector token
        # the transfer might fail if the actual connector balance is smaller than
        # the virtual balance
        irc_token = self.create_interface_score(to_token, IRCToken)
        irc_token.transfer(trader, return_amount, TRANSFER_DATA)
        # dispatch the conversion event
        # the fee is higher (magnitude = 2) since cross connector conversion equals 2 conversions
        # (from / to the smart token)
        self.Conversion(from_token, to_token, trader, amount, return_amount, fee_amount)
        # dispatch price data updates for the smart token / both connectors
        smart_token = self.create_interface_score(self.token.get(), SmartToken)
        token_supply = smart_token.totalSupply()
        self.PriceDataUpdate(from_token, token_supply, self.getConnectorBalance(from_token),
                             from_connector.weight.get())
        self.PriceDataUpdate(to_token, token_supply, self.getConnectorBalance(to_token),
                             to_connector.weight.get())
        return return_amount

    @external
    def addConnector(self, _token: Address, _weight: int, _enableVirtualBalance: bool):
        """
        defines a new connector for the token
        can only be called by the owner while the converter is inactive

        :param _token: address of the connector token
        :param _weight: constant connector weight, represented in ppm, 1-1000000
        :param _enableVirtualBalance: true to enable virtual balance for the connector,
            false to disable it
        """
        self.owner_only()
        self.require_inactive()
        Utils.check_valid_address(_token)
        Utils.check_not_this(self.address, _token)
        self._require_valid_connector_weight(_weight)

        Utils.require(self.token.get() != _token and
                      not self._connectors[_token].is_set.get() and
                      self._total_connector_weight.get() + _weight <= self._MAX_WEIGHT)

        self._connectors[_token].virtual_balance.set(0)
        self._connectors[_token].weight.set(_weight)
        self._connectors[_token].is_virtual_balance_enabled.set(_enableVirtualBalance)
        self._connectors[_token].is_purchase_enabled.set(True)
        self._connectors[_token].is_set.set(True)
        self._connector_tokens.put(_token)

        self._total_connector_weight.set(self._total_connector_weight.get() + _weight)

    @external
    def updateRegistry(self):
        """
        sets the contract registry to whichever address the current registry is pointing to
        """

        # require that upgrading is allowed or that the caller is the owner
        Utils.require(self._allow_registry_update.get() or self.msg.sender == self.address)

        # get the address of whichever registry the current registry is pointing to
        registry = self.create_interface_score(self._registry.get(), ScoreRegistry)
        new_registry = registry.getAddress(ScoreRegistry.SCORE_REGISTRY)

        # if the new registry hasn't changed or is the zero address, revert
        Utils.check_valid_address(new_registry)
        Utils.require(new_registry != self._registry.get())

        # set the previous registry as current registry and current registry as newRegistry
        self._prev_registry.set(self._registry.get())
        self._registry.set(new_registry)

    @external
    def restoreRegistry(self):
        """
        security mechanism allowing the converter owner to revert to the previous registry,
        to be used in emergency scenario
        """
        self.require_owner_or_manager_only()

        # set the registry as previous registry
        self._registry.set(self._prev_registry.get())

        # after a previous registry is restored, only the owner can allow future updates
        self._allow_registry_update.set(False)

    @external
    def disableRegistryUpdate(self, _disable: bool):
        """
        disables the registry update functionality
        this is a safety mechanism in case of a emergency
        can only be called by the manager or owner

        :param _disable: true to disable registry updates, false to re-enable them
        """

        self.require_owner_or_manager_only()
        self._allow_registry_update.set(not _disable)

    @external
    def disableConversions(self, _disable: bool):
        """
        disables the entire conversion functionality
        this is a safety mechanism in case of a emergency
        can only be called by the manager

        :param _disable: true to disable conversions, false to re-enable them
        """

        self.require_owner_or_manager_only()
        if self._conversions_enabled.get() == _disable:
            enable = not _disable
            self._conversions_enabled.set(enable)
            self.ConversionsEnable(enable)

    @external
    def setConversionFee(self, _conversionFee: int):
        """
        updates the current conversion fee
        can only be called by the manager

        :param _conversionFee: new conversion fee, represented in ppm
        :return:
        """
        self.require_owner_or_manager_only()
        self._require_valid_conversion_fee(_conversionFee)

        self.ConversionFeeUpdate(self._conversion_fee.get(), _conversionFee)
        self._conversion_fee.set(_conversionFee)

    @external
    def withdrawTokens(self, _token: Address, _to: Address, _amount: int):
        """
        withdraws tokens held by the converter and sends them to an account
        can only be called by the owner
        note that connector tokens can only be withdrawn by the owner while the converter is inactive

        :param _token: IRC2 token contract address
        :param _to: account to receive the new amount
        :param _amount: amount to withdraw
        """
        Utils.require(not self.is_active() or not self._connectors[_token].is_set.get())
        super().withdrawTokens(self, _token, _to, _amount)

    @external(readonly=True)
    def isAllowRegistryUpdate(self) -> bool:
        """
        returns if the registry update enabled

        :return: True if the registry can be updated
        """
        return self._allow_registry_update.get()

    @external(readonly=True)
    def getPreviousRegistry(self) -> Address:
        """
        gets the previous registry address

        :return: previous registry address
        """
        return self._prev_registry.get()

    @external(readonly=True)
    def getRegistry(self) -> Address:
        """
        gets the registry address

        :return: registry address
        """
        return self._registry.get()

    @external(readonly=True)
    def getConnectorTokenCount(self) -> int:
        """
        returns the number of connector tokens defined

        :return: number of connector tokens
        """
        return len(self._connector_tokens)

    @external(readonly=True)
    def getMaxConversionFee(self) -> int:
        """
        Returns maximum conversion fee

        :return: maximum conversion fee
        """

        return self._max_conversion_fee.get()

    @external(readonly=True)
    def getConversionFee(self) -> int:
        """
        Returns current conversion fee, represented in ppm, 0...maxConversionFee

        :return: current conversion fee
        """

        return self._conversion_fee.get()

    @external(readonly=True)
    def isConversionsEnabled(self) -> bool:
        """
        Returns whether the conversion is enabled

        :return: True if the conversion is enabled
        """
        return self._conversions_enabled.get()

    @external(readonly=True)
    def getConnector(self, _address: Address) -> dict:
        """
        Returns connector information

        :param _address: connector token address
        :return: connector information, in dict
        """
        connector = self._connectors[_address]

        return {
            'virtualBalance': connector.virtual_balance.get(),
            'weight': connector.weight.get(),
            'isVirtualBalanceEnabled': connector.is_virtual_balance_enabled.get(),
            'isPurchaseEnabled': connector.is_purchase_enabled.get(),
            'isSet': connector.is_set.get(),
        } if connector.is_set.get() else {}

    @external(readonly=True)
    def getConnectorBalance(self, _connectorToken: Address) -> int:
        """
        Returns the connector's virtual balance if one is defined,
        otherwise returns the actual balance

        :param _connectorToken: connector token address
        :return: connector balance
        """
        self._require_valid_connector(_connectorToken)

        connector = self._connectors[_connectorToken]

        if connector.is_virtual_balance_enabled.get():
            return connector.virtual_balance.get()

        token = self.create_interface_score(_connectorToken, IRCToken)
        return token.balanceOf(self.address)

    @external(readonly=True)
    def getReturn(self, _fromToken: Address, _toToken: Address, _amount: int) -> dict:
        """
        Returns the expected return for converting a specific amount of _fromToken to _toToken

        :param _fromToken: address of IRC2 token to convert from
        :param _toToken: address of IRC2 token to convert to
        :param _amount: amount to convert, in fromToken
        :return: expected conversion return amount and conversion fee, in dict
        """
        Utils.require(_fromToken != _toToken)

        # conversion between the token and one of its connectors
        smart_token = self.token.get()
        if _toToken == smart_token:
            return self.getPurchaseReturn(_fromToken, _amount)
        elif _fromToken == smart_token:
            return self.getSaleReturn(_toToken, _amount)

        # conversion between 2 connectors
        return self.getCrossConnectorReturn(_fromToken, _toToken, _amount)

    @external(readonly=True)
    def getPurchaseReturn(self, _connectorToken: Address, _amount: int) -> dict:
        """
        returns the expected return for buying the token for a connector token

        :param _connectorToken: connector token contract address
        :param _amount: amount to deposit (in the connector token)
        :return: expected purchase return amount and conversion fee
        """
        self.require_active()
        self._require_valid_connector(_connectorToken)

        connector = self._connectors[_connectorToken]
        Utils.require(connector.is_purchase_enabled.get())

        smart_token = self.create_interface_score(self.token.get(), SmartToken)
        registry = self.create_interface_score(self._registry.get(), ScoreRegistry)
        formula_address = registry.getAddress(ScoreRegistry.BANCOR_FORMULA)
        formula = self.create_interface_score(formula_address, Formula)

        token_supply = smart_token.totalSupply()
        connector_balance = self.getConnectorBalance(_connectorToken)

        calculated_amount = formula.calculatePurchaseReturn(
            token_supply, connector_balance, connector.weight.get(), _amount)
        final_amount = self.getFinalAmount(calculated_amount, 1)
        return {'amount': final_amount, 'fee': (calculated_amount - final_amount)}

    @external(readonly=True)
    def getSaleReturn(self, _connectorToken: Address, _amount: int) -> dict:
        """
        returns the expected return for selling the token for one of its connector tokens

        :param _connectorToken: connector token contract address
        :param _amount: amount to sell (in the smart token)
        :return: expected sale return amount and conversion fee
        """
        self.require_active()
        self._require_valid_connector(_connectorToken)

        connector = self._connectors[_connectorToken]

        smart_token = self.create_interface_score(self.token.get(), SmartToken)
        registry = self.create_interface_score(self._registry.get(), ScoreRegistry)
        formula_address = registry.getAddress(ScoreRegistry.BANCOR_FORMULA)
        formula = self.create_interface_score(formula_address, Formula)

        token_supply = smart_token.totalSupply()
        connector_balance = self.getConnectorBalance(_connectorToken)

        calculated_amount = formula.calculateSaleReturn(
            token_supply, connector_balance, connector.weight.get(), _amount)

        final_amount = self.getFinalAmount(calculated_amount, 1)
        return {'amount': final_amount, 'fee': (calculated_amount - final_amount)}

    @external(readonly=True)
    def getCrossConnectorReturn(self,
                                _fromToken: Address, _toToken: Address, _amount: int) -> dict:
        """
        returns the expected return for selling one of the connector tokens for
        another connector token

        :param _fromToken: contract address of the connector token to convert from
        :param _toToken: contract address of the connector token to convert to
        :param _amount: amount to sell (in the from connector token)
        :return: expected sale return amount and conversion fee (in the to connector token)
        """
        self.require_active()
        self._require_valid_connector(_fromToken)
        self._require_valid_connector(_toToken)

        from_connector = self._connectors[_fromToken]
        to_connector = self._connectors[_toToken]
        Utils.require(to_connector.is_purchase_enabled.get())

        registry = self.create_interface_score(self._registry.get(), ScoreRegistry)
        formula_address = registry.getAddress(ScoreRegistry.BANCOR_FORMULA)
        formula = self.create_interface_score(formula_address, Formula)

        from_connector_balance = self.getConnectorBalance(_fromToken)
        to_connector_balance = self.getConnectorBalance(_toToken)

        calculated_amount = formula.calculateCrossConnectorReturn(from_connector_balance,
                                                                  from_connector.weight.get(),
                                                                  to_connector_balance,
                                                                  to_connector.weight.get(),
                                                                  _amount)

        final_amount = self.getFinalAmount(calculated_amount, 2)
        return {'amount': final_amount, 'fee': (calculated_amount - final_amount)}

    @external(readonly=True)
    def getFinalAmount(self, _amount: int, _magnitude: int) -> int:
        """
        given a return amount, returns the amount minus the conversion fee

        :param _amount: return amount
        :param _magnitude: 1 for standard conversion, 2 for cross connector conversion
        :return: amount minus conversion fee
        """
        final_ratio = (self._MAX_CONVERSION_FEE - self._conversion_fee.get())
        return _amount * final_ratio ** _magnitude // self._MAX_CONVERSION_FEE ** _magnitude
