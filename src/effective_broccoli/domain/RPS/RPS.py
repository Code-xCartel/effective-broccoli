import uuid
from typing import Dict, List, Tuple

from effective_broccoli.domain.abstract import AbstractDomain
from effective_broccoli.protocol.schemas.abstract import AbstractAction
from effective_broccoli.protocol.schemas.domain_result import DomainResult, ResultState
from effective_broccoli.protocol.schemas.RPS.RPS import RPSAction

WINS = {
    (RPSAction.ROCK, RPSAction.SCISSOR),
    (RPSAction.PAPER, RPSAction.ROCK),
    (RPSAction.SCISSOR, RPSAction.PAPER),
}


class RPS(AbstractDomain):
    def __init__(self) -> None:
        self.round: int = 1
        self.move_set: Dict[uuid.UUID, RPSAction] = {}
        self.summary: List[Dict[int, Dict[uuid.UUID, RPSAction]]] = []

    def play_move(self, player: uuid.UUID, move: AbstractAction) -> None:
        if not isinstance(move, RPSAction):
            raise RuntimeError("Invalid Action Provided For Domain RPS")
        if player in self.move_set:
            raise RuntimeError(f"Player {player} Already Played")
        self.move_set[player] = move

    def validate(self) -> DomainResult:
        if len(self.move_set) != 2:
            return DomainResult(
                state=ResultState.INCOMPLETE,
                winner=None,
            )
        m1, m2 = self.move_set.items()
        if (m1[1], m2[1]) in WINS:
            res = DomainResult(state=ResultState.WINNER, winner=m1[0])
        elif (m2[1], m1[1]) in WINS:
            res = DomainResult(state=ResultState.WINNER, winner=m2[0])
        else:
            res = DomainResult(state=ResultState.DRAW)
        self.summary.append({self.round: self.move_set})
        return res

    def new_round(self) -> None:
        self.round = self.round + 1
        self.move_set = {}

    def reset(self) -> None:
        self.round = 1
        self.move_set = {}
        self.summary = []

    def get_summary(self) -> Tuple[int, List[Dict[int, Dict[uuid.UUID, RPSAction]]]]:
        return self.round, self.summary
