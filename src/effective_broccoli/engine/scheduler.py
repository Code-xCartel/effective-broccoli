import random
import uuid
from typing import Any, List, Literal, Optional

from effective_broccoli.domain.abstract import AbstractDomain
from effective_broccoli.protocol.schemas.abstract import AbstractAction
from effective_broccoli.protocol.schemas.domain_result import DomainResult


class Scheduler:
    def __init__(self, domain: AbstractDomain) -> None:
        self.domain = domain
        self.entity_list: List[uuid.UUID] = []
        self.current_state_entity: Optional[uuid.UUID] = None

    def initialize(self, entity_list: List[uuid.UUID]) -> None:
        if self.current_state_entity is not None or self.entity_list:
            raise RuntimeError(
                "Scheduler Has Already Initialized, "
                "Do Not Initialize Outside Of Session."
            )
        self.entity_list = entity_list
        self.current_state_entity = random.choice(self.entity_list)

    def reset_state(self) -> None:
        self.randomize_state()

    def randomize_state(self) -> None:
        self.current_state_entity = random.choice(self.entity_list)

    def flip_entity(self) -> None:
        if self.current_state_entity == self.entity_list[0]:
            self.current_state_entity = self.entity_list[1]
        else:
            self.current_state_entity = self.entity_list[0]

    def action(self, entity: uuid.UUID, action: AbstractAction) -> DomainResult:
        if self.current_state_entity is None:
            raise RuntimeError("Cannot Perform Action On Uninitialized Scheduler.")
        if self.current_state_entity != entity:
            raise RuntimeError("Cannot Perform Action On This Scheduler Cycle.")
        self.domain.play_move(entity, action)
        domain_result = self.domain.validate()
        self.flip_entity()

        return domain_result

    def update_domain(self, action: Literal["advance", "reset"]) -> None:
        self.reset_state()
        if action == "advance":
            self.domain.new_round()
        elif action == "reset":
            self.domain.reset()

    def get_domain_info(self) -> Optional[Any]:
        if hasattr(self.domain, "get_summary") and callable(
            getattr(self.domain, "get_summary")
        ):
            return self.domain.get_summary()
        return None
