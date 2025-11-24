"""
Модель взлетно-посадочной полосы
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class RunwayStatus(Enum):
    """Статус ВПП"""
    FREE = "free"
    OCCUPIED_LANDING = "occupied_landing"
    OCCUPIED_TAKEOFF = "occupied_takeoff"
    MAINTENANCE = "maintenance"


@dataclass
class Runway:
    """Взлетно-посадочная полоса"""
    
    runway_id: str
    status: RunwayStatus = RunwayStatus.FREE
    current_aircraft: Optional[str] = None
    total_landings: int = 0
    total_takeoffs: int = 0
    maintenance_needed: bool = False
    
    def __repr__(self) -> str:
        return f"Runway({self.runway_id}, status={self.status.value})"
    
    def is_available(self) -> bool:
        """Проверить доступность ВПП"""
        return self.status == RunwayStatus.FREE
    
    def occupy_for_landing(self, aircraft_id: str) -> bool:
        """Занять для посадки"""
        if self.is_available():
            self.status = RunwayStatus.OCCUPIED_LANDING
            self.current_aircraft = aircraft_id
            return True
        return False
    
    def occupy_for_takeoff(self, aircraft_id: str) -> bool:
        """Занять для взлета"""
        if self.is_available():
            self.status = RunwayStatus.OCCUPIED_TAKEOFF
            self.current_aircraft = aircraft_id
            return True
        return False
    
    def release(self) -> None:
        """Освободить ВПП"""
        if self.status == RunwayStatus.OCCUPIED_LANDING:
            self.total_landings += 1
        elif self.status == RunwayStatus.OCCUPIED_TAKEOFF:
            self.total_takeoffs += 1
        
        self.status = RunwayStatus.FREE
        self.current_aircraft = None
