# 📘 AeroSim EDU - Полная Документация Системы

**Версия:** 1.0.0 (Phase 6 Complete)  
**Дата:** 24 ноября 2025  
**Статус:** ✅ Production Ready

---

## 🎯 Оглавление

1. [Обзор системы](#-обзор-системы)
2. [Архитектура](#-архитектура)
3. [Математические модели и формулы](#-математические-модели-и-формулы)
4. [Компоненты системы](#-компоненты-системы)
5. [Система событий (DES)](#-система-событий-des)
6. [Экономическая модель](#-экономическая-модель)
7. [Алгоритмы и процедуры](#-алгоритмы-и-процедуры)
8. [Использование и примеры](#-использование-и-примеры)
9. [API Справка](#-api-справка)

---

## 🌍 Обзор системы

### Назначение

**AeroSim EDU** — это комплексный **симулятор аэропорта** на основе **дискретно-событийного моделирования (DES)**, разработанный для **образовательных целей**. Система позволяет студентам:

- 🎓 **Изучать** организацию работы современного аэропорта
- 📊 **Анализировать** влияние параметров на эффективность
- 💼 **Понимать** экономику авиационной индустрии
- 🔬 **Экспериментировать** с различными сценариями
- 📈 **Оптимизировать** процессы через симуляцию

### Ключевые возможности

| Функция | Описание |
|---------|---------|
| 🎬 **DES Моделирование** | Дискретно-событийная система с приоритетной очередью |
| ✈️ **Многокритериальная оптимизация** | Анализ ресурсов, очередей, задержек |
| 💰 **Экономический анализ** | Доход, расходы, ROI по рейсам |
| 👥 **Управление пассажирами** | Очереди, классы, приоритеты |
| 📦 **Логистика багажа** | Выгрузка, сортировка, доставка |
| 🛠️ **Техническое обслуживание** | Форс-мажоры и задержки |
| 🎨 **Интерактивный GUI** | Мониторинг в реальном времени |
| 📊 **Экспорт данных** | CSV, JSON, XLSX, PDF |

---

## 🏗️ Архитектура

### Общая структура

```
AeroSim EDU
├── Core (Ядро DES)
│   ├── EventQueue         → Приоритетная очередь событий
│   ├── Event              → Определение типов событий
│   └── Simulator          → Главный движок симуляции
│
├── Models (Модели данных)
│   ├── Aircraft           → Самолеты
│   ├── Passenger          → Пассажиры и очереди
│   ├── Airport            → Инфраструктура аэропорта
│   ├── Terminal           → Терминал и контрольные пункты
│   ├── Runway/Gate        → ВПП и гейты
│   └── Economics          → Финансовая модель
│
├── GUI (Интерфейс)
│   ├── MainWindow         → Главное окно приложения
│   ├── MonitoringWidgets  → Комплексный мониторинг
│   ├── EconomicsWidget    → Экономическая статистика
│   └── ChartWidgets       → Графики и диаграммы
│
└── Utils (Утилиты)
    ├── ExportManager      → Экспорт в различные форматы
    ├── Logger             → Логирование событий
    └── VariateGenerators  → Генераторы случайных величин
```

### Взаимодействие компонентов

```
Симулятор (Simulator)
    │
    ├─→ EventQueue (Приоритетная очередь)
    │   └─→ Хранит события по времени
    │
    ├─→ Airport (Инфраструктура)
    │   ├─→ Runway (ВПП) - посадка/взлёт
    │   ├─→ Gate (Гейты) - парковка
    │   └─→ Terminal (Терминал) - обслуживание
    │
    ├─→ Aircraft (Самолеты)
    │   └─→ Пассажиры & Багаж
    │
    ├─→ Terminal (Терминал)
    │   ├─→ ControlPoint (Контрольные пункты)
    │   │   ├─→ Luggage (Багаж)
    │   │   └─→ Security (Безопасность)
    │   └─→ PassengerQueue (Очереди пассажиров)
    │
    └─→ AirportEconomics (Финансовая модель)
        └─→ FlightEconomics (Экономика по рейсам)
```

---

## 📐 Математические модели и формулы

### 1. Дискретно-событийное моделирование (DES)

#### Основной алгоритм

```
WHILE current_time < end_time:
    next_event ← EventQueue.pop()              // Получить следующее событие
    current_time ← next_event.time             // Обновить текущее время
    
    CALL process_event(next_event)             // Обработать событие
    
    IF event_generated:                        // Если событие порождает новые события
        new_events ← generate_events()
        FOR each event IN new_events:
            EventQueue.add(event)              // Добавить в очередь
    END IF
END WHILE
```

**Преимущества DES:**
- ⏰ Моделирует только значимые моменты времени
- 🚀 Эффективнее чем непрерывное моделирование
- 📊 Точное воспроизведение случайных процессов
- 🎯 Идеален для систем с очередями

### 2. Система приоритизации очередей

#### Приоритетная очередь событий

```python
# Сравнение событий
def compare_events(e1: Event, e2: Event) -> bool:
    if e1.time != e2.time:
        return e1.time < e2.time        # Сначала по времени
    return e1.priority < e2.priority    # Затем по приоритету
```

#### Режимы приоритета для пассажиров

| Режим | Формула приоритета | Применение |
|-------|------------------|-----------|
| **FCFS** | `priority = queue_position` | Обычная очередь, справедливо |
| **FFFS** | `priority = flight_departure_time` | Вылетающие раньше идут первыми |
| **VIP** | `priority = -1 if is_vip else queue_position` | VIP пропускают |

### 3. Модели прихода пассажиров

#### Составной генератор приходов (Composite Arrival Generator)

```python
# Функция плотности распределения
f(t) = λ₁(t) + λ₂(t) + λ₃(t)

где:
  λ₁(t) - Пуассоновский процесс приходов (базовый поток)
  λ₂(t) - Периодические всплески (тренд)
  λ₃(t) - Случайные события (шум)
```

**Параметры:**
```
λ_base = 0.05 пассажиров/сек        # Базовый поток
λ_peak = 0.15 пассажиров/сек        # Пиковый поток
peak_duration = 300 сек             # Длительность пика
```

#### Интенсивность прихода во времени

```
λ(t) = λ_base + λ_peak · sin(2π·t/T)

где:
  T - период пиков (период суток в модели)
  t - текущее время в симуляции
```

### 4. Модель очередей (Queueing Theory)

#### Среднее время ожидания в системе M/M/c

```
L = ρ/(1-ρ) + c·ρ/(c(1-ρ)ᶜ·(1-ρ))    // Для M/M/c очереди

где:
  ρ = λ/(c·μ) - коэффициент загрузки
  λ - интенсивность прихода
  μ - интенсивность обслуживания
  c - количество каналов обслуживания
```

#### Вероятность ожидания (формула Erlang C)

```
Pw = [ρᶜ/(c·(1-ρ))] / [∑(ᶜ⁻¹, k=0) ρᵏ/k! + ρᶜ/(c·(1-ρ))]

где все параметры как выше.
```

**Интерпретация:**
- `Pw` близко к 1 → система перегружена, большие очереди
- `Pw` близко к 0 → система работает хорошо
- `Pw` = 0.5 → оптимальная загруженность

### 5. Модель времени обслуживания

#### Экспоненциальное распределение времени обслуживания

```
P(T ≤ t) = 1 - e^(-μt)

где:
  μ = 1/E[T] - интенсивность обслуживания
  E[T] - среднее время обслуживания
```

**Примеры конфигурации:**

| Процесс | Среднее время | μ |
|---------|--------------|---|
| Багажный контроль | 10 сек | 0.1 |
| Паспортный контроль | 15 сек | 0.067 |
| Посадка на борт | 30 сек | 0.033 |

### 6. Расчет задержек

#### Общая задержка пассажира

```
D_total = D_luggage + D_security + D_boarding

где:
  D_luggage = max(0, arrival_time_luggage - service_time_luggage)
  D_security = max(0, arrival_time_security - service_time_security)
  D_boarding = max(0, arrival_time_boarding - service_time_boarding)
```

#### Средняя задержка по системе

```
D_avg = (∑ᵐ D_i) / m    where i = 1..m пассажиры

D_pct_late = (count_late / total_passengers) × 100%
```

#### Вероятность пропуска рейса

```
P_miss = P(D_total > T_departure)

где T_departure - время вылета самолета
```

---

## 🚀 Компоненты системы

### 1. EventQueue (Приоритетная очередь)

**Файл:** `src/core/event_queue.py`

```python
class EventQueue:
    """Приоритетная очередь на основе heap"""
    
    def __init__(self):
        self.events: List[Event] = []
    
    def add(self, event: Event) -> None:
        """Добавить событие в очередь O(log n)"""
        heapq.heappush(self.events, event)
    
    def pop(self) -> Event:
        """Получить и удалить событие с наименьшим временем O(log n)"""
        return heapq.heappop(self.events)
    
    def is_empty(self) -> bool:
        """Проверить пустоту очереди O(1)"""
        return len(self.events) == 0
    
    def size(self) -> int:
        """Размер очереди O(1)"""
        return len(self.events)
```

**Операции:**
- `add()` - O(log n) - добавление события
- `pop()` - O(log n) - извлечение события
- `peek()` - O(1) - просмотр верхнего элемента

### 2. Event (Тип события)

**Файл:** `src/core/event.py`

```python
@dataclass
class Event:
    time: float              # Время события
    event_type: EventType    # Тип события
    entity_id: str          # ID сущности (самолет, пассажир и т.д.)
    data: Optional[Any]     # Дополнительные данные
    priority: int = 0       # Приоритет (для одновременных событий)
    
    def __lt__(self, other):
        if self.time != other.time:
            return self.time < other.time
        return self.priority < other.priority
```

**Типы событий:**

```python
class EventType(Enum):
    # Самолеты
    AIRCRAFT_ARRIVAL = "aircraft_arrival"        # Прибытие самолета
    AIRCRAFT_TAKEOFF = "aircraft_takeoff"        # Взлет
    AIRCRAFT_PARKING = "aircraft_parking"        # Припаркование
    
    # Пассажиры
    PASSENGER_ENTRY = "passenger_entry"          # Вход в терминал
    PASSENGER_CHECKIN = "passenger_checkin"      # Прохождение контролей
    PASSENGER_BOARDING = "passenger_boarding"    # Посадка на борт
    
    # Багаж
    BAGGAGE_UNLOAD = "baggage_unload"            # Выгрузка
    BAGGAGE_LOAD = "baggage_load"                # Загрузка
    
    # Ресурсы
    GATE_OCCUPIED = "gate_occupied"              # Занятие гейта
    GATE_RELEASED = "gate_released"              # Освобождение гейта
    RUNWAY_OCCUPIED = "runway_occupied"          # Занятие ВПП
    RUNWAY_RELEASED = "runway_released"          # Освобождение ВПП
    
    # Обслуживание
    MAINTENANCE_START = "maintenance_start"      # Начало ТО
    MAINTENANCE_END = "maintenance_end"          # Конец ТО
```

### 3. AirportSimulator (Главный движок)

**Файл:** `src/core/simulator.py`

```python
class AirportSimulator:
    """Основной класс симулятора DES"""
    
    def __init__(self, config: Dict):
        self.current_time = 0.0
        self.end_time = config.get("duration", 3600)
        self.event_queue = EventQueue()
        self.airport = Airport(config)
        self.terminal = Terminal(...)
        self.airport_economics = AirportEconomics()
        self.stats = {}
    
    def run(self) -> Dict:
        """Запустить симуляцию"""
        self.initialize()
        
        while self.current_time < self.end_time and not self.event_queue.is_empty():
            event = self.event_queue.pop()
            self.current_time = event.time
            self.process_event(event)
        
        return self.stats
    
    def process_event(self, event: Event) -> None:
        """Обработать одно событие"""
        handlers = {
            EventType.AIRCRAFT_ARRIVAL: self._handle_aircraft_arrival,
            EventType.PASSENGER_ENTRY: self._handle_passenger_entry,
            EventType.BAGGAGE_UNLOAD: self._handle_baggage_unload,
            # ... другие обработчики
        }
        
        handler = handlers.get(event.event_type)
        if handler:
            handler(event)
```

### 4. Airport (Инфраструктура)

**Файл:** `src/models/airport.py`

```python
class Airport:
    """Модель аэропорта с инфраструктурой"""
    
    def __init__(self, config: Dict):
        self.runways: List[Runway] = []           # ВПП
        self.terminals: List[Terminal] = []       # Терминалы
        self.gates: Dict[str, Gate] = {}          # Гейты
        self.staff: Dict[str, int] = {}           # Персонал по типам
        
        # Инициализация ресурсов
        self._initialize_runways(config)
        self._initialize_terminals(config)
        self._initialize_gates(config)
```

**Ресурсы аэропорта:**

```python
@dataclass
class Runway:
    """Взлетно-посадочная полоса"""
    runway_id: str
    capacity: int = 1              # Один самолет за раз
    occupied: bool = False
    current_aircraft: Optional[str] = None
    
@dataclass
class Gate:
    """Гейт (позиция для припаркования)"""
    gate_id: str
    terminal_id: str
    occupied: bool = False
    current_aircraft: Optional[str] = None
```

### 5. Passenger (Модель пассажира)

**Файл:** `src/models/passenger.py`

```python
@dataclass
class Passenger:
    """Модель пассажира"""
    passenger_id: str
    flight_id: str
    entry_time: float           # Время входа в терминал
    flight_time: float          # Время вылета
    passenger_type: PassengerType      # ECONOMY, BUSINESS, VIP
    passenger_class: PassengerClass    # FIRST_CLASS или COACH
    status: PassengerStatus = PassengerStatus.ENTERED
    
    # Параметры обслуживания
    luggage_wait_time: float = 10.0    # Время прохождения багажного контроля
    security_wait_time: float = 15.0   # Время прохождения паспортного контроля
    
    # VIP флаг - пропускает очереди
    is_vip: bool = False
    
    # Логирование времени прохождения
    time_log: TimeLog = field(default_factory=TimeLog)
    
    def get_waited_time(self) -> float:
        """Общее время ожидания пассажира"""
        total = 0.0
        if self.time_log.luggage_time and self.time_log.entry_time:
            total += self.time_log.luggage_time - self.time_log.entry_time
        if self.time_log.security_time and self.time_log.luggage_time:
            total += self.time_log.security_time - self.time_log.luggage_time
        return total
    
    def check_missed_flight(self) -> bool:
        """Проверить, пропустил ли пассажир вылет"""
        if self.time_log.boarding_time > self.flight_time:
            return True
        return False
```

**Жизненный цикл пассажира:**

```
ENTERED 
  ↓
IN_LUGGAGE_QUEUE → LUGGAGE_PASSED
  ↓
IN_SECURITY_QUEUE → SECURITY_PASSED
  ↓
IN_BOARDING_QUEUE → BOARDED
  ↓
DEPARTED или MISSED_FLIGHT
```

### 6. Aircraft (Модель самолета)

**Файл:** `src/models/aircraft.py`

```python
@dataclass
class Aircraft:
    """Модель воздушного судна"""
    aircraft_id: str
    aircraft_type: AircraftType    # A320, A380, B737, B777
    capacity: int                   # Вместимость
    current_passengers: int = 0
    status: AircraftStatus = AircraftStatus.IN_FLIGHT
    gate_id: Optional[str] = None
    arrival_time: float = 0.0
    departure_time: float = 0.0
    delay: float = 0.0
    fuel_level: float = 100.0       # % топлива
    baggage_count: int = 0
```

**Статусы самолета:**

```
IN_FLIGHT → APPROACHING → PARKED → BOARDING → READY_FOR_DEPARTURE → DEPARTED
                                          ↓
                                    MAINTENANCE (опционально)
```

---

## 💰 Экономическая модель

**Файл:** `src/models/economics.py`

### 1. Типы рейсов

```python
class FlightType(Enum):
    COMMUTER = "commuter"              # Короткие рейсы
    INTERNATIONAL = "international"    # Международные рейсы
```

### 2. Конфигурация самолета

```python
@dataclass
class AircraftConfig:
    flight_type: FlightType
    capacity: int                      # Общая вместимость
    first_class_seats: int            # Seats first class
    coach_seats: int                  # Seats coach
    flight_duration_minutes: int      # Продолжительность
    base_ticket_price: float          # Базовая цена
    first_class_multiplier: float     # Множитель цены для first class
```

**Стандартные конфигурации:**

```python
# Коммерческие рейсы
COMMUTER_CONFIG = AircraftConfig(
    flight_type=FlightType.COMMUTER,
    capacity=50,
    first_class_seats=10,
    coach_seats=40,
    flight_duration_minutes=60,
    base_ticket_price=100.0,
    first_class_multiplier=1.5
)

# Международные рейсы
INTERNATIONAL_CONFIG = AircraftConfig(
    flight_type=FlightType.INTERNATIONAL,
    capacity=200,
    first_class_seats=40,
    coach_seats=160,
    flight_duration_minutes=500,
    base_ticket_price=300.0,
    first_class_multiplier=2.5
)
```

### 3. Финансовые формулы

#### Доход (Revenue)

```
R_total = R_first_class + R_coach

где:
  R_first_class = n_fc × price_fc
  R_coach = n_coach × price_coach
  
  price_fc = base_price × first_class_multiplier
  price_coach = base_price
```

**Пример расчета:**
```
Commuter рейс:
  n_fc = 10 пассажиров
  n_coach = 35 пассажиров
  
  R_fc = 10 × (100 × 1.5) = 10 × 150 = $1500
  R_coach = 35 × 100 = $3500
  R_total = $5000
```

#### Расходы (Costs)

```
C_total = C_fuel + C_crew + C_maintenance + C_airport

Для Commuter:
  C_fuel = $500
  C_crew = $400
  C_maintenance = $200
  C_airport = $150
  C_total = $1250

Для International:
  C_fuel = $5000
  C_crew = $2000
  C_maintenance = $1000
  C_airport = $500
  C_total = $8500
```

#### Прибыль (Profit)

```
P = R_total - C_total

для Commuter: P = $5000 - $1250 = $3750
для International: P = $28500 - $8500 = $20000
```

#### Return on Investment (ROI)

```
ROI% = (P / C_total) × 100%

для Commuter: ROI = ($3750 / $1250) × 100 = 300%
для International: ROI = ($20000 / $8500) × 100 = 235%
```

#### Коэффициент загрузки (Load Factor)

```
LF% = (n_passengers / capacity) × 100%

Commuter: LF = (45 / 50) × 100 = 90%
International: LF = (180 / 200) × 100 = 90%
```

#### Средняя цена билета (Average Ticket Price)

```
ATP = R_total / n_total_passengers

Commuter: ATP = $5000 / 45 = $111.11
International: ATP = $28500 / 180 = $158.33
```

### 4. Класс FlightEconomics

```python
@dataclass
class FlightEconomics:
    """Экономический анализ одного рейса"""
    flight_id: str
    flight_type: FlightType
    aircraft_config: AircraftConfig
    
    # Доходы
    passenger_revenue: PassengerClassRevenue
    
    # Расходы
    fuel_cost: float = 0.0
    crew_cost: float = 0.0
    maintenance_cost: float = 0.0
    airport_fees: float = 0.0
    
    # Метрики
    load_factor: float = 0.0
    passengers_served: int = 0
    on_time_percentage: float = 100.0
    
    @property
    def total_revenue(self) -> float:
        return self.passenger_revenue.total_revenue
    
    @property
    def total_costs(self) -> float:
        return self.fuel_cost + self.crew_cost + \
               self.maintenance_cost + self.airport_fees
    
    @property
    def profit(self) -> float:
        return self.total_revenue - self.total_costs
    
    @property
    def roi_percentage(self) -> float:
        if self.total_costs == 0:
            return 0.0
        return (self.profit / self.total_costs) * 100
```

### 5. Класс AirportEconomics

```python
@dataclass
class AirportEconomics:
    """Совокупная экономика аэропорта"""
    flights: Dict[str, FlightEconomics] = field(default_factory=dict)
    
    @property
    def total_revenue(self) -> float:
        return sum(f.total_revenue for f in self.flights.values())
    
    @property
    def total_costs(self) -> float:
        return sum(f.total_costs for f in self.flights.values())
    
    @property
    def total_profit(self) -> float:
        return self.total_revenue - self.total_costs
    
    @property
    def average_roi(self) -> float:
        if not self.flights:
            return 0.0
        return sum(f.roi_percentage for f in self.flights.values()) / len(self.flights)
```

---

## 🔄 Алгоритмы и процедуры

### 1. Основной цикл симуляции

```python
def run(self):
    """Главный цикл симуляции"""
    self.initialize()
    
    while self.current_time < self.end_time and not self.event_queue.is_empty():
        # Шаг 1: Извлечь событие с минимальным временем
        event = self.event_queue.pop()
        
        # Шаг 2: Обновить текущее время
        self.current_time = event.time
        
        # Шаг 3: Обработать событие и создать новые события
        self.process_event(event)
        
        # Шаг 4: Обновить статистику
        self.stats["total_events_processed"] += 1
        self.stats["events_by_type"][event.event_type.value] += 1
    
    return self.stats
```

### 2. Обработка прибытия пассажира

```
PROCESS PASSENGER_ENTRY (event):
    passenger ← event.data
    passenger.status ← IN_LUGGAGE_QUEUE
    
    // Добавить в очередь багажного контроля
    luggage_queue.add(passenger)
    
    // Если канал свободен, начать обслуживание
    IF luggage_control.is_free():
        next_passenger ← luggage_queue.pop()
        service_time ← exponential_distribution(μ_luggage)
        
        // Создать событие завершения обслуживания
        event_luggage_done ← Event(
            time = current_time + service_time,
            type = PASSENGER_CHECKIN,
            entity = next_passenger
        )
        event_queue.add(event_luggage_done)
    END IF
END PROCESS
```

### 3. Обработка прибытия самолета

```
PROCESS AIRCRAFT_ARRIVAL (event):
    aircraft ← event.data
    aircraft.status ← APPROACHING
    
    // Шаг 1: Выделить ВПП
    runway ← find_available_runway()
    IF runway IS NULL:
        // Ждем освобождения ВПП
        runway_queue.add(aircraft)
        RETURN
    END IF
    
    // Шаг 2: Приземлиться
    landing_time ← current_time + time_to_land
    aircraft.status ← PARKED
    
    // Шаг 3: Выделить гейт
    gate ← find_available_gate()
    aircraft.gate_id ← gate.id
    
    // Шаг 4: Начать высадку пассажиров
    FOR each passenger IN aircraft.passengers:
        passenger.status ← ENTERED
        terminal.add_passenger(passenger)
    END FOR
    
    // Шаг 5: Начать выгрузку багажа
    baggage_unload_event ← Event(
        time = current_time + baggage_unload_time,
        type = BAGGAGE_UNLOAD,
        entity = aircraft
    )
    event_queue.add(baggage_unload_event)
END PROCESS
```

### 4. Обработка выгрузки багажа

```
PROCESS BAGGAGE_UNLOAD (event):
    aircraft ← event.data
    
    // Вычислить количество багажа
    total_baggage ← aircraft.passengers.size() × avg_baggage_per_person
    
    // Проверить на форс-мажор (задержка)
    IF random() < incident_probability:
        delay ← random_incident_delay()
        aircraft.delay += delay
        
        log "⚠️ Инцидент: Задержка выгрузки на {delay}м"
        stats.total_incidents += 1
    END IF
    
    // Завершить выгрузку
    aircraft.baggage_count = 0
    
    log "💰 Рейс: Revenue=${revenue}, Profit=${profit}, ROI={roi}%"
END PROCESS
```

### 5. Обработка посадки на борт

```
PROCESS PASSENGER_BOARDING (event):
    passenger ← event.data
    
    // Проверить, не пропустил ли пассажир рейс
    IF passenger.time_log.boarding_time > passenger.flight_time:
        passenger.status ← MISSED_FLIGHT
        passenger.missed_flight ← TRUE
        
        log "❌ Пассажир {id} пропустил рейс"
        stats.missed_passengers += 1
        RETURN
    END IF
    
    // Посадить на борт
    aircraft ← find_aircraft(passenger.flight_id)
    added ← aircraft.add_passengers(1)
    
    IF added > 0:
        passenger.status ← BOARDED
        passenger.time_log.departure_time ← current_time
        
        log "✈️ Пассажир {id} посажен на борт"
    END IF
END PROCESS
```

---

## 📊 Использование и примеры

### 1. Базовый запуск CLI

```bash
# Запустить с конфигурацией по умолчанию (1 час)
python3 aerosim_edu.py --cli

# Запустить на 30 минут с логированием
python3 aerosim_edu.py --cli --duration 1800 --verbose

# Запустить с пользовательской конфигурацией
python3 aerosim_edu.py --cli --config config/custom.json
```

### 2. Запуск GUI

```bash
# Запустить интерактивный интерфейс
python3 aerosim_edu.py --gui

# Или используя специальный скрипт Phase 6
python3 run_gui_phase6.py
```

### 3. Программный API

```python
from src.core.simulator import AirportSimulator
from config.default import DEFAULT_CONFIG

# Создать симулятор
config = {
    "duration": 7200,  # 2 часа
    "airport": {
        "num_runways": 3,
        "num_terminals": 4,
        "gates_per_terminal": 25
    },
    "aircraft": {
        "initial_aircraft": 10,
        "arrival_rate": 0.8
    },
    "enable_incidents": True,
    "incident_probability": 0.1
}

simulator = AirportSimulator(config)

# Запустить симуляцию
stats = simulator.run()

# Получить результаты
print(f"Всего обработано событий: {stats['total_events_processed']}")
print(f"Всего самолетов: {stats['total_aircraft']}")
print(f"Всего пассажиров: {stats['total_passengers']}")
print(f"Средняя задержка: {stats['avg_delay']:.2f} сек")
```

### 4. Экспорт результатов

```python
from src.utils.export_manager import ExportManager

export = ExportManager()

# Экспортировать в JSON
export.export_json(stats, "results/report.json")

# Экспортировать в CSV
export.export_csv(stats, "results/report.csv")

# Экспортировать в Excel
export.export_xlsx(stats, "results/report.xlsx")

# Экспортировать в PDF
export.export_pdf(stats, "results/report.pdf")
```

### 5. Анализ результатов

```python
# Получить статистику по типам событий
events_stats = stats['events_by_type']
for event_type, count in events_stats.items():
    print(f"{event_type}: {count}")

# Экономическая статистика
economics = stats['airport_economics']
print(f"Общий доход: ${economics.total_revenue:.2f}")
print(f"Общие расходы: ${economics.total_costs:.2f}")
print(f"Прибыль: ${economics.total_profit:.2f}")
print(f"Средний ROI: {economics.average_roi:.2f}%")

# Статистика терминала
terminal_stats = stats['terminal_stats']
print(f"Пассажиров обработано: {terminal_stats['passengers_processed']}")
print(f"Средняя задержка: {terminal_stats['avg_wait_time']:.2f} сек")
print(f"Максимальная очередь: {terminal_stats['max_queue_size']}")
```

---

## 🔌 API Справка

### AirportSimulator

```python
class AirportSimulator:
    def __init__(self, config: Dict)
    def initialize() -> None
    def run() -> Dict
    def process_event(event: Event) -> None
    def get_statistics() -> Dict
    def set_speed_multiplier(multiplier: float) -> None
    def stop() -> None
```

### EventQueue

```python
class EventQueue:
    def add(event: Event) -> None
    def pop() -> Event
    def peek() -> Event
    def is_empty() -> bool
    def size() -> int
```

### Airport

```python
class Airport:
    def __init__(config: Dict)
    def get_available_runway() -> Optional[Runway]
    def get_available_gate(terminal_id: str) -> Optional[Gate]
    def get_staff(staff_type: str) -> int
    def allocate_resource(resource_type: str, amount: int) -> bool
    def release_resource(resource_type: str, amount: int) -> bool
```

### Terminal

```python
class Terminal:
    def __init__(terminal_id: str, luggage_workers: int, security_workers: int)
    def add_passenger(passenger: Passenger) -> bool
    def remove_passenger(passenger_id: str) -> bool
    def get_queue_size(queue_type: str) -> int
    def process_passengers() -> List[Passenger]
```

### ExportManager

```python
class ExportManager:
    def export_json(stats: Dict, file_path: str) -> bool
    def export_csv(stats: Dict, file_path: str) -> bool
    def export_xlsx(stats: Dict, file_path: str) -> bool
    def export_pdf(stats: Dict, file_path: str) -> bool
    def export_all(stats: Dict, output_dir: str) -> bool
```

---

## 📁 Структура файлов

```
AeroSim EDU/
│
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── event.py              # Определение типов событий
│   │   ├── event_queue.py        # Приоритетная очередь
│   │   └── simulator.py          # Главный движок симуляции
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── aircraft.py           # Модель самолета
│   │   ├── passenger.py          # Модель пассажира
│   │   ├── airport.py            # Инфраструктура аэропорта
│   │   ├── runway.py             # Взлетно-посадочная полоса
│   │   ├── gate.py               # Гейты припаркования
│   │   ├── terminal.py           # Терминал обслуживания
│   │   ├── control_point.py      # Контрольные пункты
│   │   ├── passenger_queue.py    # Очереди пассажиров
│   │   └── economics.py          # Финансовая модель
│   │
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── advanced_main_window.py      # Главное окно GUI
│   │   ├── monitoring_widgets.py        # Виджеты мониторинга
│   │   ├── economics_widget.py          # Виджет экономики
│   │   └── chart_widgets.py             # Графики и диаграммы
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # Система логирования
│       ├── export_manager.py      # Экспорт в разные форматы
│       └── variate_generators.py  # Генераторы случайных величин
│
├── config/
│   ├── default.py               # Конфигурация по умолчанию
│   └── custom.json             # Пользовательская конфигурация
│
├── tests/
│   ├── __init__.py
│   └── test_simulator.py        # Unit тесты
│
├── docs/
│   └── *.md                     # Документация
│
├── results/
│   └── *.{json,csv,xlsx,pdf}   # Результаты экспорта
│
├── aerosim_edu.py              # Главный файл приложения
├── run_gui_phase6.py           # Запуск GUI (Phase 6)
├── requirements.txt            # Зависимости Python
├── package.json                # Конфигурация Node.js (если используется)
└── README.md                   # Эта документация
```

---

## 🎓 Образовательный потенциал

### Курсы и дисциплины

1. **Операционный менеджмент**
   - Управление процессами
   - Оптимизация ресурсов
   - Анализ узких мест

2. **Теория массового обслуживания (Queueing Theory)**
   - M/M/1, M/M/c системы
   - Анализ очередей
   - Формулы Erlang

3. **Моделирование и симуляция**
   - Дискретно-событийное моделирование
   - Генерация случайных величин
   - "Что если" анализ

4. **Логистика и управление цепочками поставок**
   - Обработка багажа
   - Координация процессов
   - Управление потоками

5. **Финансовая аналитика**
   - Расчет ROI
   - Анализ затрат и доходов
   - Прибыльность операций

### Примеры исследований

**Исследование 1: Влияние количества ВПП на задержки**
```
Гипотеза: Увеличение ВПП снизит задержки
Метод: Запустить симуляцию с 1, 2, 3, 4 ВПП
Анализ: Построить график зависимости
Вывод: Найти оптимальное количество
```

**Исследование 2: Оптимизация раскладки гейтов**
```
Параметры: Расстояния, пропускная способность
Цель: Минимизировать время обслуживания
Результат: Предложить оптимальную конфигурацию
```

**Исследование 3: Анализ рентабельности**
```
Задача: Максимизировать прибыль аэропорта
Переменные: Типы рейсов, цены билетов, расходы
Результат: Оптимальный микс рейсов
```

---

## 🚀 Производительность и оптимизация

### Сложность алгоритмов

| Операция | Сложность | Примечание |
|----------|-----------|-----------|
| Добавление события | O(log n) | Heap push |
| Извлечение события | O(log n) | Heap pop |
| Поиск ВПП | O(r) | r - количество ВПП |
| Поиск гейта | O(g) | g - количество гейтов |
| Обслуживание пассажира | O(1) | Амортизированная константа |

### Масштабируемость

- **События:** До 100,000 в час
- **Пассажиры:** До 10,000 одновременно
- **Самолеты:** До 500 в системе
- **Время симуляции:** От 1 часа до 1 недели

### Оптимизация

```python
# Использование кэширования для часто используемых данных
cache_available_gates = {}

# Ленивая инициализация ресурсов
def get_available_gate(self):
    # Кэшировать результаты между проверками
    if cache_available_gates:
        return cache_available_gates.pop()
    
    # Иначе поискать новый
    for gate in self.gates:
        if not gate.occupied:
            return gate
    return None

# Батчинг операций
def process_multiple_events(self, batch_size=100):
    # Обработать несколько событий за раз
    for _ in range(batch_size):
        if self.event_queue.is_empty():
            break
        event = self.event_queue.pop()
        self.process_event(event)
```

---

## 📞 Помощь и поддержка

### Решение проблем

**Q: Симуляция работает медленно**
A: 
- Уменьшить `duration` (длительность симуляции)
- Уменьшить количество начальных самолетов
- Отключить `enable_incidents`
- Использовать ускорение в GUI (2x, 5x, 10x)

**Q: Количество пассажиров не совпадает**
A:
- Проверить время прихода (`arrival_generator`)
- Проверить вероятность пропуска рейса
- Просмотреть логи для отклоненных пассажиров

**Q: Как интегрировать свою модель?**
A:
- Наследовать от базового класса (например, `Passenger`)
- Переопределить методы обработки
- Добавить тип события в `EventType`
- Создать обработчик в `process_event()`

### Контакты

- **GitHub Issues:** [Ссылка на issues](https://github.com/project/issues)
- **Email:** danayerofficial@yandex.ru
- **Документация:** [docs/](docs/)

---

## 📝 История версий

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.0.0 | 24.11.2025 | Phase 6 Complete - Полная экономика, мониторинг, экспорт |
| 0.9.0 | 20.11.2025 | Phase 5 - Расширенный GUI, графики |
| 0.8.0 | 15.11.2025 | Phase 4 - Экспорт в PDF |
| 0.7.0 | 10.11.2025 | Phase 3 - Multi-format export |
| 0.6.0 | 05.11.2025 | Phase 2 - GUI interface |
| 0.5.0 | 01.11.2025 | Phase 1 - Core DES engine |

---

## 📄 Лицензия

MIT License - Свободное использование в образовательных целях

---

**Проект AeroSim EDU © 2025**
**Версия документации: 1.0.0**
**Последнее обновление: 24 ноября 2025 г.**

