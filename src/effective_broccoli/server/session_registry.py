import secrets
from typing import Dict, Optional

from websockets import ServerConnection

from effective_broccoli.domain.abstract import AbstractDomain
from effective_broccoli.protocol.event import Event
from effective_broccoli.protocol.message import Message
from effective_broccoli.server.session import Session


class SessionRegistry:
    def __init__(self, domain: type[AbstractDomain]):
        self.domain = domain
        self.sessions: Dict[str, Session] = {}

    async def create(self, websocket: ServerConnection) -> Session:
        join_key = secrets.token_urlsafe(6)
        session = Session(host=websocket, join_key=join_key, domain=self.domain())
        session.add(websocket)
        self.sessions[join_key] = session
        await websocket.send(
            Message(
                Event.KEY,
                join_key=join_key,
                description="Session Created, Waiting For Other Player To Join.",
            ).dump
        )
        return session

    async def join(
        self, websocket: ServerConnection, join_key: Optional[str]
    ) -> Session:
        if not join_key:
            raise RuntimeError("Join Key Required.")
        try:
            session = self.sessions[join_key]
            session.add(websocket)

            await websocket.send(
                Message(
                    Event.WAITING,
                    description=f"Session Joined, Host: {session.host.id}.",
                ).dump
            )
            await session.host.send(
                Message(
                    Event.WAITING, description=f"{websocket.id} Joined Your Session."
                ).dump
            )
            return session
        except KeyError:
            raise RuntimeError(f"No Session For {join_key}.")
