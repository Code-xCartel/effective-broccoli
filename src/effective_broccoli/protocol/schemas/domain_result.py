import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ResultState(str, Enum):
    INCOMPLETE = "INCOMPLETE"
    WINNER = "WINNER"
    DRAW = "DRAW"


@dataclass
class DomainResult:
    state: ResultState
    winner: Optional[uuid.UUID] = None
