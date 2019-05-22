# ICON DEX

ICON DEX is a decentralized liquidity exchange network on ICON Network that allows users to buy and sell tokens without matching buyers and sellers in an exchange. 

Through the use of multiple SCOREs in the network, Flexible Tokens can be created that hold one or more other tokens as connectors. By using a connector token model and algorithmically-calculated conversion rates, tokens are calculated their own prices and converted seamlessly. 

The main ones are the Flexible Token and Converter. The Converter is responsible for converting between a token and its connectors. Flexible Token represents a converter aware *IRC-2* compliant token.

This project refers to the Bancor Protocol™  [Whitepaper](https://www.bancor.network/whitepaper) for more information.

## Component 

### Flexible token

Flexible Tokens operate as regular tokens, in compliance with *IRC-2* token standard used on ICON Network, but include additional logic that allows users to always buy and sell them directly through their own SCOREs at prices that programmatically adjust to reflect supply and demand. For this, the main function of Flexible token is to increase or decrease the token supply. Then sends the new tokens to an account or removes tokens from an account to destroy them.  

#### issue

```python
@external
def issue(self, _to: Address, _amount: int) -> None:
```

Increases the token supply and sends the new tokens to an account can only be called by the contract owner.

##### Parameters

- _to : account to receive the new amount
- _amount : amount to increase the supply by

#### destroy

```python
@external
def destroy(self, _from: Address, _amount: int) -> None:
```

Removes tokens from an account and decreases the token supply can be called by the contract owner to destroy tokens from any account or by any holder to destroy tokens from his/her own account.

##### Parameters

- _from: account to remove the amount from
- _amount: amount to decrease the supply by

### Converter

Converter allows conversion between a flexible token and other *IRC-2* tokens and between different *IRC-2* tokens and themselves. 

Converter has properties to use on converting such as connector tokens and their information, conversion fee and total connector weight. And by using connectors information, it excutes token conversion. Conversion includes buying the token by depositing one of its connector tokens and selling the token by withdrawing from one of its connector tokens.  

When the Token Converter receives tokens, tokenFallback external method is called and if the data parameter is parsed as conversion format, token conversion is executed. Conversion format is as below. 

```
{
    'toToken': [STR_ADDRESS],
    'minReturn': [INT]
}
```

*IRC-2* connector balance can be virtual, meaning that the calculations are based on the virtual balance instead of relying on the actual connector balance. This is a security mechanism that prevents the need to keep a very large (and valuable) balance in a single contract.

### Network  

The network is the main entry point for token conversions to convert between any token (*ICX*, *IRC-2* and Flexible token) in the network to any other token in a single transaction by providing a conversion path.

The conversion path is a data structure represented by a single array. It is used when converting a token to another token in the network when the conversion cannot necessarily be done by a single converter and might require multiple 'hops'. The path defines which converters should be used and which conversion should be done in each step.

##### Conversion path format :

[source token, flexible token, to token, flexible token, to token...]

Max Length of Conversion path should be **21** as using different 10 conversions.

For example, the simplest path should be [source token, flexible token, to token]. The first element's of conversion path list is always the source token which is ICX token, *IRC-2* or Flexible token. And each 'hop' is represented by a 2-tuple flexible token and to token. 
The Flexible token in the 2-tuple ones is only used as a pointer to a converter rather than converter (since converter addresses are more likely to change).

## Main external methods

#### getExpectedReturnByPath

```python
@external(readonly=True)
def getExpectedReturnByPath(self, _path: str, _amount: int) -> int:
```

Returns the expected return amount for converting a specific amount by following a given conversion path. Notice that there is no support for circular paths.

##### Parameters

-  _path: conversion path, see conversion path format above
- _amount: amount to convert from (in the initial source token)

##### Return

expected conversion return amount and conversion fee

#### convert 

```python
@external
@payable
def convert(self, _path: str, _minReturn: int) -> int:
```

It converts the Icx token to any other token in the network by following a predefined conversion path and transfers the result tokens back to the sender. This method is used on converting from ICX token to IRC token.

Notes that the converter should already own the source tokens.

##### Params

- _path: conversion path as string which is comma-delimited lists , see conversion path format as below.

  Conversion path - 

  [source token, flexible token, to token, flexible token, to token...]

  **If the source token address of the path is not the icx token, raise error**.

- _minReturn: if the conversion results in an amount smaller than the minimum return - it is canceled, must be nonzero.

##### Return

tokens issued in return 

#### transfer

```python
@external
def transfer(self, _to: Address, _value: int, _data: bytes = None) -> None:
```

An account attempt to get the token. 

It is one of *IRC-2* compliant methods to be used on converting from IRC2 compliant token to token. 

##### Params

- _to  :  Network address
- _value :  transfer amount 
- _data : data as bytes having keys of 'path' and 'minReturn'.  The original data form is as below. 

  ```json
  {
      "path": "cx863333129b4077652c352ae765d9c4084e35d3d1,cx8e91e81f3db177b7b591f20dac83b2204a7cbee0,cx8e91e81f3db177b7b591f20dac83b2204a7cbee0", 
      "minReturn": 1
  }
  ```
  - path :  conversion path as string which is comma-delimited lists.

  - minReturn: if the conversion results in an amount smaller than the minimum return - it is canceled, must be nonzero.

##### Return

None

## How to deploy ICON DEX 

### Generating Packages

By using a builder in this project, writes target SCOREs and their dependencies to the build directory.

```shell
# Writes all of SCOREs in ICON DEX and their dependencies to the file system under the builder directory. 
$ python build.py 
# Writes SCOREs and their dependencies you write down to the file system under the builder directory. 
$ python build.py <whitespace-delimited lists of SCOREs>
# Cleans all files under the builder directory. 
$ python build.py clean
```

Once you build them, SCORE packages appear in the build directory like the below.
```shell
$ ls build/
converter/      flexible_token/ icx_token/      irc_token/      network/        score_registry/
```


### DEX System Contracts

DEX System Contracts are SCOREs that provide meta information or act as a helper for the DEX system.
It is enough for them to be installed once in a single network.

#### 1. Deploy the Network, Registry, and ICX Token SCOREs at first. 

They don't receive parameters on install as follows.

```
...

"from": "hxcc2c5b620f6cea93d68637bdb536edaf4acea90e",
"to": "cx0000000000000000000000000000000000000000",
"dataType": "deploy",
"data": {
  "contentType": "application/zip",
  "content": "0x504b0304140000000800..."
},

...
```

The result is like the below. 

```
## Network
"scoreAddress": "cx313ef3c3e3862b2261914b517a55133799d637a8",
"status": "0x1",

## Registry
"scoreAddress": "cxd277ff7ca945d080caa59817023e79e1abffae1b",
"status": "0x1",

## ICX Token
"scoreAddress": "cx917060cdce5346f8d5b8f755fcaa2beb20b33b26",
"status": "0x1",
```

#### 2. Register the Network SCORE to the Registry SCORE

Register the Network SCORE to the Registry SCORE by sending a transaction to call an external method of `registerAddress` on the Registry SCORE. You can check it by querying an external method of `getAddress` on the Registry SCORE. 


The APIs are as follows.

##### registerAddress

```python
@external
def registerAddress(self, _scoreName: str, _scoreAddress: Address) -> None:
```

  Register an address to Registry SCORE. 

  ###### Params
  - _scoreName : SCORE name to be registered 
  - _scoreAddress : SCORE address to be registered. In the case, puts in the deployed Network SCORE address. 

##### getAddress

```python
@external(readonly=True)
def getAddress(self, _scoreName: str) -> Address:
```

  Gets an address from the SCORE name. The SCORE have already registered. If not it return ZERO SCORE ADDRESS. 

  ###### Params 
  - _scoreName : the registered SCORE name 
      

The request is like this.

```
...

"from": "hxcc2c5b620f6cea93d68637bdb536edaf4acea90e",
"to": "cxd277ff7ca945d080caa59817023e79e1abffae1b",
"dataType": "call",
"data": {
	"method": "registerAddress",
	"params": {
		"_scoreName": "Network",
		"_scoreAddress": "cx313ef3c3e3862b2261914b517a55133799d637a8"
	}
},

...
```


#### 3. Register the ICX token SCORE to the Network SCORE
Register the ICX token SCORE to the Network SCORE by sending a transaction to call an external method of `registerIcxToken` on the Network SCORE. And send ICX to the ICX token SCORE. 

##### registerIcxToken

```python
@external
def registerIcxToken(self, _icxToken: Address, _register: bool) -> None:
```

  Allows the owner to register/unregister Icx tokens.
  
  ###### Params 
  - _icxToken: Icx token contract address
  - _register: true to register, false to unregister
      
    

The request is like this.

```
...

"from": "hxcc2c5b620f6cea93d68637bdb536edaf4acea90e",
"to": "cx313ef3c3e3862b2261914b517a55133799d637a8",
"dataType": "call",
"data": {
	"method": "registerIcxToken",
	"params": {
		"_icxToken": "cx917060cdce5346f8d5b8f755fcaa2beb20b33b26",
		"_register": "0x1"
	}
},

...
```

### Setup Converter Set 

Once the DEX system SCOREs are set up, multiple converter sets can be added.
The following examples show the converter sets of ICX-TK1 and TK1-TK2. 
For this case, the TK1(`cx0e8dde341e84c31062567ea4249d5f7052332da0`) and TK2(`cx90faecce66a112e2d499cf12f18370e56d8fe3b6`) are IRC2 compliant tokens.  

#### 4. Deploy the Flexible token for the relation of ICX-TK1

Deploy the Flexible token SCORE with four parameter which is _name, _symbol, _initialSupply, and _decimals for initializing.  

##### on_install method of Flexible token SCORE

```python
def on_install(self, _name: str, _symbol: str, _initialSupply: int, _decimals: int) -> None:
```

The Flexible token named  `ICXT-TK1 Flexible Token` and symboled `ICXT-TK1`.
Params of deploying transaction are as below. 
    
```
...

"from": "hxcc2c5b620f6cea93d68637bdb536edaf4acea90e",
"to": "cx0000000000000000000000000000000000000000",
"dataType": "deploy",
"data": {
  "contentType": "application/zip",
  "content": "0x504b0304140000000800..."
  "params": {
    "_name": "ICXT-TK1 Flexible Token",
    "_symbol": "ICXT-TK1",
    "_initialSupply": "0x2625a00",
    "_decimals": "0x12"
  }

},

...
```

And then the result is like the below. 

```
"scoreAddress": "cx0db2449d56fb8f394e54bc5669fd15a4d35ce799",
"status": "0x1",
```

#### 5. Deploy the Converter for the relation of ICX-TK1

The Converter receives 5 params which are `_token`, `_registry`, `_maxConversionFee`, `_connectorToken` and `_connectorWeight`, the details of them are the below.

##### on_install method of Converter SCORE

```python
def on_install(self,
               _token: Address,
               _registry: Address,
               _maxConversionFee: int,
               _connectorToken: Address,
               _connectorWeight: int):
```

  ###### params
  - _token: flexible token governed by the converter
  - _registry: address of a contract registry contract
  -  _maxConversionFee: maximum conversion fee, represented in ppm
  - _connectorToken: optional, initial connector, allows defining the first connector at deployment time
  - _connectorWeight: optional, weight for the initial connector
    

Params of deploying transaction is as below. 
    
```
...

"from": "hxcc2c5b620f6cea93d68637bdb536edaf4acea90e",
"to": "cx0000000000000000000000000000000000000000",
"dataType": "deploy",
"data": {
  "contentType": "application/zip",
  "content": "0x504b0304140000000800..."
  "params": {
    "_token": "cx0db2449d56fb8f394e54bc5669fd15a4d35ce799",
		"_registry": "cxd277ff7ca945d080caa59817023e79e1abffae1b",
		"_maxConversionFee": "0xf4240",
		"_connectorToken": "cx917060cdce5346f8d5b8f755fcaa2beb20b33b26",
		"_connectorWeight": "0x3d090"
  }

},

...
```

The result is like the below. 

```
"scoreAddress": "cxa121a2829bf0be3f4b3e6bfcce76129790a82d44",
"status": "0x1",
```

The converter has just one connector.

![ICXTTK1-ICXT](./img/icxttk1_icxt.svg)


#### 6. Add connector of TK1 by sending a transaction to call an external method of `addConnector` on Converter SCORE.

##### addConnector

```python
@external
def addConnector(self, 
                 _token: Address, 
                 _weight: int, 
                 _enableVirtualBalance: bool) -> None:
```

Defines a new connector for the token. It can only be called by the owner while the converter is inactive.

  ###### Params
  - _token: address of the connector token
  - _weight: constant connector weight, represented in ppm, 1-1000000
  - _enableVirtualBalance: true to enable virtual balance for the connector,  false to disable it


Params of sending a call transaction is as below. 

```
...

"from": "hxcc2c5b620f6cea93d68637bdb536edaf4acea90e",
"to": "cxa121a2829bf0be3f4b3e6bfcce76129790a82d44",
"dataType": "call",
"data": {
	"method": "addConnector",
	"params": {
		"_token": "cx0e8dde341e84c31062567ea4249d5f7052332da0",
		"_weight": "0xb71b0",
		"_enableVirtualBalance": "0x0"
	}
},

...
```

#### 7. Activate the converter

Converters should be activated by using the `acceptTokenOwnership` API in order to convert each token between connectors.

##### acceptTokenOwnership

```python
@external
def acceptTokenOwnership(self) -> None:
```

`acceptTokenOwnership` receives no params as follows.

```
...

"from": "hxcc2c5b620f6cea93d68637bdb536edaf4acea90e",
"to": "cxa121a2829bf0be3f4b3e6bfcce76129790a82d44",
"dataType": "call",
"data": {
	"method": "acceptTokenOwnership"
},

...
```


Now the converter set has been made up like the following image.

![ICXTTK1-ICXT-TK1](./img/icxttk1_icxt_tk1.svg)


Repeating 4 - 7, you can set up another converter set such as TK1-TK2.

![TK1TK2-TK1-TK2](./img/tk1tk2-tk1-tk2.svg)

## How to convert token to the other token 

### Converting ICX token to IRC token 

![icx ft1 irc](./img/icx_ft1_irc.svg)

By calling the [`convert`](#convert) external method, it allows ICX to be converted into IRC. 

From the above tutorial, In case of converting ICX to TK1, the example is like the below.

- to: `NETWORK`
- value: `10,000(ICX)`
- data.method: `"convert"`
- data.params._path: `FROM_TOKEN(ICXT)`, `FLEXIBLE_TOKEN(ICXT-TK1)`, `TO_TOKEN(TK1)`
- data.params.__minReturn: `MINIMUM_ALLOWABLE_AMOUNT`
  
```
...
  
"to": "cx313ef3c3e3862b2261914b517a55133799d637a8",
"value": "0x21e19e0c9bab2400000",
"dataType": "call",
"data": {
  "method": "convert",
  "params": {
    "_path": "cx917060cdce5346f8d5b8f755fcaa2beb20b33b26,cx0db2449d56fb8f394e54bc5669fd15a4d35ce799,cx0e8dde341e84c31062567ea4249d5f7052332da0",
    "_minReturn": "0x21e19e0c9bab240000"
  }
},
  
...

```


### Converting IRC token to IRC token

![irc ft1 irc](./img/irc_ft1_irc.svg)

By calling the [`transfer`](#transfer) external method, it allows IRC token to be converted into the other IRC token. 

From the above tutorial, In case of converting TK1 to TK2, the example is like the below.

- to: `TK1`
- data.method: `"transfer"`
- data.params._to: `NETWORK`
- data.params._value: `10,000(TK1)`
- data.params._data: UTF8ENCODE({"_path":"`TK1`, `TK1-TK2`, `TK2`","_minReturn":"`MINIMUM_ALLOWABLE_AMOUNT`"})"
  
```
...
  
"to": "cx0e8dde341e84c31062567ea4249d5f7052332da0",
"dataType": "call",
"data": {
  "method": "transfer",
  "params": {
    "_to": "cx313ef3c3e3862b2261914b517a55133799d637a8",
    "_value": "0x21e19e0c9bab2400000",
    "_data": "0x7b2270617468223a226378306538646465333431653834633331303632353637656134323439643566373035323333326461302c6378363731656332326138353232353139303634386337313666353463356365653431323532313831342c20637839306661656363653636613131326532643439396366313266313833373065353664386665336236222c226d696e52657475726e223a31303030303030303030303030303030303030303030307d"
  }
},
  
...

```

### Converting token to the other token with multiple converters

![long_path](./img/long_path.svg)

#### Component

- converter : flexible token 1, flexible token 2 ..
- connector token : ICX, IRC1, IRC2 .. 

#### case 1 : Converting ICX to IRC2 with multiple converters

In the case, it excutes conversion same as converting ICX token to IRC token with one converter by calling the [`convert`](#convert) external method.

The difference is conversion path, see conversion path format above.

From the above tutorial, In case of converting ICX to TK2, the example is like the below.

- to: `NETWORK`
- value: `10,000(ICX)`
- data.method: `"convert"`
- data.params._path: `ICXT`, `ICXT-TK1`, `TK1`, `TK1-TK2`, `TK2`
- data.params.__minReturn: `MINIMUM_ALLOWABLE_AMOUNT`
  
```
...
  
"to": "cx313ef3c3e3862b2261914b517a55133799d637a8",
"value": "0x21e19e0c9bab2400000",
"dataType": "call",
"data": {
  "method": "convert",
  "params": {
    "_path": "cx917060cdce5346f8d5b8f755fcaa2beb20b33b26,cx0db2449d56fb8f394e54bc5669fd15a4d35ce799,cx0e8dde341e84c31062567ea4249d5f7052332da0,cx671ec22a85225190648c716f54c5cee412521814,cx90faecce66a112e2d499cf12f18370e56d8fe3b6",
    "_minReturn": "0x21e19e0c9bab240000"
  }
},
  
...

```

#### case 2 : Converting IRC to ICX with muliple converters

In the case, it excutes conversion same as converting IRC token to IRC token with one converter by calling the [`transfer`](#transfer) external method.

The difference is conversion path, see conversion path format above.

From the above tutorial, In case of converting TK2 to ICX, the example is like the below.

- to: `TK2`
- data.method: `"transfer"`
- data.params._to: `NETWORK`
- data.params._value: `10,000(TK2)`
- data.params._data: UTF8ENCODE({"_path":"`TK2`, `TK1-TK2`, `TK1`, `ICXT-TK1`, `ICXT`","_minReturn":"`MINIMUM_ALLOWABLE_AMOUNT`"})"
  
```
...
  
"to": "cx90faecce66a112e2d499cf12f18370e56d8fe3b6",
"dataType": "call",
"data": {
  "method": "transfer",
  "params": {
    "_to": "cx313ef3c3e3862b2261914b517a55133799d637a8",
    "_value": "0x21e19e0c9bab2400000",
    "_data": "0x7b2270617468223a226378393066616563636536366131313265326434393963663132663138333730653536643866653362362c6378363731656332326138353232353139303634386337313666353463356365653431323532313831342c206378306538646465333431653834633331303632353637656134323439643566373035323333326461302c6378306462323434396435366662386633393465353462633536363966643135613464333563653739392c20637839313730363063646365353334366638643562386637353566636161326265623230623333623236222c226d696e52657475726e223a313030303030303030303030303030303030307d"
  }
},
  
...

```

### Getting expected amount of the token 

By querying the [`getExpectedReturnByPath`](#getExpectedReturnByPath) which is read-only external method, it allows to get expected amount of the token.

From the above tutorial, In case of estimating ICX to TK1, the example is like the below.

- to: `NETWORK`
- data.method: `"getExpectedReturnByPath"`
- data.params._path: `ICXT`,`ICXT-TK1`,`TK1`
- data.params._amount: `10,000(ICX)`

```
...
  
"to": "cx313ef3c3e3862b2261914b517a55133799d637a8",
"dataType": "call",
"data": {
  "method": "getExpectedReturnByPath",
    "params": {
      "_path": "cx917060cdce5346f8d5b8f755fcaa2beb20b33b26,cx0db2449d56fb8f394e54bc5669fd15a4d35ce799,cx0e8dde341e84c31062567ea4249d5f7052332da0",
      "_amount": "0x21e19e0c9bab2400000"
    }

},
  
...
```

The result is like the below.

```
{
  "jsonrpc": "2.0",
  "result": "0xfbd47cc221b588ad503",
  "id": 1234
}
```

## Samples for Testnet ([Euljiro](https://github.com/icon-project/icon-project.github.io/blob/master/docs/icon_network.md#testnet-for-exchanges))

### Contracts

#### 1. DEX System Contracts

- Network: `cx313ef3c3e3862b2261914b517a55133799d637a8`
- Registry: `cxd277ff7ca945d080caa59817023e79e1abffae1b`
- ICXToken (ICXT): `cx917060cdce5346f8d5b8f755fcaa2beb20b33b26`

#### 2. Sample Tokens

- TOKEN ONE (TK1): `cx0e8dde341e84c31062567ea4249d5f7052332da0`
- TOKEN TWO (TK2): `cx90faecce66a112e2d499cf12f18370e56d8fe3b6`

#### 3. Sample Converter Set (between ICXT and TK1) 

- ICXT-TK1 Flexible Token (ICXT-TK1): `cx0db2449d56fb8f394e54bc5669fd15a4d35ce799`
- Converter: `cxa121a2829bf0be3f4b3e6bfcce76129790a82d44`
- Initial Reserves: 
    - 100,000 ICXT with 25% Weight
    - 3,000,000 TK1 with 75% Weight
    - ICX:TK1 = 10:1

#### 4. Sample Converter Set (between TK1 and TK2) 

- TK1-TK2 Flexible Token (TK1-TK2): `cx671ec22a85225190648c716f54c5cee412521814`
- Converter: `cx6a622e5af96b1b02f489afa9972ce30bee2ae459`
- Initial Reserves: 
    - 1,000,000 TK1 with 50% Weight
    - 4,000,000 TK2 with 50% Weight
    - TK1:TK2 = 4:1

### Examples

#### 1. Conversion from 10,000 ICXs to TK1

- Json RPC Params
  - to: `NETWORK`
  - value: `10,000(ICX)`
  - data.method: `"convert"`
  - data.params._path: `FROM_TOKEN(ICXT)`, `FLEXIBLE_TOKEN(ICXT-TK1)`, `TO_TOKEN(TK1)`
  - data.params.__minReturn: `MINIMUM_ALLOWABLE_AMOUNT`
  
  ```
  ...
  
  "to": "cx313ef3c3e3862b2261914b517a55133799d637a8",
  "value": "0x21e19e0c9bab2400000",
  "dataType": "call",
  "data": {
    "method": "convert",
    "params": {
      "_path": "cx917060cdce5346f8d5b8f755fcaa2beb20b33b26,cx0db2449d56fb8f394e54bc5669fd15a4d35ce799,cx0e8dde341e84c31062567ea4249d5f7052332da0",
      "_minReturn": "0x21e19e0c9bab240000"
    }
  },
  
  ...

  ```
  
  > https://trackerdev.icon.foundation/transaction/0x846f33d9f39e6a13c127151d32ab07c4bfa5b08a248f3b6e8a920652bcafddee


#### 2. Conversion from 10,000 ICXs to TK2

- Json RPC Params
  - to: `NETWORK`
  - value: `10,000(ICX)`
  - data.method: `"convert"`
  - data.params._path: `ICXT`, `ICXT-TK1`, `TK1`, `TK1-TK2`, `TK2`
  - data.params.__minReturn: `MINIMUM_ALLOWABLE_AMOUNT`
  
  ```
  ...
  
  "to": "cx313ef3c3e3862b2261914b517a55133799d637a8",
  "value": "0x21e19e0c9bab2400000",
  "dataType": "call",
  "data": {
    "method": "convert",
    "params": {
      "_path": "cx917060cdce5346f8d5b8f755fcaa2beb20b33b26,cx0db2449d56fb8f394e54bc5669fd15a4d35ce799,cx0e8dde341e84c31062567ea4249d5f7052332da0,cx671ec22a85225190648c716f54c5cee412521814,cx90faecce66a112e2d499cf12f18370e56d8fe3b6",
      "_minReturn": "0x21e19e0c9bab240000"
    }
  },
  
  ...

  ```
  
  > https://trackerdev.icon.foundation/transaction/0x42e12be4099863ae16f28487ce9dba14149be40974104f5e05d8fecd265ba1fb


## License 

This project follows the Apache 2.0 License. Please refer to [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) for details.