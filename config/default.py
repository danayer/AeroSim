"""
Конфигурация по умолчанию для AeroSim EDU
"""

DEFAULT_CONFIG = {
    "duration": 3600,  # 1 час в секундах
    "airport": {
        "id": "AIRPORT_SIM",
        "num_runways": 2,
        "num_terminals": 3,
        "gates_per_terminal": 20,
    },
    "aircraft": {
        "initial_aircraft": 5,
        "arrival_rate": 0.5,  # Самолетов в минуту
        "average_passenger_count": 150,
    },
    "passengers": {
        "checkin_time": 5,  # Минут
        "boarding_time": 30,  # Минут
        "security_time": 10,  # Минут
    },
    "baggage": {
        "unload_time": 15,  # Минут
        "load_time": 15,  # Минут
        "average_baggage_per_passenger": 1.5,
    },
    "maintenance": {
        "maintenance_probability": 0.1,  # 10%
        "maintenance_duration": 60,  # Минут
    },
    "logging": {
        "level": "INFO",
        "format": "[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    }
}
