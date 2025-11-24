"""
Система событий для дискретно-событийной симуляции (DES)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional


class EventType(Enum):
    """Типы событий в аэропорту"""
    
    # События самолета
    AIRCRAFT_ARRIVAL = "aircraft_arrival"
    AIRCRAFT_TAKEOFF = "aircraft_takeoff"
    AIRCRAFT_PARKING = "aircraft_parking"
    AIRCRAFT_DEPARTURE_READY = "aircraft_departure_ready"
    
    # События пассажиров
    PASSENGER_ARRIVAL = "passenger_arrival"
    PASSENGER_ENTRY = "passenger_entry"  # Вход пассажира в терминал
    PASSENGER_CHECKIN = "passenger_checkin"
    PASSENGER_BOARDING = "passenger_boarding"
    PASSENGER_DEPARTURE = "passenger_departure"
    
    # События багажа
    BAGGAGE_UNLOAD = "baggage_unload"
    BAGGAGE_LOAD = "baggage_load"
    BAGGAGE_DELIVERY = "baggage_delivery"
    
    # События ресурсов
    GATE_OCCUPIED = "gate_occupied"
    GATE_RELEASED = "gate_released"
    RUNWAY_OCCUPIED = "runway_occupied"
    RUNWAY_RELEASED = "runway_released"
    
    # События обслуживания
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"
    
    # События очереди
    QUEUE_UPDATED = "queue_updated"
    DELAY_OCCURRED = "delay_occurred"


@dataclass
class Event:
    """Представление события в симуляции"""
    
    time: float
    event_type: EventType
    entity_id: str
    data: Optional[Any] = None
    priority: int = 0
    
    def __lt__(self, other: "Event") -> bool:
        """Сравнение для приоритетной очереди"""
        if self.time != other.time:
            return self.time < other.time
        return self.priority < other.priority
    
    def __eq__(self, other: "Event") -> bool:
        """Проверка равенства"""
        return self.time == other.time and self.event_type == other.event_type
    
    def __repr__(self) -> str:
        return (
            f"Event(time={self.time}, type={self.event_type.value}, "
            f"entity={self.entity_id})"
        )
