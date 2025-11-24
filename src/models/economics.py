"""
Экономическая модель аэропорта
Интегрировано из Airport-Simulation.py-master
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class FlightType(Enum):
    """Типы рейсов"""
    COMMUTER = "commuter"          # Короткие рейсы (60 мин, 50 мест)
    INTERNATIONAL = "international" # Длинные рейсы (500 мин, 200 мест)


class PassengerClass(Enum):
    """Классы пассажиров"""
    FIRST_CLASS = "first_class"
    COACH = "coach"


@dataclass
class AircraftConfig:
    """Конфигурация самолета по типу рейса"""
    flight_type: FlightType
    capacity: int                    # Общая вместимость
    first_class_seats: int          # Места first class
    coach_seats: int                # Места coach
    flight_duration_minutes: int    # Продолжительность рейса
    base_ticket_price: float        # Базовая цена билета
    first_class_multiplier: float   # Множитель цены для first class
    
    
# Стандартные конфигурации - интегрировано из constants_and_params.py
COMMUTER_CONFIG = AircraftConfig(
    flight_type=FlightType.COMMUTER,
    capacity=50,
    first_class_seats=10,
    coach_seats=40,
    flight_duration_minutes=60,
    base_ticket_price=100.0,
    first_class_multiplier=1.5
)

INTERNATIONAL_CONFIG = AircraftConfig(
    flight_type=FlightType.INTERNATIONAL,
    capacity=200,
    first_class_seats=40,
    coach_seats=160,
    flight_duration_minutes=500,
    base_ticket_price=300.0,
    first_class_multiplier=2.5
)


@dataclass
class PassengerClassRevenue:
    """Доход от класса пассажиров"""
    first_class_passengers: int = 0
    coach_passengers: int = 0
    first_class_revenue: float = 0.0
    coach_revenue: float = 0.0
    
    @property
    def total_passengers(self) -> int:
        return self.first_class_passengers + self.coach_passengers
    
    @property
    def total_revenue(self) -> float:
        return self.first_class_revenue + self.coach_revenue
    
    @property
    def average_ticket_price(self) -> float:
        if self.total_passengers == 0:
            return 0.0
        return self.total_revenue / self.total_passengers


@dataclass
class FlightEconomics:
    """Экономический анализ одного рейса"""
    flight_id: str
    flight_type: FlightType
    aircraft_config: AircraftConfig = field(default_factory=lambda: COMMUTER_CONFIG)
    
    # Доходы
    passenger_revenue: PassengerClassRevenue = field(default_factory=PassengerClassRevenue)
    
    # Расходы
    fuel_cost: float = 0.0
    crew_cost: float = 0.0
    maintenance_cost: float = 0.0
    airport_fees: float = 0.0
    
    # Статистика
    load_factor: float = 0.0  # Процент заполненности
    passengers_served: int = 0
    on_time_percentage: float = 100.0  # Процент пунктуальных рейсов
    
    def calculate_costs(self):
        """Вычислить расходы в зависимости от типа рейса"""
        if self.flight_type == FlightType.COMMUTER:
            self.fuel_cost = 500.0
            self.crew_cost = 400.0
            self.maintenance_cost = 200.0
            self.airport_fees = 150.0
        else:  # INTERNATIONAL
            self.fuel_cost = 5000.0
            self.crew_cost = 2000.0
            self.maintenance_cost = 1000.0
            self.airport_fees = 500.0
    
    def update_load_factor(self):
        """Обновить коэффициент заполнения"""
        if self.aircraft_config.capacity > 0:
            self.load_factor = (
                self.passenger_revenue.total_passengers / 
                self.aircraft_config.capacity * 100
            )
    
    @property
    def total_revenue(self) -> float:
        """Общий доход"""
        return self.passenger_revenue.total_revenue
    
    @property
    def total_costs(self) -> float:
        """Общие расходы"""
        return (
            self.fuel_cost + 
            self.crew_cost + 
            self.maintenance_cost + 
            self.airport_fees
        )
    
    @property
    def profit(self) -> float:
        """Прибыль"""
        return self.total_revenue - self.total_costs
    
    @property
    def roi_percentage(self) -> float:
        """ROI в процентах"""
        if self.total_costs == 0:
            return 0.0
        return (self.profit / self.total_costs) * 100
    
    def __repr__(self) -> str:
        return (
            f"FlightEconomics({self.flight_id}, "
            f"type={self.flight_type.value}, "
            f"revenue=${self.total_revenue:.2f}, "
            f"profit=${self.profit:.2f}, "
            f"roi={self.roi_percentage:.1f}%)"
        )


@dataclass
class AirportEconomics:
    """Общая экономическая статистика аэропорта"""
    simulation_time: float = 0.0
    total_flights: int = 0
    commuter_flights: int = 0
    international_flights: int = 0
    
    # Доходы
    total_passenger_revenue: float = 0.0
    first_class_revenue: float = 0.0
    coach_revenue: float = 0.0
    
    # Расходы
    total_costs: float = 0.0
    fuel_costs: float = 0.0
    crew_costs: float = 0.0
    maintenance_costs: float = 0.0
    airport_fees: float = 0.0
    
    # Статистика
    total_passengers_served: int = 0
    first_class_passengers: int = 0
    coach_passengers: int = 0
    
    # История (для отслеживания по времени)
    flight_economics_history: List[FlightEconomics] = field(default_factory=list)
    
    def add_flight_economics(self, flight_econ: FlightEconomics):
        """Добавить экономику полета"""
        self.flight_economics_history.append(flight_econ)
        
        self.total_flights += 1
        if flight_econ.flight_type == FlightType.COMMUTER:
            self.commuter_flights += 1
        else:
            self.international_flights += 1
        
        # Обновить доходы
        self.total_passenger_revenue += flight_econ.passenger_revenue.total_revenue
        self.first_class_revenue += flight_econ.passenger_revenue.first_class_revenue
        self.coach_revenue += flight_econ.passenger_revenue.coach_revenue
        
        # Обновить расходы
        self.total_costs += flight_econ.total_costs
        self.fuel_costs += flight_econ.fuel_cost
        self.crew_costs += flight_econ.crew_cost
        self.maintenance_costs += flight_econ.maintenance_cost
        self.airport_fees += flight_econ.airport_fees
        
        # Обновить статистику пассажиров
        self.total_passengers_served += flight_econ.passenger_revenue.total_passengers
        self.first_class_passengers += flight_econ.passenger_revenue.first_class_passengers
        self.coach_passengers += flight_econ.passenger_revenue.coach_passengers
    
    @property
    def total_profit(self) -> float:
        """Общая прибыль"""
        return self.total_passenger_revenue - self.total_costs
    
    @property
    def roi_percentage(self) -> float:
        """Общий ROI"""
        if self.total_costs == 0:
            return 0.0
        return (self.total_profit / self.total_costs) * 100
    
    @property
    def average_load_factor(self) -> float:
        """Средний коэффициент заполнения"""
        if len(self.flight_economics_history) == 0:
            return 0.0
        return sum(f.load_factor for f in self.flight_economics_history) / len(self.flight_economics_history)
    
    @property
    def average_revenue_per_flight(self) -> float:
        """Средний доход на один рейс"""
        if self.total_flights == 0:
            return 0.0
        return self.total_passenger_revenue / self.total_flights
    
    @property
    def average_profit_per_flight(self) -> float:
        """Средняя прибыль на один рейс"""
        if self.total_flights == 0:
            return 0.0
        return self.total_profit / self.total_flights
    
    def get_first_class_revenue_percentage(self) -> float:
        """Процент дохода от first class"""
        if self.total_passenger_revenue == 0:
            return 0.0
        return (self.first_class_revenue / self.total_passenger_revenue) * 100
    
    def get_coach_revenue_percentage(self) -> float:
        """Процент дохода от coach"""
        if self.total_passenger_revenue == 0:
            return 0.0
        return (self.coach_revenue / self.total_passenger_revenue) * 100
    
    def get_flight_profitability_ranking(self) -> List[FlightEconomics]:
        """Рейсы, отсортированные по прибыльности"""
        return sorted(self.flight_economics_history, key=lambda f: f.profit, reverse=True)
    
    def __repr__(self) -> str:
        return (
            f"AirportEconomics(flights={self.total_flights}, "
            f"passengers={self.total_passengers_served}, "
            f"revenue=${self.total_passenger_revenue:.2f}, "
            f"profit=${self.total_profit:.2f}, "
            f"roi={self.roi_percentage:.1f}%)"
        )
