"""
Модель аэропорта
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .runway import Runway
from .gate import Gate


@dataclass
class Terminal:
    """Терминал аэропорта"""
    
    terminal_id: str
    gates: List[Gate] = field(default_factory=list)
    capacity: int = 3000  # Пассажиров
    current_passengers: int = 0
    
    def __repr__(self) -> str:
        return f"Terminal({self.terminal_id}, gates={len(self.gates)})"
    
    def get_available_gate(self) -> Optional[Gate]:
        """Получить первый доступный гейт"""
        for gate in self.gates:
            if gate.is_available():
                return gate
        return None


@dataclass
class Airport:
    """Аэропорт"""
    
    airport_id: str = "AIRPORT"
    runways: List[Runway] = field(default_factory=list)
    terminals: Dict[str, Terminal] = field(default_factory=dict)
    
    def __init__(self, config: Dict = None):
        """Инициализация аэропорта"""
        config = config or {}
        self.airport_id = config.get("id", "AIRPORT")
        self.runways = []
        self.terminals = {}
        
        # Создать ВПП
        num_runways = config.get("num_runways", 2)
        for i in range(num_runways):
            runway = Runway(f"RWY{i+1:02d}")
            self.runways.append(runway)
        
        # Создать терминалы
        num_terminals = config.get("num_terminals", 3)
        for i in range(num_terminals):
            terminal_id = f"T{i+1}"
            num_gates = config.get("gates_per_terminal", 20)
            
            gates = [
                Gate(f"{terminal_id}-G{j+1:02d}", terminal_id)
                for j in range(num_gates)
            ]
            
            terminal = Terminal(terminal_id, gates)
            self.terminals[terminal_id] = terminal
    
    def __repr__(self) -> str:
        return (
            f"Airport({self.airport_id}, runways={len(self.runways)}, "
            f"terminals={len(self.terminals)})"
        )
    
    def get_available_gate(self) -> Optional[Gate]:
        """Получить первый доступный гейт в любом терминале"""
        for terminal in self.terminals.values():
            gate = terminal.get_available_gate()
            if gate:
                return gate
        return None
    
    def get_available_runway(self) -> Optional[Runway]:
        """Получить первую доступную ВПП"""
        for runway in self.runways:
            if runway.is_available():
                return runway
        return None
