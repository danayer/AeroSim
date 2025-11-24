"""
AeroSim EDU - Симулятор аэропорта для образовательных целей
"""

__version__ = "1.0.0"
__author__ = "AeroSim EDU Team"
__license__ = "MIT"

from .core.simulator import AirportSimulator
from .models.aircraft import Aircraft
from .models.passenger import Passenger
from .models.runway import Runway

__all__ = [
    "AirportSimulator",
    "Aircraft",
    "Passenger",
    "Runway",
]
