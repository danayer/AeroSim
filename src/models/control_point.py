"""
Модель контрольной точки (багажный контроль, паспортный контроль)
"""

from typing import Optional


class ControlPoint:
    """
    Контрольная точка с ограниченным количеством работников
    (как в airport-simulation: Luggage Control, Security Control)
    """
    
    def __init__(self, worker_count: int = 1):
        """
        Инициализация контрольной точки
        
        Args:
            worker_count: Количество работников (counters)
        """
        self.worker_count = worker_count
        self.busy_workers = 0
    
    def is_busy(self) -> bool:
        """Проверить, заняты ли все работники"""
        return self.busy_workers >= self.worker_count
    
    def occupy_worker(self) -> bool:
        """
        Занять одного работника
        
        Returns:
            True если удалось занять, False если все заняты
        """
        if self.is_busy():
            return False
        self.busy_workers += 1
        return True
    
    def release_worker(self) -> bool:
        """
        Освободить одного работника
        
        Returns:
            True если была освобождена, False если уже свободны
        """
        if self.busy_workers == 0:
            return False
        self.busy_workers -= 1
        return True
    
    def get_utilization(self) -> float:
        """
        Получить процент использования
        
        Returns:
            Процент занятости (0-100)
        """
        if self.worker_count == 0:
            return 0.0
        return (self.busy_workers / self.worker_count) * 100.0
    
    def reset(self) -> None:
        """Сбросить состояние (все работники свободны)"""
        self.busy_workers = 0
    
    def __repr__(self) -> str:
        return (
            f"ControlPoint(workers={self.worker_count}, "
            f"busy={self.busy_workers}, util={self.get_utilization():.1f}%)"
        )
