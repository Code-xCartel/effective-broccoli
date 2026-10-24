import json
from typing import Any, Dict, Optional

from .event import Event


class Message:
    def __init__(
        self,
        event: Event,
        join_key: Optional[str] = None,
        action: Optional[Any] = None,
        description: Optional[str] = None,
    ) -> None:
        self.event = event
        self.join_key: Optional[str] = join_key
        self.action: Optional[Any] = action
        self.description: Optional[str] = description

    @property
    def dump(self) -> str:
        dumper: Dict[str, Any] = {
            "event": self.event,
        }
        if self.join_key:
            dumper["join_key"] = self.join_key
        if self.action:
            dumper["action"] = self.action
        return json.dumps(dumper)

    @classmethod
    def parse(cls, message: Any) -> "Message":
        try:
            message = json.loads(message)
            return cls(**message)
        except json.decoder.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON message: {e}")

    def assert_event(self) -> None:
        try:
            Event(self.event)
        except ValueError as e:
            raise ValueError(f"Invalid event: {self.event}: {e}")
