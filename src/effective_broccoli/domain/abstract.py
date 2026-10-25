import abc
import uuid

from effective_broccoli.protocol.schemas.abstract import AbstractAction
from effective_broccoli.protocol.schemas.domain_result import DomainResult


# Just for typing
class AbstractDomain(abc.ABC):
    @abc.abstractmethod
    def play_move(self, entity: uuid.UUID, action: AbstractAction) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def validate(self) -> DomainResult:
        raise NotImplementedError()

    @abc.abstractmethod
    def new_round(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def reset(self) -> None:
        raise NotImplementedError()
