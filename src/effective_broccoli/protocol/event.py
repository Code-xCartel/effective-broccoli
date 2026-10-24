from enum import Enum


class Event(str, Enum):
    CREATE = "CREATE"
    JOIN = "JOIN"
    DISCONNECT = "DISCONNECT"
    KEY = "KEY"
    ERROR = "ERROR"
