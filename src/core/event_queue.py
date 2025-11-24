"""
Приоритетная очередь событий для DES
"""

import heapq
from typing import List, Optional
from .event import Event, EventType


class EventQueue:
    """Приоритетная очередь для управления событиями в порядке возникновения"""
    
    def __init__(self):
        self._queue: List[Event] = []
        self._processed_count = 0
    
    def push(self, event: Event) -> None:
        """Добавить событие в очередь"""
        heapq.heappush(self._queue, event)
    
    def pop(self) -> Optional[Event]:
        """Извлечь следующее событие"""
        if self._queue:
            self._processed_count += 1
            return heapq.heappop(self._queue)
        return None
    
    def peek(self) -> Optional[Event]:
        """Посмотреть следующее событие без извлечения"""
        if self._queue:
            return self._queue[0]
        return None
    
    def is_empty(self) -> bool:
        """Проверить, пуста ли очередь"""
        return len(self._queue) == 0
    
    def size(self) -> int:
        """Получить размер очереди"""
        return len(self._queue)
    
    def clear(self) -> None:
        """Очистить очередь"""
        self._queue.clear()
    
    def get_processed_count(self) -> int:
        """Получить количество обработанных событий"""
        return self._processed_count
    
    def __repr__(self) -> str:
        return f"EventQueue(size={len(self._queue)})"
