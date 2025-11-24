"""
Виджеты графиков для мониторинга в реальном времени с интерактивностью
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPen, QColor, QPainter
from typing import Dict, List
from collections import deque


class InteractiveChartView(QChartView):
    """Расширенный QChartView с поддержкой tooltip при наведении мыши (оптимизированный)"""
    
    def __init__(self, chart):
        super().__init__(chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self.series_points = {}
        self.last_tooltip_time = 0
        self.tooltip_throttle = 0.1  # Обновлять tooltip не чаще 10 раз в секунду
    
    def mouseMoveEvent(self, event):
        """Обработить движение мыши с throttling для tooltip"""
        super().mouseMoveEvent(event)
        
        # Throttling: не обновлять tooltip слишком часто
        import time
        current_time = time.time()
        if current_time - self.last_tooltip_time < self.tooltip_throttle:
            return
        
        self.last_tooltip_time = current_time
        
        pos = self.mapToScene(event.pos())
        chart_pos = self.chart().mapFromScene(pos)
        
        plot_area = self.chart().plotArea()
        if not plot_area.contains(chart_pos):
            self.setToolTip("")
            return
        
        # Оптимизация: искать только в видимой области
        closest_point = None
        min_distance = float('inf')
        series_info = None
        
        for series in self.chart().series():
            if not hasattr(series, 'points'):
                continue
            
            points = series.points()
            if len(points) == 0:
                continue
            
            # Искать только 20 ближайших точек вместо всех
            for point in points[-20:]:  # Только последние 20 точек (самые свежие)
                scene_point = self.chart().mapToScene(point.x(), point.y())
                screen_point = self.mapFromScene(scene_point)
                
                dx = event.pos().x() - screen_point.x()
                dy = event.pos().y() - screen_point.y()
                distance = (dx*dx + dy*dy) ** 0.5
                
                if distance < min_distance and distance < 15:
                    min_distance = distance
                    closest_point = point
                    series_info = series.name()
        
        if closest_point:
            tooltip_text = f"Время: {closest_point.x():.1f} сек\n{series_info}: {closest_point.y():.2f}"
            self.setToolTip(tooltip_text)
        else:
            self.setToolTip("")


class RealtimeChartWidget(QWidget):
    """Граф для отслеживания метрик в реальном времени с динамической шкалой"""
    
    def __init__(self, title: str = "Мониторинг", initial_duration: float = 3600):
        super().__init__()
        self.title = title
        self.duration = initial_duration
        self.data_points = deque(maxlen=2000)
        self.series = QLineSeries()
        self.current_time = 0
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        layout = QVBoxLayout()
        
        self.chart = QChart()
        self.chart.setTitle(self.title)
        self.chart.addSeries(self.series)
        self.chart.setAnimationOptions(QChart.NoAnimation)
        
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Время (сек)")
        self.axis_x.setRange(0, self.duration)
        
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Значение")
        self.axis_y.setRange(0, 100)
        
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        
        self.chart_view = InteractiveChartView(self.chart)
        
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
    
    def add_data_point(self, time: float, value: float):
        """Добавить точку данных"""
        self.current_time = time
        self.data_points.append((time, value))
        self.update_chart()
    
    def update_chart(self):
        """Обновить граф с динамической шкалой"""
        try:
            self.series.clear()
            
            for time, value in self.data_points:
                self.series.append(time, value)
            
            if len(self.data_points) > 0:
                values = [v for _, v in self.data_points]
                max_val = max(values) if values else 100
                
                self.axis_y.setRange(0, max(100, max_val * 1.1))
                time_range = max(self.duration, self.current_time * 1.05)
                self.axis_x.setRange(0, time_range)
            
            self.chart_view.update()
        except Exception as e:
            print(f"Ошибка обновления графика: {e}")
    
    def set_duration(self, duration: float):
        """Установить длительность симуляции в секундах"""
        self.duration = duration
        self.axis_x.setRange(0, duration * 1.05)


class MultiSeriesChartWidget(QWidget):
    """Граф с несколькими временными рядами и интерактивностью (оптимизированный)"""
    
    def __init__(self, title: str = "Мониторинг", series_names: List[str] = None, initial_duration: float = 3600):
        super().__init__()
        self.title = title
        self.duration = initial_duration
        self.series_names = series_names or ["Series 1", "Series 2", "Series 3"]
        # Ограничить до 500 точек вместо 2000 - достаточно для отображения
        self.series_data = {name: deque(maxlen=500) for name in self.series_names}
        self.series_objects = {}
        self.current_time = 0
        self.update_counter = 0  # Счетчик для пропуска некоторых обновлений
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        layout = QVBoxLayout()
        
        self.chart = QChart()
        self.chart.setTitle(self.title)
        self.chart.setAnimationOptions(QChart.NoAnimation)
        
        colors = [
            QColor("#2196F3"),  # Blue
            QColor("#FF9800"),  # Orange
            QColor("#4CAF50"),  # Green
            QColor("#F44336"),  # Red
            QColor("#9C27B0"),  # Purple
        ]
        
        for i, name in enumerate(self.series_names):
            series = QLineSeries()
            series.setName(name)
            
            pen = QPen(colors[i % len(colors)])
            pen.setWidth(2)
            series.setPen(pen)
            
            self.chart.addSeries(series)
            self.series_objects[name] = series
        
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Время (сек)")
        self.axis_x.setRange(0, self.duration)
        
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Значение (%)")
        self.axis_y.setRange(0, 100)
        
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        
        for series in self.series_objects.values():
            series.attachAxis(self.axis_x)
            series.attachAxis(self.axis_y)
        
        self.chart_view = InteractiveChartView(self.chart)
        
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignTop)
        
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
    
    def add_multiple_points(self, data: Dict[str, float], time: float):
        """Добавить точки для нескольких серий одновременно с временной меткой"""
        for name, value in data.items():
            if name in self.series_data:
                self.series_data[name].append((time, value))
        
        self.current_time = max(self.current_time, time)
        
        # Обновлять граф не каждый раз, а через раз (для снижения нагрузки)
        # Но с опциональным флагом force_update для важных данных
        self.update_counter += 1
        if self.update_counter % 2 == 0:
            self.update_chart()
    
    def add_multiple_points_force(self, data: Dict[str, float], time: float):
        """Добавить точки и обновить немедленно (для важных данных типа экономики)"""
        for name, value in data.items():
            if name in self.series_data:
                self.series_data[name].append((time, value))
        
        self.current_time = max(self.current_time, time)
        self.update_chart()  # Обновить сразу без throttling
    
    def update_chart(self):
        """Обновить граф с динамической шкалой (оптимизированная версия)"""
        try:
            max_len = max([len(self.series_data[name]) for name in self.series_names], default=0)
            
            if max_len == 0:
                return
            
            # Полностью перестраивать график только если количество точек значительно изменилось
            for name in self.series_names:
                series = self.series_objects[name]
                series.clear()  # Очистить и переполнить - это быстрее обновления отдельных точек
                
                for time, value in self.series_data[name]:
                    series.append(time, value)
            
            # Обновить оси
            time_range = max(self.duration, self.current_time * 1.05)
            self.axis_x.setRange(0, time_range)
            self.axis_y.setRange(0, 100)
            
            # Не вызывать update() явно - будет обновлено автоматически
        except Exception as e:
            print(f"Ошибка обновления графика: {e}")
    
    def set_duration(self, duration: float):
        """Установить длительность симуляции в секундах"""
        self.duration = duration
        self.axis_x.setRange(0, duration * 1.05)


class SimpleLineChartWidget(QWidget):
    """Простой граф линии с одной серией"""
    
    def __init__(self, title: str, series_name: str = "Значение", initial_duration: float = 3600):
        super().__init__()
        self.title = title
        self.series_name = series_name
        self.duration = initial_duration
        self.data_points = deque(maxlen=500)
        self.init_ui()
        self.current_time = 0
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        layout = QVBoxLayout()
        
        self.chart = QChart()
        self.chart.setTitle(self.title)
        self.chart.setAnimationOptions(QChart.NoAnimation)
        
        self.series = QLineSeries()
        self.series.setName(self.series_name)
        pen = QPen(QColor("#2196F3"))
        pen.setWidth(2)
        self.series.setPen(pen)
        self.chart.addSeries(self.series)
        
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Время (сек)")
        self.axis_x.setRange(0, self.duration)
        
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Значение ($)")
        self.axis_y.setRange(0, 100)
        
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        
        self.chart_view = InteractiveChartView(self.chart)
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
    
    def add_point(self, time: float, value: float):
        """Добавить точку данных"""
        self.current_time = time
        self.data_points.append((time, value))
        self.update_display()
    
    def update_display(self):
        """Обновить отображение"""
        try:
            self.series.clear()
            for time, value in self.data_points:
                self.series.append(time, value)
            
            if len(self.data_points) > 0:
                values = [v for _, v in self.data_points]
                max_val = max(values) if values else 100
                self.axis_y.setRange(0, max(100, max_val * 1.1))
            
            time_range = max(self.duration, self.current_time * 1.05)
            self.axis_x.setRange(0, time_range)
        except Exception as e:
            pass


class SystemMetricsChartWidget(QWidget):
    """Специализированный граф для метрик системы с интерактивностью"""
    
    def __init__(self, initial_duration: float = 3600):
        super().__init__()
        self.duration = initial_duration
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # Вкладка 1: Использование ресурсов (в процентах)
        self.utilization_chart = MultiSeriesChartWidget(
            title="📊 Использование Ресурсов (%)",
            series_names=["ВПП", "Гейты", "Персонал", "Багаж"],
            initial_duration=self.duration
        )
        tabs.addTab(self.utilization_chart, "📊 Ресурсы")
        
        # Вкладка 2: Очереди пассажиров
        self.queue_chart = MultiSeriesChartWidget(
            title="👥 Очереди Пассажиров",
            series_names=["Багаж", "Безопасность", "На посадке"],
            initial_duration=self.duration
        )
        tabs.addTab(self.queue_chart, "👥 Очереди")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def update_metrics(self, stats: dict, time: float):
        """Обновить метрики из статистики с временной меткой"""
        try:
            utilization_data = {
                "ВПП": stats.get('runway_utilization', 0),
                "Гейты": stats.get('gate_utilization', 0),
                "Персонал": stats.get('staff_utilization', 0),
                "Багаж": stats.get('baggage_utilization', 0),
            }
            # Обновить ресурсы через обычный канал
            self.utilization_chart.add_multiple_points(utilization_data, time)
            
            # Для очередей: использовать текущий размер + максимум для видимости
            luggage_q = stats.get('luggage_queue_size', 0)
            security_q = stats.get('security_queue_size', 0)
            
            queue_data = {
                "Багаж": luggage_q,
                "Безопасность": security_q,
                "На посадке": 0,
            }
            # Очереди обновлять всегда - нужна высокая частота
            self.queue_chart.add_multiple_points_force(queue_data, time)
        except Exception as e:
            pass  # Молча игнорировать ошибки графиков
    
    def set_duration(self, duration: float):
        """Установить длительность симуляции"""
        self.duration = duration
        self.utilization_chart.set_duration(duration)
        self.queue_chart.set_duration(duration)


class EconomicsChartWidget(QWidget):
    """Граф для визуализации экономических данных - ПЕРЕДЕЛАН"""
    
    def __init__(self, initial_duration: float = 3600):
        super().__init__()
        self.duration = initial_duration
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # Вкладка 1: Общие доходы
        self.total_revenue_chart = SimpleLineChartWidget(
            title="💰 Общие Доходы",
            series_name="Доход ($)",
            initial_duration=self.duration
        )
        tabs.addTab(self.total_revenue_chart, "💰 Доход")
        
        # Вкладка 2: Прибыль
        self.profit_chart = SimpleLineChartWidget(
            title="📈 Чистая Прибыль",
            series_name="Прибыль ($)",
            initial_duration=self.duration
        )
        tabs.addTab(self.profit_chart, "📈 Прибыль")
        
        # Вкладка 3: Затраты
        self.costs_chart = SimpleLineChartWidget(
            title="💸 Операционные Затраты",
            series_name="Затраты ($)",
            initial_duration=self.duration
        )
        tabs.addTab(self.costs_chart, "💸 Затраты")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def update_economics(self, stats: dict, time: float):
        """Обновить экономические данные с временной меткой"""
        try:
            economics = stats.get('airport_economics', {})
            
            # Получить основные значения (уже в долларах)
            total_revenue = economics.get('total_revenue', 0)
            total_costs = economics.get('total_costs', 0)
            total_profit = economics.get('total_profit', 0)
            
            # Убедиться что значения растут (не уменьшаются)
            total_revenue = max(0, total_revenue)
            total_costs = max(0, total_costs)
            total_profit = max(0, total_profit)
            
            # Обновить графики
            self.total_revenue_chart.add_point(time, total_revenue)
            self.profit_chart.add_point(time, max(0, total_profit))
            self.costs_chart.add_point(time, total_costs)
        except Exception as e:
            pass
    
    def set_duration(self, duration: float):
        """Установить длительность симуляции"""
        self.duration = duration
        self.total_revenue_chart.duration = duration
        self.profit_chart.duration = duration
        self.costs_chart.duration = duration
