import asyncio
from typing import Any, Awaitable, Callable, Optional, Tuple

import websockets
from websockets import ServerConnection

from effective_broccoli.domain.registry import get_domain_from_registry
from effective_broccoli.protocol.event import Event
from effective_broccoli.protocol.message import Message
from effective_broccoli.server.session import Session
from effective_broccoli.server.session_registry import SessionRegistry
from effective_broccoli.server.states import HandlerStateMachine, is_valid_transition


async def handle_state_transition(
    current: HandlerStateMachine,
    to: HandlerStateMachine,
    callback: Callable[..., Awaitable[Any]],
    **kwargs,
) -> Tuple[Optional[Session], HandlerStateMachine]:
    if is_valid_transition(current, to):
        _current_session = await callback(**kwargs)
        return _current_session, to
    else:
        raise RuntimeError("Invalid State.")


async def main(domain: str) -> None:
    _domain = get_domain_from_registry(domain=domain)
    registry = SessionRegistry(domain=_domain)

    async def handler(websocket: ServerConnection) -> None:
        _current_session = None
        _current_state = HandlerStateMachine.CONNECTED
        async for _message in websocket:
            try:
                message = Message.parse(_message)
                message.assert_event()

                match message.event:
                    case Event.CREATE:
                        (
                            _current_session,
                            _current_state,
                        ) = await handle_state_transition(
                            _current_state,
                            HandlerStateMachine.IN_LOBBY,
                            registry.create,
                            websocket=websocket,
                        )
                    case Event.JOIN:
                        (
                            _current_session,
                            _current_state,
                        ) = await handle_state_transition(
                            _current_state,
                            HandlerStateMachine.IN_LOBBY,
                            registry.join,
                            websocket=websocket,
                            join_key=message.join_key,
                        )
                    case Event.START:
                        (
                            _,
                            _current_state,
                        ) = await handle_state_transition(
                            _current_state,
                            HandlerStateMachine.IN_SESSION,
                            _current_session.start,  # type: ignore
                            websocket=websocket,
                        )
                    case Event.ACTION:
                        await handle_state_transition(
                            _current_state,
                            HandlerStateMachine.IN_SESSION,
                            _current_session.perform_action,  # type: ignore
                            websocket=websocket,
                            action=message.action,
                        )
                    case Event.ADVANCE:
                        await handle_state_transition(
                            _current_state,
                            HandlerStateMachine.IN_SESSION,
                            _current_session.update,  # type: ignore
                            websocket=websocket,
                            action="advance",
                        )
                    case Event.RESET:
                        await handle_state_transition(
                            _current_state,
                            HandlerStateMachine.IN_SESSION,
                            _current_session.update,  # type: ignore
                            websocket=websocket,
                            action="reset",
                        )
                    # Realistically, it's not reachable since event is asserted above
                    case _:
                        raise RuntimeError("How Did We Get Here?")
            except RuntimeError as e:
                await websocket.send(Message(Event.ERROR, description=str(e)).dump)

    server = await websockets.serve(handler, "", 8765)
    print("Listening on port 8765")
    await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main(domain="RPS"))
