"""
Модели данных для аэропорта
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class AircraftType(Enum):
    """Типы воздушных судов"""
    AIRBUS_A320 = "A320"
    AIRBUS_A380 = "A380"
    BOEING_737 = "B737"
    BOEING_777 = "B777"
    BOMBARDIER_CRJ = "CRJ"


class AircraftStatus(Enum):
    """Статус самолета"""
    IN_FLIGHT = "in_flight"
    APPROACHING = "approaching"
    PARKED = "parked"
    BOARDING = "boarding"
    READY_FOR_DEPARTURE = "ready_for_departure"
    DEPARTED = "departed"
    MAINTENANCE = "maintenance"


@dataclass
class Aircraft:
    """Модель воздушного судна"""
    
    aircraft_id: str
    aircraft_type: AircraftType
    capacity: int
    current_passengers: int = 0
    status: AircraftStatus = AircraftStatus.IN_FLIGHT
    gate_id: Optional[str] = None
    arrival_time: float = 0.0
    departure_time: float = 0.0
    delay: float = 0.0
    fuel_level: float = 100.0  # Процент
    maintenance_needed: bool = False
    baggage_count: int = 0
    
    def __repr__(self) -> str:
        return (
            f"Aircraft({self.aircraft_id}, {self.aircraft_type.value}, "
            f"status={self.status.value}, gate={self.gate_id})"
        )
    
    def is_at_capacity(self) -> bool:
        """Проверить, полон ли самолет"""
        return self.current_passengers >= self.capacity
    
    def add_passengers(self, count: int) -> int:
        """
        Добавить пассажиров
        
        Returns:
            Количество добавленных пассажиров
        """
        available_space = self.capacity - self.current_passengers
        added = min(count, available_space)
        self.current_passengers += added
        return added
    
    def remove_passengers(self, count: int) -> int:
        """Удалить пассажиров"""
        removed = min(count, self.current_passengers)
        self.current_passengers -= removed
        return removed
