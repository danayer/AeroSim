"""
База данных для сохранения результатов симуляции
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from src.utils.logger import get_logger


class SimulationDatabase:
    """База данных для результатов симуляции"""
    
    def __init__(self, db_path: str = "results/aerosim.db"):
        """
        Инициализация БД
        
        Args:
            db_path: Путь к файлу БД
        """
        self.logger = get_logger(__name__)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.connection = None
        self._connect()
        self._initialize_tables()
    
    def _connect(self):
        """Подключиться к БД"""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            self.logger.info(f"Подключение к БД: {self.db_path}")
        except Exception as e:
            self.logger.error(f"Ошибка подключения к БД: {e}")
            raise
    
    def _initialize_tables(self):
        """Инициализировать таблицы"""
        cursor = self.connection.cursor()
        
        # Таблица симуляций
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                duration REAL,
                total_events INTEGER,
                total_aircraft INTEGER,
                total_passengers INTEGER,
                total_delays REAL,
                runway_utilization REAL,
                gate_utilization REAL,
                config TEXT
            )
        """)
        
        # Таблица событий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id INTEGER,
                event_time REAL,
                event_type TEXT,
                entity_id TEXT,
                data TEXT,
                FOREIGN KEY (simulation_id) REFERENCES simulations(id)
            )
        """)
        
        # Таблица самолетов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aircraft (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id INTEGER,
                aircraft_id TEXT,
                aircraft_type TEXT,
                arrival_time REAL,
                departure_time REAL,
                delay REAL,
                passengers INTEGER,
                FOREIGN KEY (simulation_id) REFERENCES simulations(id)
            )
        """)
        
        # Таблица пассажиров
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passengers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id INTEGER,
                passenger_id TEXT,
                flight_id TEXT,
                status TEXT,
                arrival_time REAL,
                departure_time REAL,
                wait_time REAL,
                FOREIGN KEY (simulation_id) REFERENCES simulations(id)
            )
        """)
        
        self.connection.commit()
        self.logger.info("Таблицы инициализированы")
    
    def save_simulation(self, stats: Dict[str, Any], config: Dict = None) -> int:
        """
        Сохранить результаты симуляции
        
        Args:
            stats: Словарь со статистикой
            config: Конфигурация симуляции
            
        Returns:
            ID симуляции в БД
        """
        import json
        
        cursor = self.connection.cursor()
        
        config_json = json.dumps(config or {})
        
        cursor.execute("""
            INSERT INTO simulations 
            (duration, total_events, total_aircraft, total_passengers, 
             total_delays, runway_utilization, gate_utilization, config)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stats.get('simulation_time', 0),
            stats.get('total_events_processed', 0),
            stats.get('total_aircraft', 0),
            stats.get('total_passengers', 0),
            stats.get('total_delays', 0),
            stats.get('runway_utilization_percent', 0),
            stats.get('gate_utilization_percent', 0),
            config_json
        ))
        
        self.connection.commit()
        simulation_id = cursor.lastrowid
        
        self.logger.info(f"Симуляция сохранена с ID: {simulation_id}")
        return simulation_id
    
    def save_events(self, simulation_id: int, events: List[Dict]):
        """
        Сохранить события симуляции
        
        Args:
            simulation_id: ID симуляции
            events: Список событий
        """
        import json
        
        cursor = self.connection.cursor()
        
        for event in events:
            cursor.execute("""
                INSERT INTO events 
                (simulation_id, event_time, event_type, entity_id, data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                simulation_id,
                event.get('time', 0),
                event.get('type', 'UNKNOWN'),
                event.get('entity_id', ''),
                json.dumps(event.get('data', {}))
            ))
        
        self.connection.commit()
        self.logger.info(f"Сохранено {len(events)} событий")
    
    def get_simulation(self, simulation_id: int) -> Dict:
        """Получить результаты симуляции"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM simulations WHERE id = ?", (simulation_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_simulations(self) -> List[Dict]:
        """Получить все симуляции"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM simulations ORDER BY timestamp DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_events(self, simulation_id: int) -> List[Dict]:
        """Получить события симуляции"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM events WHERE simulation_id = ? ORDER BY event_time",
            (simulation_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self, simulation_id: int) -> Dict:
        """Получить статистику симуляции"""
        sim = self.get_simulation(simulation_id)
        if not sim:
            return None
        
        return {
            'id': sim['id'],
            'timestamp': sim['timestamp'],
            'duration': sim['duration'],
            'total_events': sim['total_events'],
            'total_aircraft': sim['total_aircraft'],
            'total_passengers': sim['total_passengers'],
            'total_delays': sim['total_delays'],
            'runway_utilization': sim['runway_utilization'],
            'gate_utilization': sim['gate_utilization'],
        }
    
    def delete_simulation(self, simulation_id: int) -> bool:
        """Удалить симуляцию"""
        cursor = self.connection.cursor()
        
        cursor.execute("DELETE FROM events WHERE simulation_id = ?", (simulation_id,))
        cursor.execute("DELETE FROM aircraft WHERE simulation_id = ?", (simulation_id,))
        cursor.execute("DELETE FROM passengers WHERE simulation_id = ?", (simulation_id,))
        cursor.execute("DELETE FROM simulations WHERE id = ?", (simulation_id,))
        
        self.connection.commit()
        self.logger.info(f"Симуляция {simulation_id} удалена")
        return True
    
    def close(self):
        """Закрыть подключение"""
        if self.connection:
            self.connection.close()
            self.logger.info("Подключение к БД закрыто")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
