from typing import Literal, Set

from websockets import ServerConnection, broadcast

from effective_broccoli.domain.abstract import AbstractDomain
from effective_broccoli.engine.scheduler import Scheduler
from effective_broccoli.protocol.event import Event
from effective_broccoli.protocol.message import Message
from effective_broccoli.protocol.schemas.abstract import AbstractAction
from effective_broccoli.protocol.schemas.domain_result import ResultState
from effective_broccoli.server.states import SessionStateMachine

MAX_ENTITIES_PER_SESSION = 2


class Session:
    def __init__(
        self, host: ServerConnection, join_key: str, domain: AbstractDomain
    ) -> None:
        self.join_key = join_key
        self.host = host
        self.connections: Set[ServerConnection] = set()
        self.scheduler = Scheduler(domain=domain)
        self.state: SessionStateMachine = SessionStateMachine.LOBBY

    def add(self, session: ServerConnection) -> None:
        if len(self.connections) >= MAX_ENTITIES_PER_SESSION:
            raise RuntimeError(f"Only {MAX_ENTITIES_PER_SESSION} Players Are Allowed.")
        self.connections.add(session)

    async def start(self, websocket: ServerConnection) -> None:
        if self.host.id != websocket.id:
            raise RuntimeError("Only Host Can Start Session.")
        if len(self.connections) < MAX_ENTITIES_PER_SESSION:
            raise RuntimeError("Cannot Start Incomplete Session.")
        broadcast(
            self.connections,
            Message(Event.INFO, description="Session Started.").dump,
        )
        self.state = SessionStateMachine.IN_SESSION
        self.scheduler.initialize([conn.id for conn in self.connections])
        broadcast(
            self.connections,
            Message(
                Event.TURN, payload={"detail": self.scheduler.current_state_entity}
            ).dump,
        )

    async def perform_action(
        self, websocket: ServerConnection, action: AbstractAction
    ) -> None:
        if self.state != SessionStateMachine.IN_SESSION:
            raise RuntimeError("Session State Is Invalid.")
        action_result = self.scheduler.action(websocket.id, action)

        match action_result.state:
            case ResultState.INCOMPLETE:
                broadcast(
                    self.connections,
                    Message(
                        Event.TURN,
                        payload={"detail": self.scheduler.current_state_entity},
                    ).dump,
                )
            case ResultState.WINNER:
                self.state = SessionStateMachine.ENDED
                broadcast(
                    self.connections,
                    Message(Event.END, description=f"{action_result.winner} Won.").dump,
                )
            case ResultState.DRAW:
                self.state = SessionStateMachine.ENDED
                broadcast(
                    self.connections, Message(Event.END, description="Its A Draw.").dump
                )

    async def update(
        self, websocket: ServerConnection, action: Literal["advance", "reset"]
    ) -> None:
        if self.state != SessionStateMachine.ENDED:
            raise RuntimeError("Session State Is Invalid.")
        if self.host.id != websocket.id:
            raise RuntimeError("Only Host Can Start Session.")
        self.state = SessionStateMachine.IN_SESSION
        self.scheduler.update_domain(action)
        broadcast(
            self.connections,
            Message(Event.INFO, payload=self.scheduler.get_domain_info()).dump,
        )
        broadcast(
            self.connections,
            Message(
                Event.TURN, payload={"detail": self.scheduler.current_state_entity}
            ).dump,
        )
