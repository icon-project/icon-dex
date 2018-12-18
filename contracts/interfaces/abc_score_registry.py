from iconservice import *


# noinspection PyPep8Naming
class ABCScoreRegistry(ABC):
    """
    ScoreRegistry interface
    """
    SCORE_FEATURES = "ScoreFeatures"
    SCORE_REGISTRY = "ScoreRegistry"

    # todo: consider the name of dex score (whether use bancor or not)
    BANCOR_NETWORK = "BancorNetwork"
    BANCOR_FORMULA = "BancorForMula"

    # todo: consider the name of dex token (whether use bnt or not)
    BNT_TOKEN = "BNTToken"
    BNT_CONVERTER = "BNTConverter"

    @abstractmethod
    def getAddressFromBytesName(self, _scoreName: bytes) -> 'Address':
        """
        Returns score address
        :param _scoreName:
        :return:
        """
        pass
