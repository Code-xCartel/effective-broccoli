import secrets
from types import SimpleNamespace
from typing import Dict, Optional, Set, Tuple

from websockets import ServerConnection

from effective_broccoli.protocol.event import Event
from effective_broccoli.protocol.message import Message


class Session:
    def __init__(self):
        self.sessions: Dict[str, Tuple[SimpleNamespace, Set[ServerConnection]]] = {}

    async def create(self, websocket: ServerConnection):
        join_key = secrets.token_urlsafe(6)
        game = SimpleNamespace()
        self.sessions[join_key] = game, {websocket}
        await websocket.send(
            Message(Event.KEY, join_key=join_key, description="Session Created.").dump
        )
        return

    async def join(self, websocket: ServerConnection, join_key: Optional[str]):
        if not join_key:
            await websocket.send(
                Message(Event.ERROR, description="Join Key Required").dump
            )
            return
        try:
            game, join = self.sessions[join_key]
        except KeyError:
            raise Exception(f"No Session For {join_key}")

        if len(join) >= 2:
            await websocket.send(Message(Event.ERROR, description="Session Full.").dump)
            return

        host = next(iter(join))
        join.add(websocket)
        await websocket.send(
            Message(Event.JOIN, description=f"Session Joined, Host: {host.id}").dump
        )
        await host.send(
            Message(Event.JOIN, description=f"{websocket.id} Joined Your Session").dump
        )
        return
