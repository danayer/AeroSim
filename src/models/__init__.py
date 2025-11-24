"""
Модели данных
"""

from .aircraft import Aircraft, AircraftType, AircraftStatus
from .passenger import Passenger, PassengerStatus, PassengerType, PriorityMode, TimeLog
from .runway import Runway, RunwayStatus
from .gate import Gate, GateStatus
from .airport import Airport, Terminal
from .control_point import ControlPoint
from .passenger_queue import PassengerQueue
from .terminal import Terminal as TerminalClass

__all__ = [
    "Aircraft",
    "AircraftType",
    "AircraftStatus",
    "Passenger",
    "PassengerStatus",
    "PassengerType",
    "PriorityMode",
    "TimeLog",
    "Runway",
    "RunwayStatus",
    "Gate",
    "GateStatus",
    "Airport",
    "Terminal",
    "ControlPoint",
    "PassengerQueue",
    "TerminalClass",
]
