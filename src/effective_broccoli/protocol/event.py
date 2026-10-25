from enum import Enum


class Event(str, Enum):
    # Create new room
    CREATE = "CREATE"
    # When a room is created a key is sent back to the host
    KEY = "KEY"
    # Join an existing room
    JOIN = "JOIN"
    # After room is created the host needs to wait for all player to join,
    # when all players have joined they have to wait for the host to start
    WAITING = "WAITING"
    # Start an existing game
    START = "START"
    # Next round, as per domain
    ADVANCE = "ADVANCE"
    # Reset all round and their history
    RESET = "RESET"
    # Any action that is required for the domain
    ACTION = "ACTION"
    # When a session state ends (either someone won, or it's a draw etc.)
    END = "END"
    # ...
    TURN = "TURN"
    # Random info for the client, supposedly not actionable
    INFO = "INFO"
    # Don't raise error or the socket connection would fail,
    # instead send an error event back to the client with disconnecting them
    ERROR = "ERROR"
    # unused for now, might remove
    DISCONNECT = "DISCONNECT"
