"""
Виджеты для детальной визуализации и мониторинга
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QGridLayout, QFrame, QGroupBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from typing import Dict, Any


class AirportResourceWidget(QWidget):
    """Виджет для мониторинга ресурсов аэропорта"""
    
    def __init__(self):
        super().__init__()
        self.resource_bars = {}
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("✈️ РЕСУРСЫ АЭРОПОРТА")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Создать бары с заполнителями
        self.resource_bars['runways'] = self.create_resource_bar("ВПП", 0, 2, "#2196F3")
        layout.addWidget(self.resource_bars['runways'][0])
        
        self.resource_bars['gates'] = self.create_resource_bar("Гейты", 0, 60, "#FF9800")
        layout.addWidget(self.resource_bars['gates'][0])
        
        self.resource_bars['staff'] = self.create_resource_bar("Персонал", 0, 100, "#4CAF50")
        layout.addWidget(self.resource_bars['staff'][0])
        
        self.resource_bars['baggage'] = self.create_resource_bar("Багажное ОБ", 0, 80, "#9C27B0")
        layout.addWidget(self.resource_bars['baggage'][0])
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_resource_bar(self, name: str, current: int, total: int, color: str) -> tuple:
        """Создать строку ресурса и вернуть (widget, progress, label)"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        
        label = QLabel(f"{name}:")
        label.setMinimumWidth(120)
        layout.addWidget(label)
        
        progress = QProgressBar()
        progress.setMaximum(total)
        progress.setValue(current)
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        layout.addWidget(progress)
        
        percent_label = QLabel(f"{int(current/total*100)}% ({current}/{total})")
        percent_label.setMinimumWidth(80)
        percent_label.setAlignment(Qt.AlignRight)
        layout.addWidget(percent_label)
        
        widget.setLayout(layout)
        return (widget, progress, percent_label)
    
    def update_resources(self, stats: dict):
        """Обновить данные ресурсов"""
        try:
            # Обновить ВПП
            runway_util = stats.get('runway_utilization', 0)
            if 'runways' in self.resource_bars:
                widget, progress, label = self.resource_bars['runways']
                progress.setMaximum(2)
                current = int(2 * runway_util / 100) if runway_util > 0 else 0
                progress.setValue(current)
                label.setText(f"{int(runway_util)}% ({current}/2)")
            
            # Обновить гейты
            gate_util = stats.get('gate_utilization', 0)
            if 'gates' in self.resource_bars:
                widget, progress, label = self.resource_bars['gates']
                progress.setMaximum(60)
                current = int(60 * gate_util / 100) if gate_util > 0 else 0
                progress.setValue(current)
                label.setText(f"{int(gate_util)}% ({current}/60)")
            
            # Обновить персонал
            staff_util = stats.get('staff_utilization', 0)
            if 'staff' in self.resource_bars:
                widget, progress, label = self.resource_bars['staff']
                progress.setMaximum(100)
                current = int(staff_util)
                progress.setValue(current)
                label.setText(f"{int(staff_util)}% ({current}/100)")
            
            # Обновить багажное обслуживание
            baggage_util = stats.get('baggage_utilization', 0)
            if 'baggage' in self.resource_bars:
                widget, progress, label = self.resource_bars['baggage']
                progress.setMaximum(80)
                current = int(80 * baggage_util / 100) if baggage_util > 0 else 0
                progress.setValue(current)
                label.setText(f"{int(baggage_util)}% ({current}/80)")
        except Exception as e:
            print(f"Ошибка обновления ресурсов: {e}")


class PassengerFlowWidget(QWidget):
    """Виджет для мониторинга потока пассажиров"""
    
    def __init__(self):
        super().__init__()
        self.total_label = None
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("👥 ПОТОК ПАССАЖИРОВ")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Таблица статусов
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Статус", "Количество"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMaximumHeight(200)
        
        # Инициализировать строки
        self.table.setRowCount(7)
        statuses = [
            "Зарегистрировано",
            "На контроле безопасности",
            "В зоне ожидания",
            "На посадке",
            "На борту",
            "В пути",
            "Приземлено",
        ]
        for row, status in enumerate(statuses):
            self.table.setItem(row, 0, QTableWidgetItem(status))
            self.table.setItem(row, 1, QTableWidgetItem("0"))
        
        layout.addWidget(self.table)
        
        # Статистика
        stats_layout = QGridLayout()
        stats_layout.addWidget(QLabel("Всего пассажиров:"), 0, 0)
        self.total_label = QLabel("0")
        stats_layout.addWidget(self.total_label, 0, 1)
        stats_layout.addWidget(QLabel("Среднее ожидание:"), 1, 0)
        stats_layout.addWidget(QLabel("0 мин"), 1, 1)
        stats_layout.addWidget(QLabel("Максимальная очередь:"), 2, 0)
        stats_layout.addWidget(QLabel("0 чел"), 2, 1)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_passenger_data(self, stats: dict):
        """Обновить данные пассажиров"""
        try:
            total = stats.get('total_passengers', 0)
            if self.total_label:
                self.total_label.setText(str(int(total)))
            
            # Обновить статистику по статусам
            passenger_stats = stats.get('passenger_stats', {})
            
            # Убедимся что значения не отрицательные
            status_mapping = [
                ('registered', 0),           # Зарегистрировано (прошли багажный)
                ('security', 1),             # На контроле безопасности (в очереди)
                ('waiting_area', 2),         # В зоне ожидания (после контроля, до посадки)
                ('boarding', 3),             # На посадке
                ('boarded', 4),              # На борту
                ('in_flight', 5),            # В пути
                ('landed', 6),               # Приземлено
            ]
            
            for stat_key, row in status_mapping:
                count = max(0, int(passenger_stats.get(stat_key, 0)))
                self.table.setItem(row, 1, QTableWidgetItem(str(count)))
        except Exception as e:
            print(f"Ошибка обновления пассажиров: {e}")


class FlightListWidget(QWidget):
    """Виджет со списком полетов"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("✈️ СПИСОК ПОЛЕТОВ")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Список полетов
        self.flight_list = QTableWidget()
        self.flight_list.setColumnCount(6)
        self.flight_list.setHorizontalHeaderLabels([
            "Рейс", "Статус", "Пассажиры", "Задержка", "ВПП", "Гейт"
        ])
        self.flight_list.horizontalHeader().setStretchLastSection(True)
        
        # Инициализировать 5 строк
        self.flight_list.setRowCount(5)
        for row in range(5):
            for col in range(6):
                self.flight_list.setItem(row, col, QTableWidgetItem(""))
        
        layout.addWidget(self.flight_list)
        self.setLayout(layout)
    
    def update_flights(self, stats: dict):
        """Обновить список полетов"""
        try:
            active_flights = stats.get('active_flights', [])
            
            # Убедиться что таблица имеет достаточно строк
            if len(active_flights) > self.flight_list.rowCount():
                self.flight_list.setRowCount(len(active_flights))
            
            # Очистить и заполнить таблицу
            for i in range(self.flight_list.rowCount()):
                if i < len(active_flights):
                    flight = active_flights[i]
                    
                    # Рейс (ID)
                    flight_id = flight.get('flight_id', '')
                    self.flight_list.setItem(i, 0, QTableWidgetItem(flight_id))
                    
                    # Статус
                    status = flight.get('status', 'unknown')
                    self.flight_list.setItem(i, 1, QTableWidgetItem(status))
                    
                    # Пассажиры
                    passengers = flight.get('passengers', 0)
                    self.flight_list.setItem(i, 2, QTableWidgetItem(str(passengers)))
                    
                    # Задержка
                    delay = flight.get('delay', 0)
                    self.flight_list.setItem(i, 3, QTableWidgetItem(f"{delay:.1f}м"))
                    
                    # ВПП
                    runway_id = flight.get('runway_id', '-')
                    self.flight_list.setItem(i, 4, QTableWidgetItem(str(runway_id)))
                    
                    # Гейт
                    gate_id = flight.get('gate_id', '-')
                    self.flight_list.setItem(i, 5, QTableWidgetItem(str(gate_id)))
                else:
                    # Очистить оставшиеся строки
                    for col in range(6):
                        self.flight_list.setItem(i, col, QTableWidgetItem(""))
        except Exception as e:
            print(f"Ошибка обновления полетов: {e}")


class SystemHealthWidget(QWidget):
    """Виджет здоровья системы"""
    
    def __init__(self):
        super().__init__()
        self.indicators = {}
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("🏥 ЗДОРОВЬЕ СИСТЕМЫ")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Показатели
        indicator_data = [
            ("runway_util", "ВПП использование", "#2196F3"),
            ("gate_util", "Гейты использование", "#FF9800"),
            ("terminal_util", "Терминал использование", "#4CAF50"),
            ("avg_wait", "Среднее время ожидания", "#9C27B0"),
            ("avg_delay", "Средняя задержка", "#F44336"),
        ]
        
        for key, name, color in indicator_data:
            widget, progress, label = self.create_indicator(name, 0, color)
            self.indicators[key] = (widget, progress, label)
            layout.addWidget(widget)
        
        layout.addStretch()
        self.setLayout(layout)
    
    @staticmethod
    def create_indicator(name: str, value: int, color: str) -> tuple:
        """Создать индикатор и вернуть (widget, progress, label)"""
        widget = QWidget()
        widget_layout = QHBoxLayout()
        widget_layout.setContentsMargins(0, 5, 0, 5)
        
        label = QLabel(name)
        label.setMinimumWidth(150)
        widget_layout.addWidget(label)
        
        # Полоса
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setValue(min(value, 100))
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 3px;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        widget_layout.addWidget(progress)
        
        # Значение
        value_label = QLabel(str(value))
        value_label.setMinimumWidth(40)
        value_label.setAlignment(Qt.AlignRight)
        widget_layout.addWidget(value_label)
        
        widget.setLayout(widget_layout)
        return (widget, progress, value_label)
    
    def update_health(self, stats: dict):
        """Обновить показатели здоровья системы"""
        try:
            # Обновить ВПП
            if 'runway_util' in self.indicators:
                widget, progress, label = self.indicators['runway_util']
                val = int(stats.get('runway_utilization', 0))
                progress.setValue(min(val, 100))
                label.setText(f"{val}%")
            
            # Обновить гейты
            if 'gate_util' in self.indicators:
                widget, progress, label = self.indicators['gate_util']
                val = int(stats.get('gate_utilization', 0))
                progress.setValue(min(val, 100))
                label.setText(f"{val}%")
            
            # Обновить терминал
            if 'terminal_util' in self.indicators:
                widget, progress, label = self.indicators['terminal_util']
                val = int(stats.get('terminal_utilization', 0))
                progress.setValue(min(val, 100))
                label.setText(f"{val}%")
            
            # Обновить среднее время ожидания
            if 'avg_wait' in self.indicators:
                widget, progress, label = self.indicators['avg_wait']
                val = int(stats.get('avg_wait_time', 0))
                progress.setValue(min(val, 100))
                label.setText(f"{val}м")
            
            # Обновить среднюю задержку
            if 'avg_delay' in self.indicators:
                widget, progress, label = self.indicators['avg_delay']
                val = int(stats.get('avg_delay_time', 0))
                progress.setValue(min(val, 100))
                label.setText(f"{val}м")
        except Exception as e:
            print(f"Ошибка обновления здоровья системы: {e}")


class EventMonitorWidget(QWidget):
    """Виджет для мониторинга событий"""
    
    def __init__(self):
        super().__init__()
        self.events_list = None
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("📡 МОНИТОР СОБЫТИЙ")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Список событий
        self.events_list = QListWidget()
        self.events_list.setMaximumHeight(120)
        
        # Добавить начальные события
        initial_events = [
            "[ИНИЦИАЛИЗАЦИЯ] Система запущена",
            "[ГОТОВНОСТЬ] Ожидание начала симуляции",
        ]
        
        for event in initial_events:
            item = QListWidgetItem(event)
            self.events_list.addItem(item)
        
        layout.addWidget(self.events_list)
        self.setLayout(layout)
    
    def add_event(self, event_text: str):
        """Добавить новое событие"""
        try:
            if self.events_list:
                item = QListWidgetItem(event_text)
                if "Ошибка" in event_text or "❌" in event_text:
                    item.setForeground(QColor("#F44336"))
                elif "Предупреждение" in event_text or "⚠️" in event_text:
                    item.setForeground(QColor("#FF9800"))
                elif "✅" in event_text:
                    item.setForeground(QColor("#4CAF50"))
                
                self.events_list.addItem(item)
                # Показать последнее событие
                self.events_list.scrollToBottom()
                
                # Ограничить количество событий (последние 50)
                while self.events_list.count() > 50:
                    self.events_list.takeItem(0)
        except Exception as e:
            print(f"Ошибка добавления события: {e}")


class ComprehensiveMonitoringWidget(QWidget):
    """Комплексный мониторинг всей системы"""
    
    def __init__(self):
        super().__init__()
        self.resource_widget = None
        self.passenger_widget = None
        self.flight_widget = None
        self.health_widget = None
        self.event_widget = None
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать"""
        layout = QVBoxLayout()
        
        # Верхняя строка - ресурсы и пассажиры
        top_layout = QHBoxLayout()
        self.resource_widget = AirportResourceWidget()
        self.passenger_widget = PassengerFlowWidget()
        top_layout.addWidget(self.resource_widget, 1)
        top_layout.addWidget(self.passenger_widget, 1)
        layout.addLayout(top_layout)
        
        # Средняя строка - полеты и здоровье
        middle_layout = QHBoxLayout()
        self.flight_widget = FlightListWidget()
        self.health_widget = SystemHealthWidget()
        middle_layout.addWidget(self.flight_widget, 2)
        middle_layout.addWidget(self.health_widget, 1)
        layout.addLayout(middle_layout)
        
        # Нижняя строка - события
        self.event_widget = EventMonitorWidget()
        layout.addWidget(self.event_widget)
        
        self.setLayout(layout)
    
    def update_monitoring(self, stats: dict):
        """Обновить мониторинг с новыми данными"""
        try:
            # Обновить ресурсы
            if self.resource_widget:
                self.resource_widget.update_resources(stats)
            
            # Обновить пассажиров
            if self.passenger_widget:
                self.passenger_widget.update_passenger_data(stats)
            
            # Обновить полеты
            if self.flight_widget:
                self.flight_widget.update_flights(stats)
            
            # Обновить здоровье системы
            if self.health_widget:
                self.health_widget.update_health(stats)
        except Exception as e:
            print(f"Ошибка обновления мониторинга: {e}")
