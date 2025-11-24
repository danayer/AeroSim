#!/usr/bin/env python3
"""
Примеры использования виджетов мониторинга AeroSim EDU
"""

# Пример 1: Использование ComprehensiveMonitoringWidget
from src.gui.monitoring_widgets import ComprehensiveMonitoringWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QScrollArea

def example_comprehensive_monitoring():
    """Создать окно с полным мониторингом"""
    
    app = QApplication([])
    
    # Создать главное окно
    window = QMainWindow()
    window.setWindowTitle("AeroSim EDU - Комплексный Мониторинг")
    window.setGeometry(100, 100, 1600, 1000)
    
    # Создать виджет мониторинга
    monitoring = ComprehensiveMonitoringWidget()
    
    # Обернуть в scrollable контейнер
    scroll = QScrollArea()
    scroll.setWidget(monitoring)
    scroll.setWidgetResizable(True)
    
    window.setCentralWidget(scroll)
    window.show()
    
    app.exec_()


# Пример 2: Использование отдельных виджетов
from src.gui.monitoring_widgets import (
    AirportResourceWidget,
    PassengerFlowWidget,
    FlightListWidget,
    SystemHealthWidget,
    EventMonitorWidget
)

def example_individual_widgets():
    """Использовать отдельные виджеты"""
    
    app = QApplication([])
    
    window = QMainWindow()
    window.setWindowTitle("AeroSim EDU - Виджеты")
    window.setGeometry(100, 100, 1200, 800)
    
    # Главный контейнер
    central = QWidget()
    layout = QVBoxLayout()
    
    # Добавить виджеты
    layout.addWidget(AirportResourceWidget())
    layout.addWidget(PassengerFlowWidget())
    layout.addWidget(SystemHealthWidget())
    
    central.setLayout(layout)
    window.setCentralWidget(central)
    window.show()
    
    app.exec_()


# Пример 3: Использование с реальным симулятором
from src.core.simulator import AirportSimulator
from src.utils.statistics import StatisticsCollector
from PyQt5.QtCore import QTimer, QThread, pyqtSignal

class MonitoringSimulationThread(QThread):
    """Поток симуляции с мониторингом"""
    
    stats_updated = pyqtSignal(dict)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def run(self):
        """Запустить симуляцию с обновлением статистики"""
        simulator = AirportSimulator(self.config)
        collector = StatisticsCollector()
        
        # Симулировать 10 событий
        for _ in range(10):
            simulator.run_step()  # Обработать один шаг
            stats = collector.collect(simulator)
            self.stats_updated.emit(stats.to_dict())


def example_monitoring_with_simulator():
    """Пример мониторинга с симулятором"""
    
    from src.config.default import DEFAULT_CONFIG
    
    app = QApplication([])
    
    window = QMainWindow()
    window.setWindowTitle("AeroSim EDU - Live Мониторинг")
    window.setGeometry(100, 100, 1400, 900)
    
    # Создать мониторинг
    monitoring = ComprehensiveMonitoringWidget()
    scroll = QScrollArea()
    scroll.setWidget(monitoring)
    scroll.setWidgetResizable(True)
    
    window.setCentralWidget(scroll)
    
    # Запустить симуляцию в отдельном потоке
    sim_thread = MonitoringSimulationThread(DEFAULT_CONFIG)
    sim_thread.stats_updated.connect(lambda stats: print(f"Updated: {stats}"))
    sim_thread.start()
    
    window.show()
    app.exec_()


# Пример 4: Кастомизация виджетов
from src.gui.monitoring_widgets import AirportResourceWidget
from PyQt5.QtWidgets import QVBoxLayout, QLabel
from PyQt5.QtGui import QFont

class CustomAirportMonitor(AirportResourceWidget):
    """Кастомный монитор с дополнительными ресурсами"""
    
    def __init__(self):
        super().__init__()
        # Добавить дополнительные ресурсы
        self.layout().insertWidget(
            self.layout().count() - 1,
            self.create_resource_bar("Аэростанции", 30, 40, "#FFC107")
        )
        self.layout().insertWidget(
            self.layout().count() - 1,
            self.create_resource_bar("Уборка", 25, 30, "#795548")
        )


def example_custom_monitoring():
    """Пример с кастомным монитором"""
    
    app = QApplication([])
    
    window = QMainWindow()
    window.setWindowTitle("AeroSim EDU - Кастомный Мониторинг")
    window.setGeometry(100, 100, 600, 400)
    
    monitor = CustomAirportMonitor()
    window.setCentralWidget(monitor)
    window.show()
    
    app.exec_()


# Пример 5: Интеграция в существующий GUI
def example_integration_with_existing_gui():
    """Интеграция мониторинга в существующий GUI"""
    
    from src.gui.app import run_gui
    
    # Мониторинг автоматически включен в advanced GUI
    # Просто запустите:
    run_gui(advanced=True)


# Пример 6: Обновление данных в мониторинге
class LiveMonitoringWindow(QMainWindow):
    """Окно с живым обновлением данных"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AeroSim EDU - Live Мониторинг")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Создать мониторинг
        self.monitoring = ComprehensiveMonitoringWidget()
        scroll = QScrollArea()
        scroll.setWidget(self.monitoring)
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)
        
        # Таймер для обновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_monitoring_data)
        self.update_timer.start(2000)  # Обновлять каждые 2 сек
    
    def update_monitoring_data(self):
        """Обновить данные мониторинга"""
        # Здесь можно обновить данные из симулятора
        # например, обновить таблицы, полосы прогресса и т.д.
        pass


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        
        if example == "comprehensive":
            example_comprehensive_monitoring()
        elif example == "individual":
            example_individual_widgets()
        elif example == "simulator":
            example_monitoring_with_simulator()
        elif example == "custom":
            example_custom_monitoring()
        elif example == "integration":
            example_integration_with_existing_gui()
        else:
            print("Неизвестный пример:", example)
    else:
        print("""
        Примеры использования виджетов мониторинга:
        
        1. Полный мониторинг:
           python3 monitoring_examples.py comprehensive
        
        2. Отдельные виджеты:
           python3 monitoring_examples.py individual
        
        3. С симулятором:
           python3 monitoring_examples.py simulator
        
        4. Кастомный мониторинг:
           python3 monitoring_examples.py custom
        
        5. Интеграция:
           python3 monitoring_examples.py integration
        """)
