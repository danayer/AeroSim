"""
Виджет мониторинга пассажиров и терминала
Показывает:
- Статистику по пассажирам (входило, посажено, пропустило)
- Размеры очередей
- Использование контрольных точек
- История перемещения пассажиров
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QGridLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from typing import Dict, Any, Optional


class PassengerMonitoringWidget(QWidget):
    """Виджет для мониторинга пассажиров в терминале"""
    
    def __init__(self):
        super().__init__()
        self.progress_bars = {}
        self.labels = {}
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("👥 МОНИТОРИНГ ПАССАЖИРОВ")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Статистика пассажиров (сверху)
        stats_layout = QGridLayout()
        
        # Всего пассажиров
        self.labels['total'] = QLabel("0")
        self.labels['total'].setFont(QFont("Arial", 14, QFont.Bold))
        stats_layout.addWidget(QLabel("Пассажиров:"), 0, 0)
        stats_layout.addWidget(self.labels['total'], 0, 1)
        
        # Посажено
        self.labels['boarded'] = QLabel("0")
        self.labels['boarded'].setFont(QFont("Arial", 14, QFont.Bold))
        self.labels['boarded'].setStyleSheet("color: #4CAF50")
        stats_layout.addWidget(QLabel("Посажено:"), 0, 2)
        stats_layout.addWidget(self.labels['boarded'], 0, 3)
        
        # Пропустило
        self.labels['missed'] = QLabel("0")
        self.labels['missed'].setFont(QFont("Arial", 14, QFont.Bold))
        self.labels['missed'].setStyleSheet("color: #FF6B6B")
        stats_layout.addWidget(QLabel("Пропустило:"), 0, 4)
        stats_layout.addWidget(self.labels['missed'], 0, 5)
        
        # Время ожидания
        self.labels['avg_wait'] = QLabel("0.0s")
        stats_layout.addWidget(QLabel("Ср. ожидание:"), 1, 0)
        stats_layout.addWidget(self.labels['avg_wait'], 1, 1)
        
        # Процент пропусков
        self.labels['miss_percent'] = QLabel("0%")
        self.labels['miss_percent'].setStyleSheet("color: #FF6B6B")
        stats_layout.addWidget(QLabel("% пропусков:"), 1, 2)
        stats_layout.addWidget(self.labels['miss_percent'], 1, 3)
        
        layout.addLayout(stats_layout)
        layout.addWidget(self._create_separator())
        
        # Очереди (посередине)
        queue_group = QGroupBox("📋 ОЧЕРЕДИ")
        queue_layout = QGridLayout()
        
        # Багажный контроль
        queue_layout.addWidget(QLabel("Багажный контроль:"), 0, 0)
        self.labels['luggage_queue'] = QLabel("0")
        queue_layout.addWidget(self.labels['luggage_queue'], 0, 1)
        
        # Паспортный контроль
        queue_layout.addWidget(QLabel("Паспортный контроль:"), 1, 0)
        self.labels['security_queue'] = QLabel("0")
        queue_layout.addWidget(self.labels['security_queue'], 1, 1)
        
        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)
        layout.addWidget(self._create_separator())
        
        # Использование ресурсов (снизу)
        resources_group = QGroupBox("⚙️ ИСПОЛЬЗОВАНИЕ РЕСУРСОВ")
        resources_layout = QGridLayout()
        
        # Багажный контроль
        resources_layout.addWidget(QLabel("Багажный контроль:"), 0, 0)
        self.progress_bars['luggage'] = QProgressBar()
        self.progress_bars['luggage'].setStyleSheet(self._get_progress_style("#FF9800"))
        resources_layout.addWidget(self.progress_bars['luggage'], 0, 1)
        self.labels['luggage_util'] = QLabel("0%")
        resources_layout.addWidget(self.labels['luggage_util'], 0, 2)
        
        # Паспортный контроль
        resources_layout.addWidget(QLabel("Паспортный контроль:"), 1, 0)
        self.progress_bars['security'] = QProgressBar()
        self.progress_bars['security'].setStyleSheet(self._get_progress_style("#2196F3"))
        resources_layout.addWidget(self.progress_bars['security'], 1, 1)
        self.labels['security_util'] = QLabel("0%")
        resources_layout.addWidget(self.labels['security_util'], 1, 2)
        
        resources_group.setLayout(resources_layout)
        layout.addWidget(resources_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_passenger_stats(self, stats: Dict[str, Any]) -> None:
        """
        Обновить статистику пассажиров
        
        Args:
            stats: Словарь со статистикой от терминала
        """
        terminal_stats = stats.get('terminal_stats', {})
        
        # Обновить метрики
        self.labels['total'].setText(str(terminal_stats.get('total_passengers', 0)))
        self.labels['boarded'].setText(str(terminal_stats.get('boarded', 0)))
        self.labels['missed'].setText(str(terminal_stats.get('missed_flights', 0)))
        
        # Среднее время ожидания
        avg_wait = terminal_stats.get('avg_wait_time', 0)
        self.labels['avg_wait'].setText(f"{avg_wait:.1f}s")
        
        # Процент пропусков
        total = terminal_stats.get('total_passengers', 0)
        missed = terminal_stats.get('missed_flights', 0)
        if total > 0:
            percent = (missed / total) * 100
            self.labels['miss_percent'].setText(f"{percent:.1f}%")
        else:
            self.labels['miss_percent'].setText("0%")
        
        # Размеры очередей
        self.labels['luggage_queue'].setText(str(stats.get('luggage_queue_size', 0)))
        self.labels['security_queue'].setText(str(stats.get('security_queue_size', 0)))
        
        # Использование ресурсов
        luggage_util = stats.get('luggage_utilization', 0)
        security_util = stats.get('security_utilization', 0)
        
        self.progress_bars['luggage'].setValue(int(luggage_util))
        self.labels['luggage_util'].setText(f"{luggage_util:.1f}%")
        
        self.progress_bars['security'].setValue(int(security_util))
        self.labels['security_util'].setText(f"{security_util:.1f}%")
    
    @staticmethod
    def _create_separator() -> QFrame:
        """Создать горизонтальный разделитель"""
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        return sep
    
    @staticmethod
    def _get_progress_style(color: str) -> str:
        """Получить CSS для progress bar"""
        return f"""
        QProgressBar {{
            border: 2px solid #cccccc;
            border-radius: 5px;
            background-color: #f0f0f0;
            height: 20px;
        }}
        QProgressBar::chunk {{
            background-color: {color};
        }}
        """


class TerminalQueuesWidget(QWidget):
    """Виджет для отображения очередей в реальном времени"""
    
    def __init__(self):
        super().__init__()
        self.queue_tables = {}
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        layout = QHBoxLayout()
        
        # Очередь к багажному контролю
        luggage_group = QGroupBox("👜 Очередь к багажному контролю")
        luggage_layout = QVBoxLayout()
        
        self.queue_tables['luggage'] = QTableWidget()
        self.queue_tables['luggage'].setColumnCount(3)
        self.queue_tables['luggage'].setHorizontalHeaderLabels(
            ['ID Пассажира', 'Рейс', 'Вылет (s)']
        )
        self.queue_tables['luggage'].setMaximumHeight(150)
        luggage_layout.addWidget(self.queue_tables['luggage'])
        luggage_group.setLayout(luggage_layout)
        layout.addWidget(luggage_group)
        
        # Очередь к паспортному контролю
        security_group = QGroupBox("🛂 Очередь к паспортному контролю")
        security_layout = QVBoxLayout()
        
        self.queue_tables['security'] = QTableWidget()
        self.queue_tables['security'].setColumnCount(3)
        self.queue_tables['security'].setHorizontalHeaderLabels(
            ['ID Пассажира', 'Рейс', 'Вылет (s)']
        )
        self.queue_tables['security'].setMaximumHeight(150)
        security_layout.addWidget(self.queue_tables['security'])
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        self.setLayout(layout)
    
    def update_queues(self, simulator) -> None:
        """
        Обновить отображение очередей
        
        Args:
            simulator: Объект симулятора
        """
        # Обновить очередь к багажному контролю
        luggage_passengers = simulator.terminal.luggage_queue.get_all()
        self.queue_tables['luggage'].setRowCount(len(luggage_passengers))
        
        for i, passenger in enumerate(luggage_passengers):
            self.queue_tables['luggage'].setItem(
                i, 0, QTableWidgetItem(passenger.passenger_id)
            )
            self.queue_tables['luggage'].setItem(
                i, 1, QTableWidgetItem(passenger.flight_id)
            )
            self.queue_tables['luggage'].setItem(
                i, 2, QTableWidgetItem(f"{passenger.flight_time:.0f}")
            )
        
        # Обновить очередь к паспортному контролю
        security_passengers = simulator.terminal.security_queue.get_all()
        self.queue_tables['security'].setRowCount(len(security_passengers))
        
        for i, passenger in enumerate(security_passengers):
            self.queue_tables['security'].setItem(
                i, 0, QTableWidgetItem(passenger.passenger_id)
            )
            self.queue_tables['security'].setItem(
                i, 1, QTableWidgetItem(passenger.flight_id)
            )
            self.queue_tables['security'].setItem(
                i, 2, QTableWidgetItem(f"{passenger.flight_time:.0f}")
            )


class PassengerFlowWidget(QWidget):
    """Виджет для визуализации потока пассажиров"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("🔄 ПОТОК ПАССАЖИРОВ")
        title.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(title)
        
        # Этапы обработки
        flow_layout = QGridLayout()
        
        stages = [
            ("ВХОД", "Пассажиры входят в терминал"),
            ("БАГАЖ", "Багажный контроль"),
            ("БЕЗОП", "Паспортный контроль"),
            ("ПОСАДКА", "Посадка на борт"),
            ("ВЫЛЕТ", "Вылет")
        ]
        
        self.stage_labels = {}
        for i, (stage_name, description) in enumerate(stages):
            # Название этапа
            stage_label = QLabel(stage_name)
            stage_label.setFont(QFont("Arial", 10, QFont.Bold))
            stage_label.setStyleSheet("background-color: #e0e0e0; padding: 5px; border-radius: 3px;")
            stage_label.setAlignment(Qt.AlignCenter)
            flow_layout.addWidget(stage_label, 0, i)
            
            # Количество пассажиров на этапе
            count_label = QLabel("0")
            count_label.setFont(QFont("Arial", 12, QFont.Bold))
            count_label.setAlignment(Qt.AlignCenter)
            self.stage_labels[stage_name] = count_label
            flow_layout.addWidget(count_label, 1, i)
            
            # Описание (попутно)
            if i < len(stages) - 1:
                arrow = QLabel("→")
                arrow.setFont(QFont("Arial", 14, QFont.Bold))
                arrow.setAlignment(Qt.AlignCenter)
                flow_layout.addWidget(arrow, 0, i + 0.5)
        
        layout.addLayout(flow_layout)
        layout.addStretch()
        self.setLayout(layout)
    
    def update_flow(self, stats: Dict[str, Any]) -> None:
        """
        Обновить статистику потока
        
        Args:
            stats: Статистика симулятора
        """
        terminal_stats = stats.get('terminal_stats', {})
        
        # Примерное распределение пассажиров на разных этапах
        total = terminal_stats.get('total_passengers', 0)
        boarded = terminal_stats.get('boarded', 0)
        
        # Упрощенное распределение
        if total > 0:
            self.stage_labels['ВХОД'].setText(str(total))
            self.stage_labels['БАГАЖ'].setText(str(int(total * 0.8)))
            self.stage_labels['БЕЗОП'].setText(str(int(total * 0.7)))
            self.stage_labels['ПОСАДКА'].setText(str(boarded))
            self.stage_labels['ВЫЛЕТ'].setText(str(boarded))
