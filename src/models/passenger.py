"""
Модель пассажира с поддержкой контрольных пунктов
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict


class PassengerStatus(Enum):
    """Статус пассажира"""
    ENTERED = "entered"
    IN_LUGGAGE_QUEUE = "in_luggage_queue"
    LUGGAGE_PASSED = "luggage_passed"
    IN_SECURITY_QUEUE = "in_security_queue"
    SECURITY_PASSED = "security_passed"
    IN_BOARDING_QUEUE = "in_boarding_queue"
    BOARDED = "boarded"
    DEPARTED = "departed"
    MISSED_FLIGHT = "missed_flight"


class PassengerType(Enum):
    """Тип пассажира"""
    ECONOMY = "economy"
    BUSINESS = "business"
    VIP = "vip"


class PassengerClass(Enum):
    """Класс пассажира (интегрировано из Airport-Simulation.py-master)"""
    FIRST_CLASS = "first_class"
    COACH = "coach"


class PriorityMode(Enum):
    """Режим приоритета в очереди"""
    FIRST_COME_FIRST_SERVE = "fcfs"      # Обычная очередь
    FIRST_FLY_FIRST_SERVE = "fffs"       # По времени вылета
    VIP_SKIP_SECURITY = "vip_skip"       # VIP пропускают


@dataclass
class TimeLog:
    """Логирование времени прохождения пассажира"""
    entry_time: float = 0.0
    luggage_time: Optional[float] = None
    security_time: Optional[float] = None
    boarding_time: Optional[float] = None
    departure_time: Optional[float] = None


@dataclass
class Passenger:
    """Модель пассажира с отслеживанием контрольных пунктов"""
    
    passenger_id: str
    flight_id: str
    entry_time: float = 0.0
    flight_time: float = 0.0  # Время вылета самолета
    luggage_wait_time: float = 10.0  # Время прохождения багажного контроля
    security_wait_time: float = 15.0  # Время прохождения паспортного контроля
    
    passenger_type: PassengerType = PassengerType.ECONOMY
    passenger_class: PassengerClass = PassengerClass.COACH  # NEW: интегрировано
    status: PassengerStatus = PassengerStatus.ENTERED
    has_baggage: bool = True
    is_vip: bool = False
    
    # Логирование времени
    time_log: TimeLog = field(default_factory=TimeLog)
    skipped_luggage: bool = False
    skipped_security: bool = False
    missed_flight: bool = False
    
    # Дополнительно
    baggage_count: int = 1
    boarding_time: Optional[float] = None
    departure_time: Optional[float] = None
    
    def __post_init__(self):
        """Инициализация после создания"""
        self.time_log.entry_time = self.entry_time
        if self.passenger_type == PassengerType.VIP:
            self.is_vip = True
    
    def get_waited_time(self) -> float:
        """Получить общее время ожидания пассажира"""
        total = 0.0
        if self.time_log.luggage_time and self.time_log.entry_time:
            total += self.time_log.luggage_time - self.time_log.entry_time
        if self.time_log.security_time and self.time_log.luggage_time:
            total += self.time_log.security_time - self.time_log.luggage_time
        return total
    
    def check_missed_flight(self) -> bool:
        """Проверить, пропустил ли пассажир вылет"""
        if self.time_log.boarding_time and self.time_log.boarding_time > self.flight_time:
            self.missed_flight = True
            return True
        return False
    
    def __repr__(self) -> str:
        vip_mark = "👑 " if self.is_vip else ""
        return (
            f"{vip_mark}Pass({self.passenger_id}, "
            f"flight={self.flight_id}, status={self.status.value})"
        )
