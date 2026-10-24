import asyncio

import websockets
from websockets import ServerConnection

from effective_broccoli.protocol.event import Event
from effective_broccoli.protocol.message import Message
from effective_broccoli.server.session import Session


async def handler(websocket: ServerConnection) -> None:
    _message = await websocket.recv()
    message = Message.parse(_message)
    message.assert_event()

    session = Session()
    match message.event:
        case Event.CREATE:
            return await session.create(websocket)
        case Event.JOIN:
            return await session.join(websocket, message.join_key)
        case _:  # realistically, it's not reachable since event is asserted above
            raise Exception("Invalid Event")


async def main() -> None:
    server = await websockets.serve(handler, "", 8765)
    await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
