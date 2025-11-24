#!/usr/bin/env python3
"""
Пример использования AeroSim EDU с поддержкой пассажиров
Демонстрирует:
- Симуляцию потока пассажиров через терминал
- Багажный и паспортный контроль
- Системы приоритета (FCFS, FFFS, VIP)
- Отслеживание времени прохождения пассажиров
"""

import sys
import time
from datetime import datetime

# Добавить src в path
sys.path.insert(0, '/home/danayer/Документы/AeroSim EDU')

from src.core.simulator import AirportSimulator
from src.models.passenger import Passenger, PassengerType, PriorityMode
from src.core.event import Event, EventType
from src.utils.logger import get_logger


def create_test_passengers(start_time: float = 0.0) -> list:
    """Создать тестовых пассажиров"""
    passengers = []
    
    # Обычные пассажиры
    for i in range(5):
        p = Passenger(
            passenger_id=f"P{i+1:03d}",
            flight_id=f"FL{i%3+1:03d}",
            entry_time=start_time + i * 5,
            flight_time=start_time + 120,  # Вылет через 2 минуты
            luggage_wait_time=10.0,
            security_wait_time=15.0,
            passenger_type=PassengerType.ECONOMY,
            has_baggage=True
        )
        passengers.append(p)
    
    # VIP пассажиры
    for i in range(2):
        p = Passenger(
            passenger_id=f"VIP{i+1:03d}",
            flight_id=f"FL{i%3+1:03d}",
            entry_time=start_time + 30 + i * 5,
            flight_time=start_time + 120,
            luggage_wait_time=5.0,
            security_wait_time=0.0,  # Пропускают безопасность
            passenger_type=PassengerType.VIP,
            has_baggage=True,
            is_vip=True
        )
        passengers.append(p)
    
    return passengers


def example_fcfs():
    """Пример: FIRST COME FIRST SERVE (обычная очередь)"""
    print("\n" + "="*60)
    print("ПРИМЕР 1: FIRST COME FIRST SERVE (FCFS)")
    print("="*60)
    print("Режим: обычная FIFO очередь")
    print("Ожидаемое поведение: пассажиры проходят в порядке прихода")
    print()
    
    config = {
        "duration": 600,
        "enable_incidents": False,
        "terminal_id": "T1_FCFS",
        "luggage_workers": 2,
        "security_workers": 3,
        "priority_mode": "fcfs",  # FIRST COME FIRST SERVE
        "online_ticketing": False
    }
    
    simulator = AirportSimulator(config)
    
    # Добавить пассажиров
    passengers = create_test_passengers(start_time=0)
    for p in passengers:
        event = Event(
            time=p.entry_time,
            event_type=EventType.PASSENGER_ENTRY,
            entity_id=p.passenger_id,
            data={"passenger": p}
        )
        simulator.event_queue.push(event)
    
    print(f"Создано пассажиров: {len(passengers)}")
    print(f"Режим приоритета: {simulator.terminal.priority_mode.value}")
    print(f"Рабочих в багажном контроле: {simulator.terminal.luggage_control.worker_count}")
    print(f"Рабочих в паспортном контроле: {simulator.terminal.security_control.worker_count}")
    print()
    
    # Обработать несколько событий
    for i in range(20):
        if not simulator.event_queue.is_empty():
            event = simulator.event_queue.pop()
            if event and event.time <= 150:
                simulator.process_event(event)
    
    # Вывести статистику терминала
    term_stats = simulator.terminal.get_statistics()
    print(f"\nОбработано пассажиров: {term_stats['total_passengers']}")
    print(f"Посадили на борт: {term_stats['boarded']}")
    print(f"Пропустили вылет: {term_stats['missed_flights']}")
    print(f"Среднее время ожидания: {term_stats['avg_wait_time']:.1f}s")


def example_fffs():
    """Пример: FIRST FLY FIRST SERVE (по времени вылета)"""
    print("\n" + "="*60)
    print("ПРИМЕР 2: FIRST FLY FIRST SERVE (FFFS)")
    print("="*60)
    print("Режим: приоритет по времени вылета")
    print("Ожидаемое поведение: пассажиры с близким вылетом проходят в приоритете")
    print()
    
    config = {
        "duration": 600,
        "enable_incidents": False,
        "terminal_id": "T1_FFFS",
        "luggage_workers": 2,
        "security_workers": 3,
        "priority_mode": "fffs",  # FIRST FLY FIRST SERVE
        "online_ticketing": False
    }
    
    simulator = AirportSimulator(config)
    
    # Создать пассажиров с разными временами вылета
    passengers = []
    base_time = 0
    
    # Группа 1: вылет в 300s
    for i in range(3):
        p = Passenger(
            passenger_id=f"A{i+1:03d}",
            flight_id="FL1",
            entry_time=base_time + i * 2,
            flight_time=base_time + 300,
            luggage_wait_time=10.0,
            security_wait_time=15.0,
            passenger_type=PassengerType.ECONOMY,
            has_baggage=True
        )
        passengers.append(p)
    
    # Группа 2: вылет в 600s (позже)
    for i in range(3):
        p = Passenger(
            passenger_id=f"B{i+1:03d}",
            flight_id="FL2",
            entry_time=base_time + 100 + i * 2,
            flight_time=base_time + 600,
            luggage_wait_time=10.0,
            security_wait_time=15.0,
            passenger_type=PassengerType.ECONOMY,
            has_baggage=True
        )
        passengers.append(p)
    
    for p in passengers:
        event = Event(
            time=p.entry_time,
            event_type=EventType.PASSENGER_ENTRY,
            entity_id=p.passenger_id,
            data={"passenger": p}
        )
        simulator.event_queue.push(event)
    
    print(f"Создано пассажиров: {len(passengers)}")
    print(f"Группа A: 3 пассажира, вылет в 300s")
    print(f"Группа B: 3 пассажира, вылет в 600s")
    print(f"Режим приоритета: {simulator.terminal.priority_mode.value}")
    print()
    
    # Обработать события
    for i in range(30):
        if not simulator.event_queue.is_empty():
            event = simulator.event_queue.pop()
            if event and event.time <= 300:
                simulator.process_event(event)
    
    # Вывести статистику
    term_stats = simulator.terminal.get_statistics()
    print(f"\nПосадили на борт: {term_stats['boarded']}")
    print(f"Пропустили вылет: {term_stats['missed_flights']}")
    print(f"Среднее время ожидания: {term_stats['avg_wait_time']:.1f}s")


def example_vip():
    """Пример: VIP пассажиры пропускают безопасность"""
    print("\n" + "="*60)
    print("ПРИМЕР 3: VIP ПРИОРИТЕТ")
    print("="*60)
    print("VIP пассажиры пропускают паспортный контроль")
    print()
    
    config = {
        "duration": 600,
        "enable_incidents": False,
        "terminal_id": "T1_VIP",
        "luggage_workers": 2,
        "security_workers": 3,
        "priority_mode": "fcfs",
        "online_ticketing": False
    }
    
    simulator = AirportSimulator(config)
    
    passengers = []
    
    # Обычные пассажиры
    for i in range(3):
        p = Passenger(
            passenger_id=f"ECO{i+1:03d}",
            flight_id="FL1",
            entry_time=0 + i * 1,
            flight_time=120,
            luggage_wait_time=10.0,
            security_wait_time=15.0,
            passenger_type=PassengerType.ECONOMY,
            has_baggage=True,
            is_vip=False
        )
        passengers.append(p)
    
    # VIP пассажиры
    for i in range(2):
        p = Passenger(
            passenger_id=f"VIP{i+1:03d}",
            flight_id="FL1",
            entry_time=2 + i * 1,
            flight_time=120,
            luggage_wait_time=10.0,
            security_wait_time=0.0,  # Пропускают
            passenger_type=PassengerType.VIP,
            has_baggage=True,
            is_vip=True
        )
        passengers.append(p)
    
    for p in passengers:
        event = Event(
            time=p.entry_time,
            event_type=EventType.PASSENGER_ENTRY,
            entity_id=p.passenger_id,
            data={"passenger": p}
        )
        simulator.event_queue.push(event)
    
    print(f"Обычных пассажиров: 3")
    print(f"VIP пассажиров: 2")
    print(f"VIP пропускают паспортный контроль (security_wait_time=0)")
    print()
    
    # Обработать события
    for i in range(25):
        if not simulator.event_queue.is_empty():
            event = simulator.event_queue.pop()
            if event and event.time <= 150:
                simulator.process_event(event)
    
    # Вывести статистику
    term_stats = simulator.terminal.get_statistics()
    print(f"\nПосадили на борт: {term_stats['boarded']}")
    print(f"Среднее время ожидания: {term_stats['avg_wait_time']:.1f}s")


def example_online_ticketing():
    """Пример: онлайн регистрация (без багажа)"""
    print("\n" + "="*60)
    print("ПРИМЕР 4: ОНЛАЙН РЕГИСТРАЦИЯ")
    print("="*60)
    print("Пассажиры без багажа пропускают багажный контроль")
    print()
    
    config = {
        "duration": 600,
        "enable_incidents": False,
        "terminal_id": "T1_ONLINE",
        "luggage_workers": 2,
        "security_workers": 3,
        "priority_mode": "fcfs",
        "online_ticketing": True  # Включить онлайн регистрацию
    }
    
    simulator = AirportSimulator(config)
    
    passengers = []
    
    # С багажом
    for i in range(3):
        p = Passenger(
            passenger_id=f"BAG{i+1:03d}",
            flight_id="FL1",
            entry_time=0 + i * 1,
            flight_time=120,
            luggage_wait_time=10.0,
            security_wait_time=15.0,
            has_baggage=True
        )
        passengers.append(p)
    
    # Без багажа (пропускают багажный контроль)
    for i in range(3):
        p = Passenger(
            passenger_id=f"NOBAG{i+1:03d}",
            flight_id="FL1",
            entry_time=2 + i * 1,
            flight_time=120,
            luggage_wait_time=0.0,  # Не нужен
            security_wait_time=15.0,
            has_baggage=False
        )
        passengers.append(p)
    
    for p in passengers:
        event = Event(
            time=p.entry_time,
            event_type=EventType.PASSENGER_ENTRY,
            entity_id=p.passenger_id,
            data={"passenger": p}
        )
        simulator.event_queue.push(event)
    
    print(f"Пассажиров с багажом: 3")
    print(f"Пассажиров без багажа: 3 (пропускают багажный контроль)")
    print()
    
    # Обработать события
    for i in range(25):
        if not simulator.event_queue.is_empty():
            event = simulator.event_queue.pop()
            if event and event.time <= 150:
                simulator.process_event(event)
    
    # Вывести статистику
    term_stats = simulator.terminal.get_statistics()
    print(f"\nПосадили на борт: {term_stats['boarded']}")
    print(f"Среднее время ожидания: {term_stats['avg_wait_time']:.1f}s")


if __name__ == "__main__":
    logger = get_logger(__name__)
    
    print("\n" + "="*60)
    print("AeroSim EDU - Примеры симуляции пассажиров")
    print("Интеграция логики из airport-simulation-master")
    print("="*60)
    
    try:
        example_fcfs()
        example_fffs()
        example_vip()
        example_online_ticketing()
        
        print("\n" + "="*60)
        print("✓ Все примеры выполнены успешно!")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        sys.exit(1)
