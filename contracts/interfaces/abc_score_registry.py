from iconservice import *


# noinspection PyPep8Naming
class ABCScoreRegistry(ABC):
    """
    ScoreRegistry interface
    """
    # todo: consider administrating ids using Enum ( cannot import Enum class now )
    SCORE_FEATURES = "ScoreFeatures"
    SCORE_REGISTRY = "ScoreRegistry"

    # todo: consider the name of dex score (whether use bancor or not)
    BANCOR_NETWORK = "BancorNetwork"
    BANCOR_FORMULA = "BancorForMula"

    # todo: consider the name of dex token (whether use bnt or not)
    BNT_TOKEN = "BNTToken"
    BNT_CONVERTER = "BNTConverter"

    SCORE_KEYS = [SCORE_FEATURES, SCORE_REGISTRY, BANCOR_NETWORK, BANCOR_FORMULA, BNT_TOKEN, BNT_CONVERTER]

    @abstractmethod
    def getAddress(self, _scoreName: bytes) -> 'Address':
        """
        Returns score address
        :param _scoreName:
        :return:
        """
        pass
