"""
Расширенная статистика симуляции
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class SimulationStatistics:
    """Расширенная статистика симуляции"""
    
    # Основные метрики
    total_events_processed: int = 0
    simulation_time: float = 0.0
    total_aircraft: int = 0
    total_passengers: int = 0
    total_delays: float = 0.0
    
    # Метрики ВПП
    runway_landings: int = 0
    runway_takeoffs: int = 0
    average_runway_wait_time: float = 0.0
    
    # Метрики гейтов
    total_gates: int = 0
    busy_gates: int = 0
    average_gate_occupancy: float = 0.0
    
    # Метрики пассажиров
    average_passenger_wait_time: float = 0.0
    total_baggage_processed: int = 0
    average_baggage_processing_time: float = 0.0
    
    # Метрики задержек
    delayed_flights: int = 0
    average_flight_delay: float = 0.0
    max_flight_delay: float = 0.0
    
    # Метрики использования ресурсов
    runway_utilization_percent: float = 0.0
    gate_utilization_percent: float = 0.0
    terminal_capacity_used_percent: float = 0.0
    
    # Распределение событий
    events_by_type: Dict[str, int] = field(default_factory=dict)
    aircraft_by_status: Dict[str, int] = field(default_factory=dict)
    passenger_by_status: Dict[str, int] = field(default_factory=dict)
    
    # Временные метрики
    peak_passenger_count: int = 0
    peak_time: float = 0.0
    average_passengers_per_hour: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            'total_events_processed': self.total_events_processed,
            'simulation_time': self.simulation_time,
            'total_aircraft': self.total_aircraft,
            'total_passengers': self.total_passengers,
            'total_delays': self.total_delays,
            'runway_landings': self.runway_landings,
            'runway_takeoffs': self.runway_takeoffs,
            'average_runway_wait_time': self.average_runway_wait_time,
            'total_gates': self.total_gates,
            'busy_gates': self.busy_gates,
            'average_gate_occupancy': self.average_gate_occupancy,
            'average_passenger_wait_time': self.average_passenger_wait_time,
            'total_baggage_processed': self.total_baggage_processed,
            'average_baggage_processing_time': self.average_baggage_processing_time,
            'delayed_flights': self.delayed_flights,
            'average_flight_delay': self.average_flight_delay,
            'max_flight_delay': self.max_flight_delay,
            'runway_utilization_percent': self.runway_utilization_percent,
            'gate_utilization_percent': self.gate_utilization_percent,
            'terminal_capacity_used_percent': self.terminal_capacity_used_percent,
            'peak_passenger_count': self.peak_passenger_count,
            'peak_time': self.peak_time,
            'average_passengers_per_hour': self.average_passengers_per_hour,
        }
    
    def get_summary(self) -> str:
        """Получить текстовую сводку"""
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║           РАСШИРЕННАЯ СТАТИСТИКА СИМУЛЯЦИИ                  ║
╚══════════════════════════════════════════════════════════════╝

📊 ОСНОВНЫЕ МЕТРИКИ
─────────────────────────────────────────────────────────────
Время симуляции: {self.simulation_time:.1f} сек
Обработано событий: {self.total_events_processed}
Всего самолетов: {self.total_aircraft}
Всего пассажиров: {self.total_passengers}
Общих задержек: {self.total_delays:.1f} мин

✈️  ВПП (ВЗЛЕТНО-ПОСАДОЧНЫЕ ПОЛОСЫ)
─────────────────────────────────────────────────────────────
Посадок: {self.runway_landings}
Взлетов: {self.runway_takeoffs}
Среднее время ожидания: {self.average_runway_wait_time:.1f} мин
Использование: {self.runway_utilization_percent:.1f}%

🚪 ГЕЙТЫ (ПАРКОВОЧНЫЕ ПОЗИЦИИ)
─────────────────────────────────────────────────────────────
Всего гейтов: {self.total_gates}
Занято гейтов: {self.busy_gates}
Среднее занятие: {self.average_gate_occupancy:.1f}%
Использование: {self.gate_utilization_percent:.1f}%

👥 ПАССАЖИРЫ
─────────────────────────────────────────────────────────────
Среднее время ожидания: {self.average_passenger_wait_time:.1f} мин
Максимум одновременно: {self.peak_passenger_count}
Среднее в час: {self.average_passengers_per_hour:.0f}

📦 БАГАЖ И ГРУЗЫ
─────────────────────────────────────────────────────────────
Обработано багажа: {self.total_baggage_processed}
Среднее время обработки: {self.average_baggage_processing_time:.1f} мин

⏱️  ЗАДЕРЖКИ
─────────────────────────────────────────────────────────────
Задержанных рейсов: {self.delayed_flights}
Средняя задержка: {self.average_flight_delay:.1f} мин
Максимальная задержка: {self.max_flight_delay:.1f} мин

📈 ИСПОЛЬЗОВАНИЕ РЕСУРСОВ
─────────────────────────────────────────────────────────────
ВПП: {self.runway_utilization_percent:.1f}%
Гейты: {self.gate_utilization_percent:.1f}%
Терминальная вместимость: {self.terminal_capacity_used_percent:.1f}%

"""
        return summary


class StatisticsCollector:
    """Сборщик статистики во время симуляции"""
    
    def __init__(self):
        self.stats = SimulationStatistics()
        self.event_log: List[Dict] = []
        self.time_series: Dict[str, List] = defaultdict(list)
    
    def log_event(self, time: float, event_type: str, data: Dict = None):
        """Записать событие"""
        self.event_log.append({
            'time': time,
            'type': event_type,
            'data': data or {}
        })
    
    def add_flight_delay(self, delay_minutes: float):
        """Добавить задержку рейса"""
        self.stats.total_delays += delay_minutes
        self.stats.delayed_flights += 1
        if delay_minutes > self.stats.max_flight_delay:
            self.stats.max_flight_delay = delay_minutes
    
    def add_passenger_wait_time(self, wait_minutes: float):
        """Добавить время ожидания пассажира"""
        if self.stats.total_passengers > 0:
            self.stats.average_passenger_wait_time = (
                (self.stats.average_passenger_wait_time * (self.stats.total_passengers - 1) + wait_minutes)
                / self.stats.total_passengers
            )
    
    def calculate_final_statistics(self) -> SimulationStatistics:
        """Рассчитать финальную статистику"""
        
        # Рассчитать средние значения
        if self.stats.delayed_flights > 0:
            self.stats.average_flight_delay = self.stats.total_delays / self.stats.delayed_flights
        
        return self.stats
    
    def get_statistics_dict(self) -> Dict[str, Any]:
        """Получить статистику как словарь"""
        return self.stats.to_dict()
