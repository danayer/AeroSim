"""
Тесты для модуля симуляции
"""

import unittest
from src.core.simulator import AirportSimulator
from src.core.event import Event, EventType
from config.default import DEFAULT_CONFIG


class TestAirportSimulator(unittest.TestCase):
    """Тесты для AirportSimulator"""
    
    def setUp(self):
        """Подготовка к тестам"""
        config = DEFAULT_CONFIG.copy()
        config["duration"] = 600  # 10 минут
        self.simulator = AirportSimulator(config)
    
    def test_initialization(self):
        """Тест инициализации симулятора"""
        self.assertEqual(self.simulator.current_time, 0.0)
        self.assertEqual(self.simulator.end_time, 600)
        self.assertFalse(self.simulator.is_running)
    
    def test_event_queue(self):
        """Тест очереди событий"""
        event = Event(
            time=10.0,
            event_type=EventType.AIRCRAFT_ARRIVAL,
            entity_id="AC001"
        )
        self.simulator.event_queue.push(event)
        
        self.assertFalse(self.simulator.event_queue.is_empty())
        retrieved_event = self.simulator.event_queue.pop()
        self.assertEqual(retrieved_event.entity_id, "AC001")
    
    def test_airport_initialization(self):
        """Тест инициализации аэропорта"""
        airport = self.simulator.airport
        
        self.assertEqual(len(airport.runways), 2)
        self.assertEqual(len(airport.terminals), 3)
        
        # Проверить наличие гейтов
        total_gates = sum(len(t.gates) for t in airport.terminals.values())
        self.assertEqual(total_gates, 60)  # 3 терминала * 20 гейтов


class TestEventQueue(unittest.TestCase):
    """Тесты для очереди событий"""
    
    def test_event_ordering(self):
        """Тест упорядочивания событий по времени"""
        from src.core.event_queue import EventQueue
        
        queue = EventQueue()
        
        # Добавить события в неправильном порядке
        queue.push(Event(30.0, EventType.AIRCRAFT_ARRIVAL, "AC003"))
        queue.push(Event(10.0, EventType.AIRCRAFT_ARRIVAL, "AC001"))
        queue.push(Event(20.0, EventType.AIRCRAFT_ARRIVAL, "AC002"))
        
        # Проверить, что они извлекаются в правильном порядке
        self.assertEqual(queue.pop().time, 10.0)
        self.assertEqual(queue.pop().time, 20.0)
        self.assertEqual(queue.pop().time, 30.0)


class TestAirport(unittest.TestCase):
    """Тесты для аэропорта"""
    
    def test_gate_availability(self):
        """Тест доступности гейтов"""
        from src.models.airport import Airport
        
        airport = Airport()
        
        # Должен быть доступен хотя бы один гейт
        gate = airport.get_available_gate()
        self.assertIsNotNone(gate)
        
        # Занять гейт
        gate.occupy("AC001")
        self.assertFalse(gate.is_available())
        
        # Освободить гейт
        gate.release()
        self.assertTrue(gate.is_available())
    
    def test_runway_availability(self):
        """Тест доступности ВПП"""
        from src.models.airport import Airport
        
        airport = Airport()
        
        runway = airport.get_available_runway()
        self.assertIsNotNone(runway)
        
        # Занять для посадки
        self.assertTrue(runway.occupy_for_landing("AC001"))
        self.assertFalse(runway.is_available())
        
        # Освободить
        runway.release()
        self.assertTrue(runway.is_available())


if __name__ == "__main__":
    unittest.main()
