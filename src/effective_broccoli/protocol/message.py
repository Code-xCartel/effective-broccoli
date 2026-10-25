import json
from typing import Any, Dict, Optional

from .event import Event
from .schemas.abstract import AbstractAction


class Message:
    def __init__(
        self,
        event: Event,
        join_key: Optional[str] = None,
        action: Optional[AbstractAction] = None,
        payload: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> None:
        self.event = event
        self.join_key = join_key
        self.action = action
        self.payload = payload
        self.description = description

    @property
    def dump(self) -> str:
        dumper: Dict[str, Any] = {
            "event": self.event,
        }
        if self.join_key:
            dumper["join_key"] = self.join_key
        if self.payload:
            dumper["payload"] = self.payload
        if self.description:
            dumper["description"] = self.description
        if self.action:
            # IDK why the linter thinks this code is unreachable??
            dumper["action"] = self.action
        return json.dumps(dumper)

    @classmethod
    def parse(cls, message: Any) -> "Message":
        try:
            message = json.loads(message)
            return cls(**message)
        except json.decoder.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON Message: {e}.")

    def assert_event(self, against: Optional[Event] = None) -> None:
        try:
            Event(self.event)
            if against and self.event != against:
                raise ValueError
        except ValueError as e:
            raise RuntimeError(f"Invalid Event: {self.event}: {e}.")
