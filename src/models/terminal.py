"""
Модель терминала аэропорта с контрольными пунктами
Управляет потоком пассажиров через:
- Багажный контроль (Luggage Control Point)
- Паспортный контроль (Security Control Point)
- Посадка на борт (Boarding)
"""

from typing import List, Optional, Tuple
from .passenger import Passenger, PassengerStatus, PriorityMode
from .control_point import ControlPoint
from .passenger_queue import PassengerQueue


class Terminal:
    """
    Терминал аэропорта с полным потоком пассажиров
    Реализует логику из airport-simulation проекта
    """
    
    def __init__(
        self,
        terminal_id: str = "T1",
        luggage_workers: int = 2,
        security_workers: int = 3,
        priority_mode: PriorityMode = PriorityMode.FIRST_COME_FIRST_SERVE,
        online_ticketing_enabled: bool = False
    ):
        """
        Инициализация терминала
        
        Args:
            terminal_id: ID терминала
            luggage_workers: Количество работников в багажном контроле
            security_workers: Количество работников в паспортном контроле
            priority_mode: Режим приоритета в очередях
            online_ticketing_enabled: Пассажиры без багажа пропускают багажный контроль
        """
        self.terminal_id = terminal_id
        self.priority_mode = priority_mode
        self.online_ticketing_enabled = online_ticketing_enabled
        
        # Контрольные пункты
        self.luggage_control = ControlPoint(luggage_workers)
        self.security_control = ControlPoint(security_workers)
        
        # Очереди
        self.luggage_queue = PassengerQueue(priority_mode)
        self.security_queue = PassengerQueue(priority_mode)
        self.boarding_queue = PassengerQueue(priority_mode)
        
        # Статистика
        self.stats = {
            "total_passengers": 0,
            "passed_luggage": 0,
            "passed_security": 0,
            "boarded": 0,
            "missed_flights": 0,
            "total_wait_time": 0.0,
            "avg_wait_time": 0.0,
        }
    
    def can_skip_luggage_control(self, passenger: Passenger) -> bool:
        """
        Может ли пассажир пропустить багажный контроль?
        (online ticketing + нет багажа)
        
        Args:
            passenger: Пассажир
            
        Returns:
            True если может пропустить
        """
        return self.online_ticketing_enabled and not passenger.has_baggage
    
    def can_skip_security_control(self, passenger: Passenger) -> bool:
        """
        Может ли пассажир пропустить паспортный контроль?
        (VIP пассажир)
        
        Args:
            passenger: Пассажир
            
        Returns:
            True если может пропустить
        """
        return passenger.is_vip
    
    def process_passenger_entry(
        self,
        passenger: Passenger,
        current_time: float
    ) -> List[Tuple[str, float, Passenger]]:
        """
        Обработать входящего пассажира
        Возвращает события (type, time, passenger)
        
        Args:
            passenger: Входящий пассажир
            current_time: Текущее время симуляции
            
        Returns:
            Список событий для добавления в очередь
        """
        events = []
        passenger.status = PassengerStatus.ENTERED
        passenger.time_log.entry_time = current_time
        
        # Проверить, может ли пропустить багажный контроль
        if self.can_skip_luggage_control(passenger):
            passenger.skipped_luggage = True
            events.append(("passenger_luggage_passed", current_time, passenger))
        else:
            # Проверить доступность baggage counter
            if self.luggage_control.is_busy():
                # Добавить в очередь
                self.luggage_queue.push(passenger)
                passenger.status = PassengerStatus.IN_LUGGAGE_QUEUE
            else:
                # Немедленно обработать
                self.luggage_control.occupy_worker()
                events.append((
                    "passenger_luggage_passed",
                    current_time + passenger.luggage_wait_time,
                    passenger
                ))
        
        return events
    
    def process_luggage_passed(
        self,
        passenger: Passenger,
        current_time: float
    ) -> List[Tuple[str, float, Passenger]]:
        """
        Пассажир прошел багажный контроль
        
        Args:
            passenger: Пассажир
            current_time: Текущее время симуляции
            
        Returns:
            Список событий
        """
        events = []
        
        # Освободить работника если не пропускал
        if not passenger.skipped_luggage:
            self.luggage_control.release_worker()
            # Обработать следующего в очереди
            next_passenger = self.luggage_queue.pop()
            if next_passenger:
                self.luggage_control.occupy_worker()
                events.append((
                    "passenger_luggage_passed",
                    current_time + next_passenger.luggage_wait_time,
                    next_passenger
                ))
        
        passenger.status = PassengerStatus.LUGGAGE_PASSED
        passenger.time_log.luggage_time = current_time
        
        # Проверить, может ли пропустить паспортный контроль
        if self.can_skip_security_control(passenger):
            passenger.skipped_security = True
            events.append(("passenger_security_passed", current_time, passenger))
        else:
            # Проверить доступность security counter
            if self.security_control.is_busy():
                self.security_queue.push(passenger)
                passenger.status = PassengerStatus.IN_SECURITY_QUEUE
            else:
                self.security_control.occupy_worker()
                events.append((
                    "passenger_security_passed",
                    current_time + passenger.security_wait_time,
                    passenger
                ))
        
        return events
    
    def process_security_passed(
        self,
        passenger: Passenger,
        current_time: float
    ) -> List[Tuple[str, float, Passenger]]:
        """
        Пассажир прошел паспортный контроль
        
        Args:
            passenger: Пассажир
            current_time: Текущее время симуляции
            
        Returns:
            Список событий
        """
        events = []
        
        # Освободить работника если не пропускал
        if not passenger.skipped_security:
            self.security_control.release_worker()
            # Обработать следующего в очереди
            next_passenger = self.security_queue.pop()
            if next_passenger:
                self.security_control.occupy_worker()
                events.append((
                    "passenger_security_passed",
                    current_time + next_passenger.security_wait_time,
                    next_passenger
                ))
        
        passenger.status = PassengerStatus.SECURITY_PASSED
        passenger.time_log.security_time = current_time
        
        # Отправить на посадку
        events.append(("passenger_boarding", current_time, passenger))
        
        return events
    
    def process_boarding(
        self,
        passenger: Passenger,
        current_time: float
    ) -> List[Tuple[str, float, Passenger]]:
        """
        Посадка пассажира на борт
        
        Args:
            passenger: Пассажир
            current_time: Текущее время симуляции
            
        Returns:
            Список событий
        """
        passenger.status = PassengerStatus.BOARDED
        passenger.time_log.boarding_time = current_time
        passenger.boarding_time = current_time
        
        # Обновить статистику
        self.stats["boarded"] += 1
        wait_time = passenger.get_waited_time()
        self.stats["total_wait_time"] += wait_time
        
        # Проверить, не пропустил ли вылет
        if current_time > passenger.flight_time:
            self.stats["missed_flights"] += 1
            passenger.missed_flight = True
        
        return []
    
    def get_statistics(self) -> dict:
        """
        Получить статистику терминала
        
        Returns:
            Словарь со статистикой
        """
        stats = self.stats.copy()
        if stats["total_passengers"] > 0:
            stats["avg_wait_time"] = stats["total_wait_time"] / stats["total_passengers"]
            stats["missed_flight_percent"] = (stats["missed_flights"] / stats["total_passengers"]) * 100
        return stats
    
    def reset(self) -> None:
        """Сбросить состояние терминала"""
        self.luggage_control.reset()
        self.security_control.reset()
        self.luggage_queue.clear()
        self.security_queue.clear()
        self.boarding_queue.clear()
        self.stats = {
            "total_passengers": 0,
            "passed_luggage": 0,
            "passed_security": 0,
            "boarded": 0,
            "missed_flights": 0,
            "total_wait_time": 0.0,
            "avg_wait_time": 0.0,
        }
    
    def __repr__(self) -> str:
        return (
            f"Terminal({self.terminal_id}, "
            f"luggage={self.luggage_control}, "
            f"security={self.security_control})"
        )
