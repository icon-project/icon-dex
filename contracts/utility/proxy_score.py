from iconservice import InterfaceScore
from iconservice import interface
from iconservice.iconscore.icon_score_constant import T


class ProxyScore(type):
    """
    A Proxy class that provides an Interface SCORE from the abc class

    usage:
        token_score = self.create_interface_score(token_address, ProxyScore(ABCIRCToken))
        token_score.transfer(to, value)
    """

    @classmethod
    def _create_class_proxy(mcs, abc_class: T) -> T:
        """
        Creates an interface SCORE related in given abc class,

        :param abc_class: An abstract class
        :return: interface SCORE class
        """

        interface_functions = {}

        for attribute in abc_class.__dict__.values():
            if callable(attribute) \
                    and hasattr(attribute, '__isabstractmethod__') \
                    and attribute.__isabstractmethod__:
                attribute.__isabstractmethod__ = False
                interface_functions[attribute.__name__] = interface(attribute)

        proxy_name = "%s(%s)" % (mcs.__name__, abc_class.__name__)
        return type(proxy_name, (InterfaceScore, abc_class), interface_functions)

    def __new__(mcs, abc_class: T) -> T:
        """
        Retrieves an interface SCORE related in given abc class if the cache exists,
        otherwise creates a new one

        :param abc_class: An abstract class
        :return: interface SCORE class
        """
        try:
            cache = mcs.__dict__["_class_proxy_cache"]
        except KeyError:
            mcs._class_proxy_cache = cache = {}
        try:
            proxy_class = cache[abc_class]
        except KeyError:
            cache[abc_class] = proxy_class = mcs._create_class_proxy(abc_class)
        return proxy_class
