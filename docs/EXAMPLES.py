"""
Примеры использования AeroSim EDU
"""

# Пример 1: Базовый запуск симуляции через Python
from src.core.simulator import AirportSimulator

# Создать симулятор с конфигом на 1 час
config = {
    "duration": 3600,
    "airport": {
        "num_runways": 2,
        "num_terminals": 3,
        "gates_per_terminal": 20,
    },
    "aircraft": {
        "initial_aircraft": 10,
    }
}

simulator = AirportSimulator(config)
simulator.run()

# Получить статистику
stats = simulator.get_statistics()
print(f"Обработано событий: {stats['total_events_processed']}")


# Пример 2: Создание пользовательского события
from src.core.event import Event, EventType

event = Event(
    time=100.0,
    event_type=EventType.AIRCRAFT_ARRIVAL,
    entity_id="AC123",
    data={"aircraft_id": "AC123"}
)

print(event)


# Пример 3: Работа с моделями
from src.models.aircraft import Aircraft, AircraftType, AircraftStatus
from src.models.passenger import Passenger, PassengerStatus, PassengerType

# Создать самолет
aircraft = Aircraft(
    aircraft_id="AC001",
    aircraft_type=AircraftType.AIRBUS_A320,
    capacity=180
)

# Добавить пассажиров
added = aircraft.add_passengers(150)
print(f"Добавлено пассажиров: {added}")

# Создать пассажира
passenger = Passenger(
    passenger_id="PASS001",
    flight_id="LH123",
    passenger_type=PassengerType.ECONOMY,
    status=PassengerStatus.ARRIVED
)

print(f"Пассажир: {passenger}")


# Пример 4: Работа с аэропортом
from src.models.airport import Airport

# Создать аэропорт
airport = Airport({
    "num_runways": 3,
    "num_terminals": 4,
    "gates_per_terminal": 25
})

# Получить доступный гейт
gate = airport.get_available_gate()
if gate:
    print(f"Гейт {gate.gate_id} свободен")
    gate.occupy("AC001")
    print(f"Гейт занят самолетом AC001")

# Получить доступную ВПП
runway = airport.get_available_runway()
if runway:
    print(f"ВПП {runway.runway_id} свободна")
