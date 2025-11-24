"""
Модель гейта в аэропорту
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class GateStatus(Enum):
    """Статус гейта"""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"


@dataclass
class Gate:
    """Гейт в терминале"""
    
    gate_id: str
    terminal_id: str
    status: GateStatus = GateStatus.AVAILABLE
    current_aircraft: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Gate({self.gate_id}, {self.terminal_id}, {self.status.value})"
    
    def is_available(self) -> bool:
        """Проверить доступность гейта"""
        return self.status == GateStatus.AVAILABLE
    
    def occupy(self, aircraft_id: str) -> bool:
        """Занять гейт"""
        if self.is_available():
            self.status = GateStatus.OCCUPIED
            self.current_aircraft = aircraft_id
            return True
        return False
    
    def release(self) -> None:
        """Освободить гейт"""
        self.status = GateStatus.AVAILABLE
        self.current_aircraft = None
