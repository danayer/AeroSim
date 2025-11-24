"""
Расширенный GUI с визуализацией данных для AeroSim EDU
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QSpinBox, QComboBox, QTextEdit,
    QProgressBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QGroupBox, QGridLayout,
    QScrollArea, QFrame, QSplitter, QCheckBox, QSlider, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon, QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
import sys
import json
import time
from datetime import datetime

from src.core.simulator import AirportSimulator
from src.utils.logger import get_logger
from src.utils.export_manager import ExportManager
from src.gui.monitoring_widgets import (
    ComprehensiveMonitoringWidget, AirportResourceWidget,
    PassengerFlowWidget, FlightListWidget, SystemHealthWidget,
    EventMonitorWidget
)
from src.gui.chart_widgets import SystemMetricsChartWidget, MultiSeriesChartWidget, EconomicsChartWidget
from src.gui.passenger_monitoring import (
    PassengerMonitoringWidget, TerminalQueuesWidget, PassengerFlowWidget as PassengerFlowNew
)
from src.gui.math_formulas import MathematicsTabWidget
from src.gui.economics_widget import EconomicsWidget
from src.gui.recommendations_widget import RecommendationsWidget


class SimulationThread(QThread):
    """Поток для выполнения симуляции"""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    status = pyqtSignal(str)
    event_occurred = pyqtSignal(str)
    stats_updated = pyqtSignal(dict)
    event_added = pyqtSignal(dict)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.simulator = None
        self.is_running = True
        self.speed_multiplier = 1.0  # NEW: Множитель скорости
    
    def run(self):
        """Выполнить симуляцию"""
        try:
            self.status.emit("Инициализация симулятора...")
            self.simulator = AirportSimulator(self.config)
            
            self.status.emit("Запуск симуляции...")
            
            # Инициализировать симулятор
            if hasattr(self.simulator, 'initialize'):
                self.simulator.initialize()
            
            # Отправить начальную статистику
            stats = self.simulator.get_statistics()
            stats['simulation_time'] = 0
            self.stats_updated.emit(stats)
            
            # Обработать события
            event_count = 0
            while self.simulator.event_queue.size() > 0 and self.simulator.current_time < self.simulator.end_time:
                if not self.is_running:
                    break
                
                event = self.simulator.event_queue.pop()
                if event:
                    self.simulator.process_event(event)
                    event_count += 1
                    
                    # Отправить информацию о событии - но только каждое 5-е событие чтобы не перегружать
                    if event_count % 5 == 0:
                        event_data = {
                            'time': self.simulator.current_time,
                            'type': event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type),
                            'entity': event.entity_id,
                            'status': 'ok'
                        }
                        self.event_added.emit(event_data)
                    
                    # Добавить задержку на основе множителя скорости (обратная пропорция)
                    # x1.0 = 5ms, x10.0 = 0.5ms
                    delay = max(0.0005, 0.005 / self.speed_multiplier)
                    time.sleep(delay)
                    
                    # Отправлять обновления каждые 15 событий (оптимум: достаточно частое, но не перегружает)
                    if event_count % 15 == 0:
                        stats = self.simulator.get_statistics()
                        stats['simulation_time'] = self.simulator.current_time
                        stats['speed_multiplier'] = self.speed_multiplier
                        self.stats_updated.emit(stats)
                        if event_count % 300 == 0:  # Логирование каждые 300 событий
                            self.status.emit(f"Обработано {event_count} событий | {self.simulator.current_time:.1f}s")
            
            # Финальное обновление
            final_stats = self.simulator.get_statistics()
            final_stats['simulation_time'] = self.simulator.current_time
            final_stats['speed_multiplier'] = self.speed_multiplier
            self.stats_updated.emit(final_stats)
            self.finished.emit(final_stats)
        except Exception as e:
            import traceback
            self.status.emit(f"Ошибка: {str(e)}")
            traceback.print_exc()
    
    def stop(self):
        """Остановить симуляцию"""
        self.is_running = False
    
    def set_speed_multiplier(self, multiplier: float):
        """Установить множитель скорости (для отображения)"""
        self.speed_multiplier = max(0.1, min(10.0, multiplier))


class StatsDisplayWidget(QWidget):
    """Виджет с обновляемыми метриками"""
    
    def __init__(self, title: str, color: str = "#4CAF50"):
        super().__init__()
        self.title_text = title
        self.color = color
        self.value_label = QLabel("0")
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.color};
                border-radius: 5px;
                border: 1px solid #ccc;
            }}
        """)
        
        title = QLabel(self.title_text)
        title.setStyleSheet("color: white; font-size: 11px; font-weight: bold;")
        
        self.value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        layout.addWidget(title)
        layout.addWidget(self.value_label)
        self.setLayout(layout)
    
    def set_value(self, value):
        """Обновить значение"""
        self.value_label.setText(str(value))


class DashboardPanel(QWidget):
    """Панель со статистикой в реальном времени"""
    
    def __init__(self):
        super().__init__()
        self.stats = {}
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("📊 ПАНЕЛЬ УПРАВЛЕНИЯ")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(title)
        
        # Сетка с метриками
        grid = QGridLayout()
        
        self.stats = {
            'events': StatsDisplayWidget("События обработано", "#2196F3"),
            'aircraft': StatsDisplayWidget("Самолетов", "#FF9800"),
            'passengers': StatsDisplayWidget("Пассажиров", "#9C27B0"),
            'delays': StatsDisplayWidget("Задержек (мин)", "#F44336"),
            'runways': StatsDisplayWidget("ВПП используется", "#00BCD4"),
            'gates': StatsDisplayWidget("Гейтов занято", "#4CAF50"),
            'time': StatsDisplayWidget("Время (сек)", "#795548"),
            'utilization': StatsDisplayWidget("Использование", "#673AB7"),
        }
        
        col = 0
        row = 0
        for key, widget in self.stats.items():
            grid.addWidget(widget, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        layout.addLayout(grid)
        layout.addStretch()
        self.setLayout(layout)
    
    def update_stats(self, stats: dict):
        """Обновить статистику"""
        try:
            self.stats['events'].set_value(int(stats.get('total_events_processed', 0)))
            self.stats['aircraft'].set_value(int(stats.get('total_aircraft', 0)))
            self.stats['passengers'].set_value(int(stats.get('total_passengers', 0)))
            self.stats['delays'].set_value(f"{stats.get('total_delays', 0):.1f}")
            self.stats['time'].set_value(f"{stats.get('simulation_time', 0):.1f}")
            self.stats['utilization'].set_value(f"{stats.get('average_utilization', 0):.1f}%")
            self.stats['runways'].set_value(f"{stats.get('runway_utilization', 0):.1f}%")
            self.stats['gates'].set_value(f"{stats.get('gate_utilization', 0):.1f}%")
        except Exception as e:
            print(f"Ошибка обновления статистики: {e}")


class ChartWidget(QWidget):
    """Виджет для отображения графиков"""
    
    def __init__(self, title: str):
        super().__init__()
        self.title_text = title
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel(self.title_text)
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title)
        
        # График
        self.chart = QChart()
        self.chart.setTitle("")
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
    
    def add_bar_data(self, categories: list, values: list, series_name: str):
        """Добавить данные столбцов"""
        # Очистить предыдущие данные
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)
        
        bar_set = QBarSet(series_name)
        bar_set.setColor(QColor("#2196F3"))
        
        for value in values:
            bar_set.append(value)
        
        series = QBarSeries()
        series.append(bar_set)
        
        self.chart.addSeries(series)
        
        # Оси
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max(values) * 1.1 if values else 10)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)


class AdvancedAeroSimMainWindow(QMainWindow):
    """Продвинутое главное окно с визуализацией"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.simulator = None
        self.simulation_thread = None
        self.current_stats = {}
        self.export_manager = ExportManager()
        
        # Отслеживание времени
        self.sim_start_time = None  # Время начала симуляции (реальное)
        self.sim_last_time = 0      # Последнее время симуляции
        self.sim_current_time = 0   # Текущее время симуляции
        
        self.init_ui()
        self.setWindowTitle("AeroSim EDU - Расширенная визуализация")
        self.setGeometry(50, 50, 1600, 1000)
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout()
        
        # Левая панель - управление
        left_panel = self.create_control_panel()
        
        # Центральная область - вкладки
        center_panel = self.create_center_panel()
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
    
    def create_control_panel(self):
        """Создать левую панель управления"""
        
        group = QGroupBox("⚙️ УПРАВЛЕНИЕ")
        layout = QVBoxLayout()
        
        # Параметры
        params_layout = QGridLayout()
        
        params_layout.addWidget(QLabel("Длительность (сек):"), 0, 0)
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(60)
        self.duration_spinbox.setMaximum(86400)
        self.duration_spinbox.setValue(3600)
        params_layout.addWidget(self.duration_spinbox, 0, 1)
        
        params_layout.addWidget(QLabel("ВПП:"), 1, 0)
        self.runways_spinbox = QSpinBox()
        self.runways_spinbox.setMinimum(1)
        self.runways_spinbox.setMaximum(10)
        self.runways_spinbox.setValue(2)
        params_layout.addWidget(self.runways_spinbox, 1, 1)
        
        params_layout.addWidget(QLabel("Терминалы:"), 2, 0)
        self.terminals_spinbox = QSpinBox()
        self.terminals_spinbox.setMinimum(1)
        self.terminals_spinbox.setMaximum(10)
        self.terminals_spinbox.setValue(3)
        params_layout.addWidget(self.terminals_spinbox, 2, 1)
        
        params_layout.addWidget(QLabel("Гейты/терм:"), 3, 0)
        self.gates_spinbox = QSpinBox()
        self.gates_spinbox.setMinimum(5)
        self.gates_spinbox.setMaximum(50)
        self.gates_spinbox.setValue(20)
        params_layout.addWidget(self.gates_spinbox, 3, 1)
        
        params_layout.addWidget(QLabel("Самолеты:"), 4, 0)
        self.aircraft_spinbox = QSpinBox()
        self.aircraft_spinbox.setMinimum(1)
        self.aircraft_spinbox.setMaximum(50)
        self.aircraft_spinbox.setValue(5)
        params_layout.addWidget(self.aircraft_spinbox, 4, 1)
        
        layout.addLayout(params_layout)
        layout.addSpacing(10)
        
        # Режим работы
        self.incidents_checkbox = QCheckBox("⚠️ Форс-мажоры")
        self.incidents_checkbox.setChecked(True)
        self.incidents_checkbox.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.incidents_checkbox)
        
        incidents_hint = QLabel("Добавить случайные сбои,\nзадержки, инциденты")
        incidents_hint.setStyleSheet("font-size: 9px; color: #666; margin-left: 20px;")
        layout.addWidget(incidents_hint)
        
        layout.addSpacing(15)
        
        # Вкладка рекомендаций
        self.recommendations_checkbox = QCheckBox("💡 Вкладка рекомендаций")
        self.recommendations_checkbox.setChecked(False)
        self.recommendations_checkbox.setStyleSheet("font-size: 11px;")
        self.recommendations_checkbox.stateChanged.connect(self.on_recommendations_toggled)
        layout.addWidget(self.recommendations_checkbox)
        
        layout.addSpacing(15)
        
        # Контроль скорости (НОВОЕ)
        speed_group = QGroupBox("⚡ Ускорение")
        speed_layout = QVBoxLayout()
        
        speed_info = QLabel("Множитель скорости:")
        speed_info.setStyleSheet("font-weight: bold;")
        speed_layout.addWidget(speed_info)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)  # 0.1x
        self.speed_slider.setMaximum(100)  # 10x
        self.speed_slider.setValue(10)  # 1x (10/10)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("1.0x (реальное время)")
        self.speed_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        speed_layout.addWidget(self.speed_label)
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        layout.addSpacing(15)
        
        # Кнопки управления - ТОЛЬКО ОДНА ПАРА
        self.start_button = QPushButton("▶ Запустить")
        self.start_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; font-size: 12px;"
        )
        self.start_button.clicked.connect(self.start_simulation)
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹ Остановить")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(
            "background-color: #F44336; color: white; font-weight: bold; padding: 10px; font-size: 12px;"
        )
        self.stop_button.clicked.connect(self.stop_simulation)
        layout.addWidget(self.stop_button)
        
        layout.addSpacing(15)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Статус
        self.status_label = QLabel("Готов")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.status_label)
        
        layout.addSpacing(20)
        
        # Экспорт
        export_label = QLabel("💾 Экспорт:")
        export_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(export_label)
        
        self.export_csv_button = QPushButton("📊 CSV")
        self.export_csv_button.clicked.connect(self.export_csv)
        layout.addWidget(self.export_csv_button)
        
        self.export_json_button = QPushButton("📄 JSON")
        self.export_json_button.clicked.connect(self.export_json)
        layout.addWidget(self.export_json_button)
        
        self.export_xlsx_button = QPushButton("📈 Excel")
        self.export_xlsx_button.clicked.connect(self.export_xlsx)
        layout.addWidget(self.export_xlsx_button)
        
        self.export_pdf_button = QPushButton("🖨️ PDF")
        self.export_pdf_button.clicked.connect(self.export_pdf)
        layout.addWidget(self.export_pdf_button)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_center_panel(self):
        """Создать центральную панель с вкладками"""
        
        tabs = QTabWidget()
        
        # Вкладка 1: Панель управления
        self.dashboard = DashboardPanel()
        tabs.addTab(self.dashboard, "📈 Панель")
        
        # Вкладка 2: События
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(4)
        self.events_table.setHorizontalHeaderLabels(["Время", "Тип", "Сущность", "Статус"])
        self.events_table.horizontalHeader().setStretchLastSection(True)
        tabs.addTab(self.events_table, "🔔 События")
        
        # Вкладка 3: Логи
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        tabs.addTab(self.log_text, "📋 Логи")
        
        # Вкладка 4: Статистика
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Метрика", "Значение"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        tabs.addTab(self.stats_table, "📊 Статистика")
        
        # Вкладка 5: Конфигурация
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        self.config_text.setFont(QFont("Courier", 9))
        tabs.addTab(self.config_text, "⚙️ Конфиг")
        
        # Вкладка 6: Графики
        self.charts_widget = QWidget()
        charts_layout = QVBoxLayout()
        
        # Специализированные графики для метрик системы
        # Получить длительность из spinbox (3600 по умолчанию)
        duration = self.duration_spinbox.value() if hasattr(self, 'duration_spinbox') else 3600
        self.metrics_chart = SystemMetricsChartWidget(initial_duration=float(duration))
        charts_layout.addWidget(self.metrics_chart)
        
        # Графики экономики
        self.economics_chart = EconomicsChartWidget(initial_duration=float(duration))
        charts_layout.addWidget(self.economics_chart)
        
        self.charts_widget.setLayout(charts_layout)
        tabs.addTab(self.charts_widget, "📉 Графики")
        
        # Вкладка 7: Мониторинг
        self.monitoring_widget = ComprehensiveMonitoringWidget()
        scroll = QScrollArea()
        scroll.setWidget(self.monitoring_widget)
        scroll.setWidgetResizable(True)
        tabs.addTab(scroll, "📡 Мониторинг")
        
        # Вкладка 8: Пассажиры
        self.passenger_monitoring = PassengerMonitoringWidget()
        scroll_pass = QScrollArea()
        scroll_pass.setWidget(self.passenger_monitoring)
        scroll_pass.setWidgetResizable(True)
        tabs.addTab(scroll_pass, "👥 Пассажиры")
        
        # Вкладка 9: Очереди
        self.terminal_queues = TerminalQueuesWidget()
        scroll_queues = QScrollArea()
        scroll_queues.setWidget(self.terminal_queues)
        scroll_queues.setWidgetResizable(True)
        tabs.addTab(scroll_queues, "📋 Очереди")
        
        # Вкладка 10: Математика
        self.math_widget = MathematicsTabWidget()
        tabs.addTab(self.math_widget, "📐 Математика")
        
        # Вкладка 11: Экономика (PHASE 6)
        self.economics_widget = EconomicsWidget()
        scroll_econ = QScrollArea()
        scroll_econ.setWidget(self.economics_widget)
        scroll_econ.setWidgetResizable(True)
        tabs.addTab(scroll_econ, "💰 Экономика")
        
        # Вкладка 12: Рекомендации (PHASE 6+)
        self.recommendations_widget = RecommendationsWidget()
        scroll_rec = QScrollArea()
        scroll_rec.setWidget(self.recommendations_widget)
        scroll_rec.setWidgetResizable(True)
        self.recommendations_tab = tabs.addTab(scroll_rec, "💡 Рекомендации")
        tabs.setTabVisible(self.recommendations_tab, False)  # Скрыта по умолчанию
        
        self.tab_widget = tabs
        return tabs
    
    def start_simulation(self):
        """Запустить симуляцию"""
        
        # Сбросить счётчик времени
        self.sim_start_time = None
        
        config = {
            "duration": self.duration_spinbox.value(),
            "airport": {
                "num_runways": self.runways_spinbox.value(),
                "num_terminals": self.terminals_spinbox.value(),
                "gates_per_terminal": self.gates_spinbox.value(),
            },
            "aircraft": {
                "initial_aircraft": self.aircraft_spinbox.value(),
            },
            "enable_incidents": self.incidents_checkbox.isChecked()
        }
        
        # Показать конфигурацию
        self.config_text.setText(json.dumps(config, indent=2, ensure_ascii=False))
        
        # Создать поток
        self.simulation_thread = SimulationThread(config)
        self.simulation_thread.status.connect(self.update_status)
        self.simulation_thread.stats_updated.connect(self.dashboard.update_stats)
        self.simulation_thread.stats_updated.connect(self.monitoring_widget.update_monitoring)
        self.simulation_thread.stats_updated.connect(self.passenger_monitoring.update_passenger_stats)
        self.simulation_thread.stats_updated.connect(self.on_stats_updated)  # NEW: Обновить все элементы с передачей времени
        # self.simulation_thread.event_added.connect(self.add_event_to_table)  # Отключено: снижает нагрузку на CPU
        self.simulation_thread.finished.connect(self.simulation_finished)
        
        # Установить множитель скорости
        speed_mult = self.speed_slider.value() / 10.0  # NEW
        self.simulation_thread.set_speed_multiplier(speed_mult)  # NEW
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.log_text.clear()
        self.events_table.setRowCount(0)
        self.log_text.append(f"🚀 Симуляция запущена (x{speed_mult:.1f})...\n")  # NEW
        
        self.simulation_thread.start()
    
    def on_stats_updated(self, stats: dict):
        """Обновить все элементы при получении новых статистик с временной меткой"""
        simulation_time = stats.get('simulation_time', 0)
        
        # Обновить отображение времени (реальное и симуляции)
        self.update_time_status(simulation_time)
        
        # Обновить экономику на главном виджете
        if hasattr(self, 'economics_widget'):
            self.economics_widget.update_economics(stats)
        
        # Обновить графики с передачей времени
        if hasattr(self, 'metrics_chart'):
            self.metrics_chart.update_metrics(stats, simulation_time)
        
        if hasattr(self, 'economics_chart'):
            self.economics_chart.update_economics(stats, simulation_time)
        
        # Обновить мониторинг
        if hasattr(self, 'monitoring_widget'):
            self.monitoring_widget.update_monitoring(stats)
        
        # Обновить пассажиров
        if hasattr(self, 'passenger_monitoring'):
            self.passenger_monitoring.update_passenger_stats(stats)
        
        # Обновить таблицу очередей в реальном времени
        if hasattr(self, 'terminal_queues') and self.simulation_thread and self.simulation_thread.simulator:
            try:
                self.terminal_queues.update_queues(self.simulation_thread.simulator)
            except Exception as e:
                self.logger.debug(f"Ошибка обновления очередей: {e}")
        
        # Добавить события с информацией о статусе
        if hasattr(self, 'events_table'):
            active_flights = stats.get('active_flights', [])
            if isinstance(active_flights, list):
                flights_count = len(active_flights)
            else:
                flights_count = 0
            
            runway_util = stats.get('runway_utilization', 0)
            gate_util = stats.get('gate_utilization', 0)
            luggage_q = stats.get('luggage_queue_size', 0)
            security_q = stats.get('security_queue_size', 0)
            total_pass = stats.get('total_passengers', 0)
            
            # Добавить событие если что-то происходит
            should_add_event = (runway_util > 0 or gate_util > 0 or luggage_q > 0 or 
                              security_q > 0 or total_pass > 0 or flights_count > 0)
            
            if should_add_event:
                row = self.events_table.rowCount()
                self.events_table.insertRow(row)
                
                time_item = QTableWidgetItem(f"{simulation_time:.1f}s")
                
                # Определить тип события
                if runway_util > 0:
                    event_type = "✈️ Полет"
                elif gate_util > 0:
                    event_type = "🚪 Гейт"
                elif luggage_q > 0:
                    event_type = "🎒 Багаж"
                elif security_q > 0:
                    event_type = "🔒 Контроль"
                else:
                    event_type = "✅ Активность"
                
                type_item = QTableWidgetItem(event_type)
                entity_item = QTableWidgetItem(f"A:{flights_count} P:{int(total_pass)}")
                status_item = QTableWidgetItem("OK")
                
                self.events_table.setItem(row, 0, time_item)
                self.events_table.setItem(row, 1, type_item)
                self.events_table.setItem(row, 2, entity_item)
                self.events_table.setItem(row, 3, status_item)
                
                # Ограничить количество строк (последние 50)
                while self.events_table.rowCount() > 50:
                    self.events_table.removeRow(0)
                
                # Прокрутить в конец
                self.events_table.scrollToBottom()
                
                # Прокрутить вниз
                self.events_table.scrollToBottom()
    
    def on_speed_changed(self, value: int):
        """Обработка изменения скорости"""
        speed_mult = value / 10.0
        
        # Визуальное представление режима
        if speed_mult == 0.1:
            display_text = "0.1x 🐢 ОЧЕНЬ МЕДЛЕННО"
            color = "#F44336"
        elif speed_mult < 1.0:
            display_text = f"{speed_mult:.1f}x 🐢 ЗАМЕДЛЕННО"
            color = "#FF9800"
        elif speed_mult == 1.0:
            display_text = "1.0x ⏱️ РЕАЛЬНОЕ ВРЕМЯ"
            color = "#4CAF50"
        elif speed_mult <= 5.0:
            display_text = f"{speed_mult:.1f}x ⚡ УСКОРЕННО"
            color = "#2196F3"
        else:
            display_text = f"{speed_mult:.1f}x 🚀 ОЧЕНЬ БЫСТРО"
            color = "#9C27B0"
        
        self.speed_label.setText(display_text)
        self.speed_label.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 11px;")
        
        # Обновить для текущей симуляции
        if self.simulation_thread and self.simulation_thread.isRunning():
            self.simulation_thread.set_speed_multiplier(speed_mult)
            self.update_status(f"Скорость изменена: {display_text}")
    
    def stop_simulation(self):
        """Остановить симуляцию - мягко и без зависаний"""
        if self.simulation_thread and self.simulation_thread.isRunning():
            # Сначала установить флаг остановки
            self.simulation_thread.is_running = False
            # Ждём завершения потока нормально (без terminate)
            self.simulation_thread.wait(3000)  # 3 секунды на graceful shutdown
            # Если не завершился, то принудительно
            if self.simulation_thread.isRunning():
                self.simulation_thread.terminate()
                self.simulation_thread.wait(1000)
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.update_status("⏹ Симуляция остановлена")
    
    def update_status(self, message: str):
        """Обновить статус"""
        self.status_label.setText(message)
        self.log_text.append(f"[{message}]")
    
    def update_time_status(self, sim_time: float):
        """Обновить статус с информацией о времени симуляции"""
        import time
        
        # Инициализировать если нужно
        if self.sim_start_time is None:
            self.sim_start_time = time.time()
        
        # Рассчитать реальное прошедшее время
        real_elapsed = time.time() - self.sim_start_time
        self.sim_current_time = sim_time
        
        # Рассчитать скорость симуляции (сколько времени симуляции за реальную секунду)
        if real_elapsed > 0.1:  # Минимум 0.1 сек для стабильного расчёта
            sim_speed = sim_time / real_elapsed
        else:
            sim_speed = 0
        
        # Рассчитать оставшееся реальное время
        if sim_speed > 0:
            remaining_sim_time = 3600 - sim_time  # Предполагаем 1 час симуляции
            estimated_remaining = remaining_sim_time / sim_speed
        else:
            estimated_remaining = 0
        
        # Форматировать время
        message = (
            f"⏱️ Реальное: {real_elapsed:.1f}s | "
            f"Симуляция: {sim_time:.1f}s | "
            f"Скорость: {sim_speed:.1f}x | "
            f"Остаток: {estimated_remaining:.0f}s"
        )
        
        self.status_label.setText(message)
    
    def add_event_to_table(self, event_data: dict):
        """Добавить событие в таблицу"""
        try:
            row = self.events_table.rowCount()
            self.events_table.insertRow(row)
            
            self.events_table.setItem(row, 0, QTableWidgetItem(f"{event_data['time']:.1f}"))
            self.events_table.setItem(row, 1, QTableWidgetItem(event_data['type']))
            self.events_table.setItem(row, 2, QTableWidgetItem(event_data['entity']))
            self.events_table.setItem(row, 3, QTableWidgetItem(event_data['status']))
            
            # Показать последние 100 событий
            if row > 100:
                self.events_table.removeRow(0)
        except Exception as e:
            print(f"Ошибка добавления события: {e}")
    
    def on_recommendations_toggled(self, state):
        """Переключить видимость вкладки рекомендаций"""
        self.tab_widget.setTabVisible(self.recommendations_tab, state == Qt.Checked)
    
    def simulation_finished(self, stats: dict):
        """Обработать завершение"""
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.current_stats = stats
        
        self.update_status("✓ Симуляция завершена")
        
        # Обновить панель и мониторинг
        self.dashboard.update_stats(stats)
        self.monitoring_widget.update_monitoring(stats)
        self.passenger_monitoring.update_passenger_stats(stats)
        
        # Обновить рекомендации после завершения
        if hasattr(self, 'recommendations_widget'):
            self.recommendations_widget.generate_recommendations(stats)
        
        # Обновить очереди если у симулятора есть терминал
        if self.simulation_thread and self.simulation_thread.simulator:
            try:
                self.terminal_queues.update_queues(self.simulation_thread.simulator)
            except Exception as e:
                self.logger.debug(f"Ошибка обновления очередей: {e}")
        
        # Обновить графики
        try:
            events_by_type = stats.get('events_by_type', {})
            if events_by_type:
                # chart_events удалена - используются новые графики в metrics_chart
                pass
        except Exception as e:
            print(f"Ошибка обновления графика: {e}")
        
        # Обновить таблицу статистики
        self.stats_table.setRowCount(0)
        
        # Первая строка - режим управления
        mode = stats.get('mode', 'Неизвестно')
        row = 0
        self.stats_table.insertRow(row)
        self.stats_table.setItem(row, 0, QTableWidgetItem("🔧 РЕЖИМ"))
        self.stats_table.setItem(row, 1, QTableWidgetItem(mode))
        
        # Остальные метрики
        for key, value in stats.items():
            if not isinstance(value, dict) and key != 'mode':
                row = self.stats_table.rowCount()
                self.stats_table.insertRow(row)
                
                # Форматировать ключ
                display_key = key.replace('_', ' ').title()
                
                # Форматировать значение
                if isinstance(value, float):
                    display_value = f"{value:.2f}"
                else:
                    display_value = str(value)
                
                self.stats_table.setItem(row, 0, QTableWidgetItem(display_key))
                self.stats_table.setItem(row, 1, QTableWidgetItem(display_value))
    
    def export_csv(self):
        """Экспортировать CSV с полной статистикой"""
        if not self.current_stats:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта. Запустите симуляцию первой.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить CSV", 
            f"simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                success = self.export_manager.export_csv(self.current_stats, file_path)
                if success:
                    self.update_status(f"✓ CSV успешно экспортирован: {file_path}")
                    QMessageBox.information(
                        self, 
                        "Экспорт завершен", 
                        f"CSV файл успешно сохранен:\n{file_path}"
                    )
                else:
                    QMessageBox.warning(self, "Ошибка", "Ошибка при экспорте CSV")
            except Exception as e:
                self.logger.error(f"Ошибка экспорта CSV: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {e}")
    
    def export_json(self):
        """Экспортировать JSON с полной статистикой"""
        if not self.current_stats:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта. Запустите симуляцию первой.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить JSON", 
            f"simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                success = self.export_manager.export_json(self.current_stats, file_path)
                if success:
                    self.update_status(f"✓ JSON успешно экспортирован: {file_path}")
                    QMessageBox.information(
                        self, 
                        "Экспорт завершен", 
                        f"JSON файл успешно сохранен:\n{file_path}"
                    )
                else:
                    QMessageBox.warning(self, "Ошибка", "Ошибка при экспорте JSON")
            except Exception as e:
                self.logger.error(f"Ошибка экспорта JSON: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {e}")
    
    def export_xlsx(self):
        """Экспортировать XLSX с красивым форматированием"""
        if not self.current_stats:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта. Запустите симуляцию первой.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить XLSX", 
            f"simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                success = self.export_manager.export_xlsx(self.current_stats, file_path)
                if success:
                    self.update_status(f"✓ XLSX успешно экспортирован: {file_path}")
                    QMessageBox.information(
                        self, 
                        "Экспорт завершен", 
                        f"Excel файл успешно сохранен:\n{file_path}"
                    )
                else:
                    QMessageBox.warning(self, "Ошибка", "Ошибка при экспорте XLSX. Убедитесь, что установлен openpyxl (pip install openpyxl)")
            except Exception as e:
                self.logger.error(f"Ошибка экспорта XLSX: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {e}")
    
    def export_pdf(self):
        """Экспортировать PDF с красивым оформлением"""
        if not self.current_stats:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта. Запустите симуляцию первой.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить PDF", 
            f"simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                success = self.export_manager.export_pdf(self.current_stats, file_path)
                if success:
                    self.update_status(f"✓ PDF успешно экспортирован: {file_path}")
                    QMessageBox.information(
                        self, 
                        "Экспорт завершен", 
                        f"PDF файл успешно сохранен:\n{file_path}"
                    )
                else:
                    QMessageBox.warning(self, "Ошибка", "Ошибка при экспорте PDF. Убедитесь, что установлен reportlab (pip install reportlab)")
            except Exception as e:
                self.logger.error(f"Ошибка экспорта PDF: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {e}")


