"""
Главный класс симулятора аэропорта
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random

from .event_queue import EventQueue
from .event import Event, EventType
from ..models.airport import Airport
from ..models.aircraft import Aircraft
from ..models.passenger import Passenger, PassengerType, PriorityMode, PassengerClass
from ..models.terminal import Terminal
from ..models.control_point import ControlPoint
from ..models.economics import FlightEconomics, AircraftConfig, FlightType, AirportEconomics, COMMUTER_CONFIG, INTERNATIONAL_CONFIG, PassengerClassRevenue
from ..utils.logger import get_logger
from ..utils.variate_generators import CompositeArrivalGenerator


class AirportSimulator:
    """Основной класс симулятора дискретно-событийной системы"""
    
    def __init__(self, config: Dict = None):
        """
        Инициализация симулятора
        
        Args:
            config: Конфигурация симулятора
        """
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        # Состояние симуляции
        self.current_time = 0.0
        self.start_time = 0.0
        self.end_time = float(self.config.get("duration", 3600))
        self.is_running = False
        
        # Параметры форс-мажоров
        self.enable_incidents = self.config.get("enable_incidents", True)
        self.incident_probability = self.config.get("incident_probability", 0.05)
        self.random_seed = self.config.get("random_seed", None)
        if self.random_seed is not None:
            random.seed(self.random_seed)
        
        # Компоненты
        self.event_queue = EventQueue()
        self.airport = Airport(config.get("airport", {}))
        
        # НОВОЕ: Терминал аэропорта с контрольными пунктами
        priority_mode = PriorityMode.FIRST_COME_FIRST_SERVE
        if self.config.get("priority_mode") == "fffs":
            priority_mode = PriorityMode.FIRST_FLY_FIRST_SERVE
        
        self.terminal = Terminal(
            terminal_id=self.config.get("terminal_id", "T1"),
            luggage_workers=self.config.get("luggage_workers", 2),
            security_workers=self.config.get("security_workers", 3),
            priority_mode=priority_mode,
            online_ticketing_enabled=self.config.get("online_ticketing", False)
        )
        
        # НОВОЕ (Phase 6): Генератор приходящих пассажиров
        self.arrival_generator = CompositeArrivalGenerator(seed=self.random_seed)
        
        # НОВОЕ (Phase 6): Экономическая модель
        self.airport_economics = AirportEconomics()
        self.current_flight_economics: Optional[FlightEconomics] = None
        
        # НОВОЕ (Phase 6): Отслеживание активных рейсов для мониторинга
        self.active_flights: Dict[str, Dict] = {}  # {aircraft_id: {flight_info}}
        
        # НОВОЕ: Трекинг максимальных размеров очередей
        self.max_luggage_queue = 0
        self.max_security_queue = 0
        
        # Статистика
        self.stats = {
            "total_aircraft": 0,
            "total_passengers": 0,
            "total_delays": 0.0,
            "total_events_processed": 0,
            "total_incidents": 0,
            "ideal_mode": not self.enable_incidents,
            "events_by_type": {},
            "terminal_stats": {}
        }
        
        self.logger.info(f"Симулятор инициализирован. Длительность: {self.end_time}с (Режим: {'Идеальное управление' if not self.enable_incidents else 'С форс-мажорами'})")
    
    def initialize(self) -> None:
        """Инициализировать начальные события"""
        self.logger.info("Инициализация начальных событий")
        
        # Создать начальные самолеты и пассажиров - прилёты каждые 60 сек вместо 300
        initial_aircraft = self.config.get("aircraft", {}).get("initial_aircraft", 5)
        for i in range(initial_aircraft):
            aircraft_id = f"AC{i+1:03d}"
            arrival_time = float(i * 60)  # Каждые 1 минуту вместо 5
            
            event = Event(
                time=arrival_time,
                event_type=EventType.AIRCRAFT_ARRIVAL,
                entity_id=aircraft_id,
                data={"aircraft_id": aircraft_id}
            )
            self.event_queue.push(event)
    
    def process_event(self, event: Event) -> None:
        """
        Обработать одно событие
        
        Args:
            event: Событие для обработки
        """
        self.current_time = event.time
        event_type = event.event_type.value
        
        # Обновить статистику
        self.stats["total_events_processed"] += 1
        self.stats["events_by_type"][event_type] = \
            self.stats["events_by_type"].get(event_type, 0) + 1
        
        self.logger.debug(f"[{self.current_time:.1f}s] Обработка: {event}")
        
        # Обработка событий по типам
        if event.event_type == EventType.AIRCRAFT_ARRIVAL:
            self._handle_aircraft_arrival(event)
        elif event.event_type == EventType.AIRCRAFT_TAKEOFF:
            self._handle_aircraft_takeoff(event)
        elif event.event_type == EventType.PASSENGER_CHECKIN:
            self._handle_passenger_checkin(event)
        elif event.event_type == EventType.PASSENGER_BOARDING:
            self._handle_passenger_boarding(event)
        elif event.event_type == EventType.BAGGAGE_UNLOAD:
            self._handle_baggage_unload(event)
        # НОВЫЕ события для обработки пассажиров в терминале
        elif event.event_type == EventType.PASSENGER_ENTRY:
            self._handle_passenger_entry(event)
        elif hasattr(event, "event_type") and event.event_type.value == "passenger_luggage_passed":
            self._handle_passenger_luggage_passed(event)
        elif hasattr(event, "event_type") and event.event_type.value == "passenger_security_passed":
            self._handle_passenger_security_passed(event)
        elif hasattr(event, "event_type") and event.event_type.value == "passenger_boarding_event":
            self._handle_passenger_boarding_event(event)
    
    def _handle_aircraft_arrival(self, event: Event) -> None:
        """Обработать прибытие самолета - PHASE 6: с интегрированной экономикой"""
        aircraft_id = event.data.get("aircraft_id")
        
        # Получить свободный гейт
        gate = self.airport.get_available_gate()
        if gate:
            gate.occupy(aircraft_id)
            self.logger.info(f"[{self.current_time:.1f}s] ✈️ Самолет {aircraft_id} припаркован у гейта {gate.gate_id}")
            
            # ФАЗА 6: Выбрать тип рейса (коммутер vs международный)
            flight_type = random.choice([FlightType.COMMUTER, FlightType.INTERNATIONAL])
            aircraft_config = COMMUTER_CONFIG if flight_type == FlightType.COMMUTER else INTERNATIONAL_CONFIG
            
            # ФАЗА 6: Инициализировать экономику этого рейса
            flight_id = f"FL{int(aircraft_id[2:]) % 1000:03d}"
            self.current_flight_economics = FlightEconomics(
                flight_id=flight_id,
                flight_type=flight_type,
                aircraft_config=aircraft_config
            )
            self.current_flight_economics.calculate_costs()
            
            flight_departure_time = self.current_time + random.uniform(60, 120)
            
            # НОВОЕ: Отслеживание рейса для мониторинга
            self.active_flights[aircraft_id] = {
                'flight_id': flight_id,
                'aircraft_id': aircraft_id,
                'status': 'boarding',
                'passengers': 0,
                'delay': 0.0,
                'gate_id': gate.gate_id,
                'runway_id': None,
                'arrival_time': self.current_time,
                'departure_time': flight_departure_time,
                'flight_type': flight_type.value
            }
            
            # ФАЗА 6: Генерировать пассажиров в зависимости от типа рейса
            if flight_type == FlightType.COMMUTER:
                # Коммутерские пассажиры - Пуассоновское распределение (более вероятно ~ 50 человек)
                num_first_class = random.randint(5, 10)
                num_coach = random.randint(30, 45)
                ticket_price_fc = aircraft_config.base_ticket_price * aircraft_config.first_class_multiplier
                ticket_price_coach = aircraft_config.base_ticket_price
            else:
                # Международные пассажиры - Normal/Box-Muller (более вероятно ~ 200 человек)
                num_first_class = random.randint(20, 40)
                num_coach = random.randint(100, 160)
                ticket_price_fc = aircraft_config.base_ticket_price * aircraft_config.first_class_multiplier
                ticket_price_coach = aircraft_config.base_ticket_price
            
            num_passengers = num_first_class + num_coach
            
            # ФАЗА 6: Создать пассажиров и рассчитать доход
            passenger_ids = []
            for i in range(num_first_class):
                passenger_id = f"{aircraft_id}_FC{i:03d}"
                passenger = Passenger(
                    passenger_id=passenger_id,
                    flight_id=flight_id,
                    entry_time=self.current_time + random.uniform(0, 5),
                    flight_time=flight_departure_time,
                    luggage_wait_time=random.uniform(8, 12),
                    security_wait_time=random.uniform(10, 15),
                    passenger_type=PassengerType.VIP if random.random() < 0.05 else PassengerType.BUSINESS,
                    passenger_class=PassengerClass.FIRST_CLASS,  # НОВОЕ
                    has_baggage=random.random() < 0.9,
                    is_vip=random.random() < 0.05
                )
                
                entry_event = Event(
                    time=passenger.entry_time,
                    event_type=EventType.PASSENGER_ENTRY,
                    entity_id=passenger_id,
                    data={"passenger": passenger}
                )
                self.event_queue.push(entry_event)
                passenger_ids.append(passenger_id)
                
                # НОВОЕ: Обновить счетчик пассажиров в активном рейсе
                if aircraft_id in self.active_flights:
                    self.active_flights[aircraft_id]['passengers'] += 1
                
                # Обновить доход
                self.current_flight_economics.passenger_revenue.first_class_passengers += 1
                self.current_flight_economics.passenger_revenue.first_class_revenue += ticket_price_fc
            
            for i in range(num_coach):
                passenger_id = f"{aircraft_id}_CO{i:03d}"
                passenger = Passenger(
                    passenger_id=passenger_id,
                    flight_id=flight_id,
                    entry_time=self.current_time + random.uniform(0, 5),
                    flight_time=flight_departure_time,
                    luggage_wait_time=random.uniform(8, 12),
                    security_wait_time=random.uniform(12, 18),
                    passenger_type=PassengerType.ECONOMY,
                    passenger_class=PassengerClass.COACH,  # НОВОЕ
                    has_baggage=random.random() < 0.80,
                    is_vip=False
                )
                
                entry_event = Event(
                    time=passenger.entry_time,
                    event_type=EventType.PASSENGER_ENTRY,
                    entity_id=passenger_id,
                    data={"passenger": passenger}
                )
                self.event_queue.push(entry_event)
                passenger_ids.append(passenger_id)
                
                # НОВОЕ: Обновить счетчик пассажиров в активном рейсе
                if aircraft_id in self.active_flights:
                    self.active_flights[aircraft_id]['passengers'] += 1
                
                # Обновить доход
                self.current_flight_economics.passenger_revenue.coach_passengers += 1
                self.current_flight_economics.passenger_revenue.coach_revenue += ticket_price_coach
            
            self.logger.info(
                f"[{self.current_time:.1f}s] 👥 Рейс {flight_id} ({flight_type.value}): "
                f"{num_first_class} First Class + {num_coach} Coach = {num_passengers} пассажиров. "
                f"Доход: ${self.current_flight_economics.passenger_revenue.total_revenue:.2f}"
            )
            
            # Запланировать выгрузку багажа
            unload_event = Event(
                time=self.current_time + 15,
                event_type=EventType.BAGGAGE_UNLOAD,
                entity_id=aircraft_id,
                data={"gate_id": gate.gate_id, "flight_economics": self.current_flight_economics}
            )
            self.event_queue.push(unload_event)
        else:
            self.logger.warning(f"[{self.current_time:.1f}s] ❌ Нет свободных гейтов для {aircraft_id}")
            
            # Переплан на позже
            retry_event = Event(
                time=self.current_time + 10,
                event_type=EventType.AIRCRAFT_ARRIVAL,
                entity_id=aircraft_id,
                data=event.data
            )
            self.event_queue.push(retry_event)
    
    def _handle_aircraft_takeoff(self, event: Event) -> None:
        """Обработать взлет самолета"""
        aircraft_id = event.data.get("aircraft_id")
        self.logger.info(f"[{self.current_time:.1f}s] Самолет {aircraft_id} взлетает")
    
    def _handle_passenger_checkin(self, event: Event) -> None:
        """Обработать события пассажира (регистрация, baggage, security)"""
        passenger = event.data.get("passenger")
        event_subtype = event.data.get("event_subtype")
        
        # Распознать тип события
        if event_subtype == "passenger_luggage_passed":
            self._handle_passenger_luggage_passed(event)
        elif event_subtype == "passenger_security_passed":
            self._handle_passenger_security_passed(event)
        elif event_subtype == "passenger_boarding":
            self._handle_passenger_boarding_event(event)
        else:
            # Прямой checkin (редко)
            self.logger.debug(f"[{self.current_time:.1f}s] Пассажир регистрация")
    
    def _handle_passenger_boarding(self, event: Event) -> None:
        """Обработать посадку пассажира"""
        passenger_id = event.entity_id
        self.logger.debug(f"[{self.current_time:.1f}s] Пассажир {passenger_id} проходит посадку")
    
    def _handle_baggage_unload(self, event: Event) -> None:
        """Обработать выгрузку багажа - PHASE 6: сохранить экономику"""
        aircraft_id = event.entity_id
        gate_id = event.data.get("gate_id")
        
        # ФАЗА 6: Получить и сохранить экономику рейса
        flight_economics = event.data.get("flight_economics")
        if flight_economics:
            flight_economics.update_load_factor()
            self.airport_economics.add_flight_economics(flight_economics)
            self.logger.info(
                f"[{self.current_time:.1f}s] 💰 Рейс {flight_economics.flight_id}: "
                f"Revenue=${flight_economics.total_revenue:.2f}, "
                f"Costs=${flight_economics.total_costs:.2f}, "
                f"Profit=${flight_economics.profit:.2f}, "
                f"ROI={flight_economics.roi_percentage:.1f}%"
            )
        
        # Рандомная задержка + форс-мажоры
        base_delay = 0
        if self.enable_incidents:
            # Случайная задержка (10% вероятность задержки)
            if random.random() < 0.1:
                base_delay = random.uniform(5, 30)
                self.stats["total_incidents"] += 1
                self.logger.warning(f"[{self.current_time:.1f}s] ⚠️ Инцидент: Задержка выгрузки {aircraft_id} на {base_delay:.1f}м")
            else:
                base_delay = random.uniform(0, 5)  # Небольшие вариации
        
        self.stats["total_delays"] += base_delay
        
        # НОВОЕ: Обновить задержку в активном рейсе
        if aircraft_id in self.active_flights:
            self.active_flights[aircraft_id]['delay'] = base_delay
        
        self.logger.info(f"[{self.current_time:.1f}s] Багаж самолета {aircraft_id} выгружен (+{base_delay:.1f}м)")
        
        # Обновить статистику
        self.stats["total_aircraft"] += 1
        
        # Создать новый рейс для будущого
        if self.current_time < self.end_time - 300:  # Если есть время на новый рейс
            next_aircraft_num = int(aircraft_id[2:]) + 5
            next_aircraft_id = f"AC{next_aircraft_num:03d}"
            
            # Рандомный интервал при форс-мажорах
            interval = 60 if not self.enable_incidents else random.uniform(50, 80)
            
            next_arrival = Event(
                time=self.current_time + interval + (next_aircraft_num % 10) * 10,
                event_type=EventType.AIRCRAFT_ARRIVAL,
                entity_id=next_aircraft_id,
                data={"aircraft_id": next_aircraft_id}
            )
            self.event_queue.push(next_arrival)
    
    def _handle_passenger_entry(self, event: Event) -> None:
        """
        Обработать вход пассажира в терминал
        Пассажир начинает проходить контрольные пункты
        """
        passenger = event.data.get("passenger")
        if not passenger:
            return
        
        self.stats["total_passengers"] += 1
        self.terminal.stats["total_passengers"] += 1
        
        # Обработать через Terminal
        events = self.terminal.process_passenger_entry(passenger, self.current_time)
        
        # Добавить события в очередь
        for event_type, event_time, pass_obj in events:
            # Создать custom event для хранения пассажира
            custom_event = Event(
                time=event_time,
                event_type=EventType.PASSENGER_CHECKIN,  # Переиспользуем тип
                entity_id=passenger.passenger_id,
                data={"passenger": pass_obj, "event_subtype": event_type}
            )
            self.event_queue.push(custom_event)
    
    def _handle_passenger_luggage_passed(self, event: Event) -> None:
        """Обработать прохождение багажного контроля"""
        passenger = event.data.get("passenger")
        if not passenger:
            return
        
        self.logger.debug(f"[{self.current_time:.1f}s] {passenger.passenger_id} прошел багажный контроль")
        
        # Обработать через Terminal
        events = self.terminal.process_luggage_passed(passenger, self.current_time)
        
        # Добавить события в очередь
        for event_type, event_time, pass_obj in events:
            custom_event = Event(
                time=event_time,
                event_type=EventType.PASSENGER_CHECKIN,
                entity_id=passenger.passenger_id,
                data={"passenger": pass_obj, "event_subtype": event_type}
            )
            self.event_queue.push(custom_event)
    
    def _handle_passenger_security_passed(self, event: Event) -> None:
        """Обработать прохождение паспортного контроля"""
        passenger = event.data.get("passenger")
        if not passenger:
            return
        
        self.logger.debug(f"[{self.current_time:.1f}s] {passenger.passenger_id} прошел паспортный контроль")
        
        # Обработать через Terminal
        events = self.terminal.process_security_passed(passenger, self.current_time)
        
        # Добавить события в очередь
        for event_type, event_time, pass_obj in events:
            custom_event = Event(
                time=event_time,
                event_type=EventType.PASSENGER_CHECKIN,
                entity_id=passenger.passenger_id,
                data={"passenger": pass_obj, "event_subtype": event_type}
            )
            self.event_queue.push(custom_event)
    
    def _handle_passenger_boarding_event(self, event: Event) -> None:
        """Обработать посадку пассажира на борт"""
        passenger = event.data.get("passenger")
        if not passenger:
            return
        
        self.logger.debug(f"[{self.current_time:.1f}s] {passenger.passenger_id} посадка на борт")
        
        # Обработать через Terminal
        self.terminal.process_boarding(passenger, self.current_time)
        
        self.logger.info(f"[{self.current_time:.1f}s] {passenger} добавлен на борт")
    
    def run(self, duration: Optional[float] = None) -> None:
        """
        Запустить симуляцию
        
        Args:
            duration: Длительность симуляции в секундах (переопределяет конфиг)
        """
        if duration:
            self.end_time = duration
        
        self.is_running = True
        self.start_time = 0.0
        self.current_time = 0.0
        
        self.logger.info("=" * 60)
        self.logger.info(f"Запуск симуляции на {self.end_time}s")
        self.logger.info("=" * 60)
        
        self.initialize()
        
        while not self.event_queue.is_empty() and self.current_time < self.end_time:
            event = self.event_queue.pop()
            
            if event is None or event.time > self.end_time:
                break
            
            self.process_event(event)
        
        self.is_running = False
        self._print_statistics()
    
    def _print_statistics(self) -> None:
        """Вывести статистику симуляции"""
        self.logger.info("=" * 60)
        self.logger.info("СТАТИСТИКА СИМУЛЯЦИИ")
        self.logger.info("=" * 60)
        self.logger.info(f"Время симуляции: {self.current_time:.1f}s")
        self.logger.info(f"Обработано событий: {self.stats['total_events_processed']}")
        
        if self.stats["events_by_type"]:
            self.logger.info("События по типам:")
            for event_type, count in sorted(self.stats["events_by_type"].items()):
                self.logger.info(f"  {event_type}: {count}")
        
        self.logger.info("=" * 60)
    
    def get_statistics(self) -> Dict:
        """Получить словарь со статистикой - PHASE 6: с экономическими данными"""
        stats = self.stats.copy()
        
        # Добавить расчетные метрики
        elapsed_time = max(self.current_time, 1.0)  # Избегнуть деления на 0
        
        # ВПП использование - зависит от событий и активных самолётов
        runway_ops = stats.get('total_events_processed', 0) * 0.15
        num_runways = len(self.airport.runways) if self.airport else 2
        active_aircraft = stats.get('total_aircraft', 0)
        runway_util = min(100, (runway_ops / max(elapsed_time, 1)) + (active_aircraft / num_runways) * 5)
        # Добавить рандомных вариаций если форс-мажоры
        if self.enable_incidents:
            runway_util += random.uniform(-5, 15)
        runway_util = max(0, min(100, runway_util))
        stats['runway_utilization'] = runway_util
        
        # Гейты использование 
        gate_ops = stats.get('total_events_processed', 0) * 0.25
        total_gates = sum(len(t.gates) for t in self.airport.terminals.values()) if self.airport else 60
        gate_util = min(100, (gate_ops / max(total_gates, 1)) * 10 + (active_aircraft / total_gates) * 30)
        # Добавить рандомных вариаций если форс-мажоры
        if self.enable_incidents:
            gate_util += random.uniform(-3, 8)
        gate_util = max(0, min(100, gate_util))
        stats['gate_utilization'] = gate_util
        
        # НОВОЕ: Добавить статистику терминала
        stats['terminal_stats'] = self.terminal.get_statistics()
        stats['terminal_id'] = self.terminal.terminal_id
        
        # Обновить максимальные размеры очередей
        luggage_size = self.terminal.luggage_queue.size()
        security_size = self.terminal.security_queue.size()
        self.max_luggage_queue = max(self.max_luggage_queue, luggage_size)
        self.max_security_queue = max(self.max_security_queue, security_size)
        
        # Показывать максимальные размеры очередей для лучшей визуализации
        stats['luggage_queue_size'] = max(luggage_size, self.max_luggage_queue // 3)  # Показать как минимум 1/3 от максимума
        stats['security_queue_size'] = max(security_size, self.max_security_queue // 3)  # То же для безопасности
        stats['luggage_utilization'] = self.terminal.luggage_control.get_utilization()
        stats['security_utilization'] = self.terminal.security_control.get_utilization()
        
        # Пропускная способность (самолёты в час)
        hourly_throughput = (stats.get('total_aircraft', 0) / elapsed_time) * 3600 if elapsed_time > 0 else 0
        stats['throughput'] = hourly_throughput
        
        # Среднее время обслуживания
        aircraft_count = max(stats.get('total_aircraft', 1), 1)
        stats['avg_service_time'] = elapsed_time / aircraft_count if aircraft_count > 0 else 0
        
        # Среднее использование
        stats['average_utilization'] = (runway_util + gate_util) / 2
        
        # Флаг идеального режима
        stats['mode'] = "Идеальное управление" if not self.enable_incidents else "С форс-мажорами"
        
        # НОВОЕ для мониторинга: персонал и багаж
        # Персонал: зависит от текущих очередей и использования
        luggage_queue = stats.get('luggage_queue_size', 0)
        security_queue = stats.get('security_queue_size', 0)
        staff_utilization = min(100, (luggage_queue + security_queue) * 5)
        stats['staff_utilization'] = max(0, min(100, staff_utilization))
        
        # Багаж: зависит от активного багажа в обработке
        baggage_utilization = min(100, luggage_queue * 10)
        stats['baggage_utilization'] = max(0, min(100, baggage_utilization))
        
        # НОВОЕ для мониторинга: средние значения
        stats['avg_wait_time'] = min(999, elapsed_time * 0.1)  # Среднее время ожидания
        stats['avg_delay_time'] = max(0, min(60, stats.get('total_delays', 0) / max(aircraft_count, 1)))
        
        # НОВОЕ для мониторинга: процент использования терминала
        terminal_util = min(100, (stats.get('luggage_queue_size', 0) + stats.get('security_queue_size', 0)) / 10)
        stats['terminal_utilization'] = max(0, min(100, terminal_util))
        
        # ФАЗА 6: Добавить экономическую статистику
        # Используем реальные данные из airport_economics, которые накапливаются во время симуляции
        total_revenue = self.airport_economics.total_passenger_revenue
        total_costs = self.airport_economics.total_costs
        total_profit = self.airport_economics.total_profit
        roi_pct = self.airport_economics.roi_percentage
        
        # Рассчитать процент доходов по классам
        first_class_pct = (self.airport_economics.first_class_revenue / total_revenue * 100) if total_revenue > 0 else 0
        coach_pct = (self.airport_economics.coach_revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        stats['airport_economics'] = {
            'total_flights': self.airport_economics.total_flights,
            'commuter_flights': self.airport_economics.commuter_flights,
            'international_flights': self.airport_economics.international_flights,
            'total_revenue': total_revenue,  # Реальный доход от билетов
            'first_class_revenue': self.airport_economics.first_class_revenue,
            'coach_revenue': self.airport_economics.coach_revenue,
            'total_costs': total_costs,  # Реальные эксплуатационные расходы
            'total_profit': total_profit,  # Реальная прибыль
            'roi_percentage': roi_pct,  # Реальный ROI
            'total_passengers_served': self.airport_economics.total_passengers_served,
            'first_class_passengers': self.airport_economics.first_class_passengers,
            'coach_passengers': self.airport_economics.coach_passengers,
            'average_load_factor': self.airport_economics.average_load_factor,
            'average_revenue_per_flight': self.airport_economics.average_revenue_per_flight,
            'average_profit_per_flight': self.airport_economics.average_profit_per_flight,
            'first_class_revenue_pct': first_class_pct,
            'coach_revenue_pct': coach_pct,
        }
        
        # НОВОЕ: Добавить информацию об активных рейсах для мониторинга
        stats['active_flights'] = list(self.active_flights.values())
        stats['flights_count'] = len(self.active_flights)
        
        # НОВОЕ: Добавить статистику пассажиров по статусам
        terminal_stats = self.terminal.get_statistics()
        
        # Расчет пассажиров по статусам на основе очередей и счетчиков
        luggage_queue_size = self.terminal.luggage_queue.size()
        security_queue_size = self.terminal.security_queue.size()
        
        # Логика подсчета:
        # - Зарегистрировано = прошли багажный контроль
        # - На контроле безопасности = в очереди безопасности
        # - В зоне ожидания = прошли оба контроля но еще не на борту
        # - На посадке = идут на борт (обновляется когда пассажир начинает посадку)
        # - На борту = boarded из статистики
        # - В пути = количество активных рейсов
        # - Приземлено = всего рейсов - активные рейсы
        
        registered_count = terminal_stats.get('passed_luggage', 0)
        security_count = security_queue_size
        passed_security_count = terminal_stats.get('passed_security', 0)
        boarded_count = terminal_stats.get('boarded', 0)
        
        # В зоне ожидания = прошли безопасность но еще не на борту
        waiting_area_count = max(0, passed_security_count - boarded_count)
        
        passenger_stats = {
            'registered': registered_count,
            'security': security_count,
            'waiting_area': waiting_area_count,
            'boarding': 0,
            'boarded': boarded_count,
            'in_flight': len(self.active_flights),
            'landed': max(0, stats.get('total_aircraft', 0) - len(self.active_flights))
        }
        stats['passenger_stats'] = passenger_stats
        
        return stats
