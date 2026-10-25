from enum import Enum


class HandlerStateMachine(str, Enum):
    CONNECTED = "CONNECTED"
    IN_LOBBY = "IN_LOBBY"
    IN_SESSION = "IN_SESSION"
    DISCONNECTED = "DISCONNECTED"


class SessionStateMachine(str, Enum):
    LOBBY = "LOBBY"
    IN_SESSION = "IN_SESSION"
    ENDED = "ENDED"


ALLOWED_TRANSITIONS = {
    HandlerStateMachine.CONNECTED: [HandlerStateMachine.IN_LOBBY],
    HandlerStateMachine.IN_LOBBY: [
        HandlerStateMachine.DISCONNECTED,
        HandlerStateMachine.IN_SESSION,
    ],
    HandlerStateMachine.IN_SESSION: [HandlerStateMachine.IN_LOBBY],
}


def is_valid_transition(current: HandlerStateMachine, to: HandlerStateMachine) -> bool:
    if current not in ALLOWED_TRANSITIONS:
        return False
    return to in ALLOWED_TRANSITIONS[current] or to == current
