#!/usr/bin/env python3
"""
Быстрый старт: Мониторинг в AeroSim EDU
"""

# ============================================================================
# ВАРИАНТ 1: ЗАПУСК GUI С МОНИТОРИНГОМ (САМЫЙ ПРОСТОЙ)
# ============================================================================

"""
Выполните в терминале:

    python3 aerosim_edu.py --gui

Затем:
1. Нажмите "▶ Запустить"
2. Перейдите на вкладку "📡 Мониторинг"
3. Наблюдайте данные в реальном времени
"""


# ============================================================================
# ВАРИАНТ 2: ИСПОЛЬЗОВАНИЕ МОНИТОРИНГА В КОДЕ
# ============================================================================

from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea
from src.gui.monitoring_widgets import ComprehensiveMonitoringWidget

def example_1():
    """Создать окно с полным мониторингом"""
    app = QApplication([])
    
    window = QMainWindow()
    window.setWindowTitle("AeroSim EDU - Мониторинг")
    window.setGeometry(100, 100, 1600, 1000)
    
    # Создать мониторинг
    monitoring = ComprehensiveMonitoringWidget()
    
    # Обернуть в scroll
    scroll = QScrollArea()
    scroll.setWidget(monitoring)
    scroll.setWidgetResizable(True)
    
    window.setCentralWidget(scroll)
    window.show()
    
    app.exec_()


# ============================================================================
# ВАРИАНТ 3: ИСПОЛЬЗОВАНИЕ ОТДЕЛЬНЫХ ВИДЖЕТОВ
# ============================================================================

from src.gui.monitoring_widgets import (
    AirportResourceWidget,
    PassengerFlowWidget,
    FlightListWidget,
    SystemHealthWidget,
    EventMonitorWidget
)

def example_2():
    """Использовать отдельные виджеты"""
    app = QApplication([])
    
    # Создать окно
    window = QMainWindow()
    window.setWindowTitle("Ресурсы")
    window.setGeometry(100, 100, 800, 600)
    
    # Добавить виджет ресурсов
    window.setCentralWidget(AirportResourceWidget())
    window.show()
    
    app.exec_()


# ============================================================================
# ВАРИАНТ 4: КОМБИНИРОВАНИЕ ВИДЖЕТОВ
# ============================================================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

def example_3():
    """Комбинировать несколько виджетов"""
    app = QApplication([])
    
    window = QMainWindow()
    window.setWindowTitle("Многокомпонентный Мониторинг")
    window.setGeometry(100, 100, 1400, 800)
    
    # Главный контейнер
    central = QWidget()
    layout = QHBoxLayout()
    
    # Левая колонка
    left = QVBoxLayout()
    left.addWidget(AirportResourceWidget())
    left.addWidget(PassengerFlowWidget())
    
    # Правая колонка
    right = QVBoxLayout()
    right.addWidget(SystemHealthWidget())
    right.addWidget(EventMonitorWidget())
    
    layout.addLayout(left, 1)
    layout.addLayout(right, 1)
    
    central.setLayout(layout)
    window.setCentralWidget(central)
    window.show()
    
    app.exec_()


# ============================================================================
# ВАРИАНТ 5: С РЕАЛЬНЫМ СИМУЛЯТОРОМ
# ============================================================================

from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from src.core.simulator import AirportSimulator
from src.config.default import DEFAULT_CONFIG

class SimulationWorker(QThread):
    """Поток для симуляции"""
    status_changed = pyqtSignal(str)
    
    def run(self):
        """Запустить симуляцию"""
        try:
            self.status_changed.emit("Инициализация...")
            simulator = AirportSimulator(DEFAULT_CONFIG)
            
            self.status_changed.emit("Запуск...")
            simulator.run()
            
            self.status_changed.emit("Завершено!")
        except Exception as e:
            self.status_changed.emit(f"Ошибка: {e}")

def example_4():
    """Мониторинг с реальным симулятором"""
    app = QApplication([])
    
    window = QMainWindow()
    window.setWindowTitle("Live Мониторинг")
    window.setGeometry(100, 100, 1600, 1000)
    
    # Создать мониторинг
    monitoring = ComprehensiveMonitoringWidget()
    scroll = QScrollArea()
    scroll.setWidget(monitoring)
    scroll.setWidgetResizable(True)
    window.setCentralWidget(scroll)
    
    # Запустить симуляцию в отдельном потоке
    worker = SimulationWorker()
    worker.start()
    
    # Логирование
    def on_status_changed(msg):
        print(f"[SIM] {msg}")
    
    worker.status_changed.connect(on_status_changed)
    
    window.show()
    app.exec_()


# ============================================================================
# ВАРИАНТ 6: ИНТЕГРАЦИЯ В СУЩЕСТВУЮЩЕЕ ПРИЛОЖЕНИЕ
# ============================================================================

def example_5():
    """Добавить мониторинг к существующему приложению"""
    from PyQt5.QtWidgets import QTabWidget
    
    # Ваше существующее приложение
    app = QApplication([])
    window = QMainWindow()
    
    # Создать табы
    tabs = QTabWidget()
    
    # Ваши существующие вкладки...
    # tabs.addTab(your_widget, "Мой таб")
    
    # Добавить мониторинг
    monitoring = ComprehensiveMonitoringWidget()
    scroll = QScrollArea()
    scroll.setWidget(monitoring)
    scroll.setWidgetResizable(True)
    tabs.addTab(scroll, "📡 Мониторинг")
    
    window.setCentralWidget(tabs)
    window.show()
    
    app.exec_()


# ============================================================================
# ВАРИАНТ 7: КАСТОМИЗАЦИЯ И РАСШИРЕНИЕ
# ============================================================================

from src.gui.monitoring_widgets import AirportResourceWidget

class CustomMonitoringWidget(AirportResourceWidget):
    """Расширенный мониторинг"""
    
    def __init__(self):
        super().__init__()
        self.add_custom_metrics()
    
    def add_custom_metrics(self):
        """Добавить кастомные метрики"""
        layout = self.layout()
        
        # Добавить новые ресурсы
        layout.insertWidget(
            layout.count() - 1,
            self.create_resource_bar("Заправка", 40, 50, "#FFC107")
        )
        layout.insertWidget(
            layout.count() - 1,
            self.create_resource_bar("Уборка", 30, 40, "#795548")
        )

def example_6():
    """Использовать кастомизированный мониторинг"""
    app = QApplication([])
    
    window = QMainWindow()
    window.setWindowTitle("Кастомный Мониторинг")
    window.setGeometry(100, 100, 800, 600)
    
    window.setCentralWidget(CustomMonitoringWidget())
    window.show()
    
    app.exec_()


# ============================================================================
# ВАРИАНТ 8: АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ ДАННЫХ
# ============================================================================

from PyQt5.QtCore import QTimer

def example_7():
    """Автоматическое обновление данных"""
    app = QApplication([])
    
    window = QMainWindow()
    window.setWindowTitle("Auto-Update Мониторинг")
    window.setGeometry(100, 100, 1600, 1000)
    
    monitoring = ComprehensiveMonitoringWidget()
    scroll = QScrollArea()
    scroll.setWidget(monitoring)
    scroll.setWidgetResizable(True)
    window.setCentralWidget(scroll)
    
    # Таймер для обновления
    timer = QTimer()
    timer.timeout.connect(lambda: print("Обновление данных..."))
    timer.start(2000)  # Обновлять каждые 2 секунды
    
    window.show()
    app.exec_()


# ============================================================================
# СПРАВКА ПО КОМПОНЕНТАМ
# ============================================================================

MONITORING_COMPONENTS = """
📡 КОМПОНЕНТЫ МОНИТОРИНГА
═══════════════════════════════════════════════════════════════════

1. 🏛️ AirportResourceWidget
   └─ Мониторит основные ресурсы аэропорта
   └─ Показывает: ВПП, Гейты, Персонал, Оборудование
   └─ Использование: 40% графических компонентов

2. 👥 PassengerFlowWidget
   └─ Отслеживает пассажиров по статусам
   └─ Показывает: Таблица статусов, Статистика очередей
   └─ Использование: Анализ загруженности терминала

3. ✈️ FlightListWidget
   └─ Текущий список всех полетов
   └─ Показывает: Номер рейса, Статус, Задержка, Ресурсы
   └─ Использование: Управление расписанием

4. 🏥 SystemHealthWidget
   └─ Здоровье всей системы
   └─ Показывает: 5 ключевых индикаторов нагрузки
   └─ Использование: Быстрая диагностика проблем

5. 📡 EventMonitorWidget
   └─ Логирование всех событий в реальном времени
   └─ Показывает: Временные метки, Типы, Статусы
   └─ Использование: Отладка и анализ

6. 🎯 ComprehensiveMonitoringWidget
   └─ Все компоненты вместе в одном окне
   └─ Показывает: Полный обзор аэропорта
   └─ Использование: Главный контрольный центр

ЦВЕТОВАЯ СХЕМА
═══════════════════════════════════════════════════════════════════
🔵 Голубой (#2196F3)  - ВПП (критично)
🟠 Оранжевый (#FF9800) - Гейты (важно)
🟢 Зеленый (#4CAF50)   - Персонал (хорошо)
🟣 Фиолетовый (#9C27B0) - Оборудование (служебное)
🔴 Красный (#F44336)   - Задержки (критично)
🔵 Голубой (#2196F3)   - Здоровье (информативно)
🟤 Коричневый (#795548) - Дополнительно (служебное)
🟣 Фиолетовый (#9C27B0) - Использование (метрика)

ЗАПУСК
═══════════════════════════════════════════════════════════════════
# Быстрый старт (самый простой)
python3 aerosim_edu.py --gui

# С опциями
python3 aerosim_edu.py --gui --verbose
python3 aerosim_edu.py --gui --duration 1800

# Примеры программистам
python3 src/gui/monitoring_examples.py comprehensive
python3 src/gui/monitoring_examples.py individual
python3 src/gui/monitoring_examples.py simulator
python3 src/gui/monitoring_examples.py custom

ДОКУМЕНТАЦИЯ
═══════════════════════════════════════════════════════════════════
docs/MONITORING_WIDGETS.md     - Полное описание виджетов
docs/ADVANCED_FEATURES.md      - Расширенные возможности
docs/CODE_STATISTICS.md        - Статистика проекта
README.md                      - Главный readme
"""

# ============================================================================
# ЗАПУСК ПРИМЕРОВ
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        
        examples = {
            "1": example_1,
            "2": example_2,
            "3": example_3,
            "4": example_4,
            "5": example_5,
            "6": example_6,
            "7": example_7,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(MONITORING_COMPONENTS)
    else:
        print(MONITORING_COMPONENTS)
        print("\nЗапуск примера: python3 quickstart_monitoring.py <номер>")
        print("Например: python3 quickstart_monitoring.py 1")
