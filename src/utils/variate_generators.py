"""
Генераторы случайных величин для реалистичного моделирования прибытий
Интегрировано из Airport-Simulation.py-master проекта
"""

import math
import random
import numpy as np
from typing import Tuple, List


class ArrivalGenerator:
    """Базовый класс для генерации прибытий пассажиров"""
    
    def __init__(self, seed: int = None):
        """
        Инициализация
        
        Args:
            seed: Seed для воспроизводимости
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def get_next_arrival(self) -> float:
        """
        Получить время до следующего прибытия
        
        Returns:
            Время в минутах
        """
        raise NotImplementedError


class PoissonArrivalGenerator(ArrivalGenerator):
    """
    Пуассоновский процесс - для коммутеров
    Arrival Rate = 40 человек/час = 2/3 в минуту
    """
    
    def __init__(self, arrival_rate: float = 2.0/3.0, seed: int = None):
        """
        Инициализация
        
        Args:
            arrival_rate: Интенсивность прибытий (1/λ в минутах)
            seed: Seed для воспроизводимости
        """
        super().__init__(seed)
        self.arrival_rate = arrival_rate
    
    def get_next_arrival(self) -> float:
        """
        Генерировать интервал до следующего прибытия
        Используется формула: -ln(1-U) / λ
        
        Returns:
            Время до следующего прибытия в минутах
        """
        return -math.log(1.0 - random.random()) / self.arrival_rate
    
    def generate_arrivals_for_period(self, period_minutes: float) -> List[float]:
        """
        Генерировать прибытия за период времени
        
        Args:
            period_minutes: Длительность периода в минутах (e.g. 360 для 6 часов)
            
        Returns:
            Список времен прибытия (в порядке возрастания)
        """
        arrivals = []
        total_time = 0.0
        
        while total_time <= period_minutes:
            interval = self.get_next_arrival()
            total_time += interval
            if total_time <= period_minutes:
                arrivals.append(total_time)
        
        return arrivals


class NormalArrivalGenerator(ArrivalGenerator):
    """
    Нормальное распределение - для международных пассажиров
    Mean = 75 мин (среднее время за день до вылета)
    Std = 50 мин
    """
    
    def __init__(self, mean: float = 75.0, std: float = 50.0, seed: int = None):
        """
        Инициализация
        
        Args:
            mean: Математическое ожидание в минутах
            std: Стандартное отклонение в минутах
            seed: Seed для воспроизводимости
        """
        super().__init__(seed)
        self.mean = mean
        self.std = std
    
    def get_next_arrival(self) -> float:
        """
        Генерировать время прибытия по нормальному распределению
        
        Returns:
            Время в минутах
        """
        return np.random.normal(self.mean, self.std)
    
    def get_next_arrival_positive(self) -> float:
        """
        Генерировать время прибытия (только положительные значения)
        
        Returns:
            Время в минутах (≥ 0)
        """
        value = self.get_next_arrival()
        return max(0.0, value)


class BoxMullerNormalGenerator(ArrivalGenerator):
    """
    Нормальное распределение через Box-Muller (Polar coordinates)
    Никогда не генерирует отрицательные значения
    """
    
    def __init__(self, mean: float = 75.0, std: float = 50.0, seed: int = None):
        """
        Инициализация
        
        Args:
            mean: Математическое ожидание в минутах
            std: Стандартное отклонение в минутах
            seed: Seed для воспроизводимости
        """
        super().__init__(seed)
        self.mean = mean
        self.std = std
    
    def get_next_arrival(self) -> float:
        """
        Генерировать значение по методу Box-Muller (Polar coordinates)
        Основано на: Sheldon Ross, Simulations 5th edition, page 83
        
        Returns:
            Время в минутах (всегда ≥ 0)
        """
        while True:
            # Шаг 1: Генерировать U1 и U2
            u1 = random.random()
            u2 = random.random()
            
            # Шаг 2: Трансформация
            v1 = 2.0 * u1 - 1.0
            v2 = 2.0 * u2 - 1.0
            s = (v1 ** 2) + (v2 ** 2)
            
            if s <= 1.0:
                # Успешное генерирование
                x = math.sqrt((-2.0 * math.log(s)) / s) * v1
                z = x * math.sqrt(self.std) + self.mean
                return z
    
    def generate_arrivals_for_flight(self, num_arrivals: int) -> List[float]:
        """
        Генерировать прибытия пассажиров на рейс
        
        Args:
            num_arrivals: Количество пассажиров
            
        Returns:
            Отсортированный список времен прибытия
        """
        arrivals = []
        for _ in range(num_arrivals):
            arrival = self.get_next_arrival()
            arrivals.append(arrival)
        
        arrivals.sort()
        return arrivals


class BinomialClassGenerator(ArrivalGenerator):
    """
    Биномиальное распределение - для определения класса пассажира
    """
    
    def __init__(self, n: int = 50, p: float = 0.8, seed: int = None):
        """
        Инициализация
        
        Args:
            n: Количество попыток
            p: Вероятность успеха
            seed: Seed для воспроизводимости
        """
        super().__init__(seed)
        self.n = n
        self.p = p
    
    def get_number_of_seats_sold(self) -> int:
        """
        Генерировать количество проданных билетов
        
        Returns:
            Количество билетов
        """
        return np.random.binomial(self.n, self.p)


class CompositeArrivalGenerator(ArrivalGenerator):
    """
    Комбинированный генератор для аэропорта с разными типами рейсов
    """
    
    def __init__(self, seed: int = None):
        """
        Инициализация
        
        Args:
            seed: Seed для воспроизводимости
        """
        super().__init__(seed)
        
        # Коммутерские рейсы (каждый час)
        self.commuter_gen = PoissonArrivalGenerator(2.0/3.0, seed)
        
        # Международные рейсы (каждые 8 часов)
        self.intl_first_gen = BoxMullerNormalGenerator(75.0, 50.0, seed)
        self.intl_coach_gen = BoxMullerNormalGenerator(75.0, 50.0, seed)
        
        # Классы пассажиров
        self.first_class_seller = BinomialClassGenerator(50, 0.80, seed)
        self.coach_seller = BinomialClassGenerator(150, 0.85, seed)
    
    def get_commuter_arrivals_for_period(self, period_minutes: float) -> List[float]:
        """Прибытия коммутеров на период"""
        return self.commuter_gen.generate_arrivals_for_period(period_minutes)
    
    def get_intl_first_class_arrivals(self, num_seats: int = None) -> List[float]:
        """Прибытия first class международных пассажиров"""
        if num_seats is None:
            num_seats = self.first_class_seller.get_number_of_seats_sold()
        return self.intl_first_gen.generate_arrivals_for_flight(num_seats)
    
    def get_intl_coach_arrivals(self, num_seats: int = None) -> List[float]:
        """Прибытия coach международных пассажиров"""
        if num_seats is None:
            num_seats = self.coach_seller.get_number_of_seats_sold()
        return self.intl_coach_gen.generate_arrivals_for_flight(num_seats)
    
    def __repr__(self) -> str:
        return "CompositeArrivalGenerator(commuter=Poisson, intl=BoxMuller)"
