import unittest
from unittest.mock import Mock, patch

from iconservice import ABC, abstractmethod, Address, IconScoreBase
from iconservice.iconscore.internal_call import InternalCall

from contracts.utility.proxy_score import ProxyScore


class ABCToken1(ABC):

    @abstractmethod
    def transfer(self, _to: 'Address', _value: int, _data: bytes = None):
        pass


class ABCToken2(ABC):

    @abstractmethod
    def transfer(self, _to: 'Address', _value: int, _data: bytes = None):
        pass


ScoreInterface = ProxyScore(ABCToken1)


class TestProxyScore(unittest.TestCase):

    def test_proxy_creation(self):
        # tests the attributes are properly imported
        assert hasattr(ScoreInterface, 'transfer')

        # tests the proxy class cache
        ScoreInterface0 = ProxyScore(ABCToken1)
        ScoreInterface1 = ProxyScore(ABCToken1)
        ScoreInterface2 = ProxyScore(ABCToken2)

        # If the ABC class names are same each other, the proxy class will be created once.
        assert ScoreInterface0 is ScoreInterface1
        # otherwise creates new one
        assert ScoreInterface0 is not ScoreInterface2

    def test_proxy_call(self):
        # tests the proxy call

        self_address = Mock(Address)
        score_address = Mock(Address)
        to_address = Mock(Address)

        value = 1

        icon_score_base = Mock(IconScoreBase)
        icon_score_base.address = self_address

        score = ScoreInterface(score_address, icon_score_base)

        with patch.object(InternalCall, 'other_external_call') as external_call:
            score.transfer(to_address, value)

            external_call.assert_called()
            call_args = external_call.call_args_list[0][0]
            assert call_args[1] is self_address  # from score
            assert call_args[2] is score_address  # to score
            assert call_args[4] == 'transfer'  # function name
            assert call_args[5][0] is to_address  # param1: _to address
            assert call_args[5][1] == 1  # param2: _value
