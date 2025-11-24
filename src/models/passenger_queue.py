"""
Менеджер очередей пассажиров с поддержкой приоритетов
Реализует:
- FIRST_COME_FIRST_SERVE (обычная FIFO очередь)
- FIRST_FLY_FIRST_SERVE (приоритет по времени вылета)
- VIP_SKIP_SECURITY (VIP пропускают безопасность)
"""

from typing import Optional, List, Deque
from collections import deque
from enum import Enum

from .passenger import Passenger, PriorityMode


class PassengerQueue:
    """
    Очередь пассажиров с поддержкой приоритетов
    Может работать в режимах FCFS (обычная очередь) или 
    FFFS (приоритет по времени вылета)
    """
    
    def __init__(self, priority_mode: PriorityMode = PriorityMode.FIRST_COME_FIRST_SERVE):
        """
        Инициализация очереди
        
        Args:
            priority_mode: Режим приоритета
        """
        self.priority_mode = priority_mode
        
        # Обычная очередь для FCFS
        self.fifo_queue: Deque[Passenger] = deque()
        
        # Приоритетная очередь для FFFS (сортируется по flight_time)
        self.priority_queue: List[Passenger] = []
        
        self.total_entered = 0
    
    def push(self, passenger: Passenger) -> None:
        """
        Добавить пассажира в очередь
        
        Args:
            passenger: Пассажир для добавления
        """
        self.total_entered += 1
        
        if self.priority_mode == PriorityMode.FIRST_FLY_FIRST_SERVE:
            # Добавить в приоритетную очередь и отсортировать
            self.priority_queue.append(passenger)
            # Сортировать по flight_time (раньше вылет = выше приоритет)
            self.priority_queue.sort(key=lambda p: (p.flight_time, self.total_entered))
        else:
            # Обычная FIFO очередь
            self.fifo_queue.append(passenger)
    
    def pop(self) -> Optional[Passenger]:
        """
        Вытащить пассажира из очереди (с учетом приоритета)
        
        Returns:
            Пассажир или None если очередь пуста
        """
        if self.priority_mode == PriorityMode.FIRST_FLY_FIRST_SERVE:
            if self.priority_queue:
                return self.priority_queue.pop(0)
        else:
            if self.fifo_queue:
                return self.fifo_queue.popleft()
        
        return None
    
    def is_empty(self) -> bool:
        """Проверить, пуста ли очередь"""
        if self.priority_mode == PriorityMode.FIRST_FLY_FIRST_SERVE:
            return len(self.priority_queue) == 0
        else:
            return len(self.fifo_queue) == 0
    
    def size(self) -> int:
        """Получить размер очереди"""
        if self.priority_mode == PriorityMode.FIRST_FLY_FIRST_SERVE:
            return len(self.priority_queue)
        else:
            return len(self.fifo_queue)
    
    def get_all(self) -> List[Passenger]:
        """Получить всех пассажиров в очереди"""
        if self.priority_mode == PriorityMode.FIRST_FLY_FIRST_SERVE:
            return self.priority_queue.copy()
        else:
            return list(self.fifo_queue)
    
    def clear(self) -> None:
        """Очистить очередь"""
        self.fifo_queue.clear()
        self.priority_queue.clear()
    
    def __repr__(self) -> str:
        return (
            f"PassengerQueue(mode={self.priority_mode.value}, "
            f"size={self.size()})"
        )
