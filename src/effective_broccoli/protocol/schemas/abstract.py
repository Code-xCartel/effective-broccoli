import abc
from enum import Enum, EnumMeta


class ABCEnumMeta(EnumMeta, abc.ABCMeta):
    pass


class AbstractAction(str, Enum, metaclass=ABCEnumMeta):
    pass
