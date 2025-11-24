"""
Виджеты для отображения экономической статистики
Интегрировано из PHASE 6
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QTableWidget, QTableWidgetItem, QProgressBar,
                             QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtCore import Qt as QtCore_Qt


class EconomicsWidget(QWidget):
    """Виджет для отображения экономической статистики"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать UI"""
        layout = QVBoxLayout()
        
        # === ФИНАНСОВАЯ СВОДКА ===
        summary_group = QGroupBox("💰 Финансовая сводка")
        summary_layout = QHBoxLayout()
        
        # Доход
        revenue_layout = QVBoxLayout()
        self.revenue_label = QLabel("Доход: $0.00")
        self.revenue_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.revenue_label.setStyleSheet("color: green;")
        revenue_layout.addWidget(QLabel("Общий доход:"))
        revenue_layout.addWidget(self.revenue_label)
        
        # Расходы
        costs_layout = QVBoxLayout()
        self.costs_label = QLabel("Расходы: $0.00")
        self.costs_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.costs_label.setStyleSheet("color: red;")
        costs_layout.addWidget(QLabel("Общие расходы:"))
        costs_layout.addWidget(self.costs_label)
        
        # Прибыль
        profit_layout = QVBoxLayout()
        self.profit_label = QLabel("Прибыль: $0.00")
        self.profit_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.profit_label.setStyleSheet("color: darkgreen;")
        profit_layout.addWidget(QLabel("Чистая прибыль:"))
        profit_layout.addWidget(self.profit_label)
        
        # ROI
        roi_layout = QVBoxLayout()
        self.roi_label = QLabel("ROI: 0%")
        self.roi_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.roi_label.setStyleSheet("color: blue;")
        roi_layout.addWidget(QLabel("Возврат инвестиций:"))
        roi_layout.addWidget(self.roi_label)
        
        summary_layout.addLayout(revenue_layout)
        summary_layout.addLayout(costs_layout)
        summary_layout.addLayout(profit_layout)
        summary_layout.addLayout(roi_layout)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # === ДОХОД ПО КЛАССАМ ===
        revenue_by_class_group = QGroupBox("📊 Доход по классам пассажиров")
        revenue_class_layout = QVBoxLayout()
        
        # First Class
        first_class_layout = QHBoxLayout()
        self.first_class_revenue_label = QLabel("First Class: $0.00 (0%)")
        self.first_class_bar = QProgressBar()
        self.first_class_bar.setMaximum(100)
        self.first_class_bar.setStyleSheet("""
            QProgressBar {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: gold;
            }
        """)
        first_class_layout.addWidget(self.first_class_revenue_label)
        first_class_layout.addWidget(self.first_class_bar)
        revenue_class_layout.addLayout(first_class_layout)
        
        # Coach
        coach_layout = QHBoxLayout()
        self.coach_revenue_label = QLabel("Coach: $0.00 (0%)")
        self.coach_bar = QProgressBar()
        self.coach_bar.setMaximum(100)
        self.coach_bar.setStyleSheet("""
            QProgressBar {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: skyblue;
            }
        """)
        coach_layout.addWidget(self.coach_revenue_label)
        coach_layout.addWidget(self.coach_bar)
        revenue_class_layout.addLayout(coach_layout)
        
        revenue_by_class_group.setLayout(revenue_class_layout)
        layout.addWidget(revenue_by_class_group)
        
        # === СТАТИСТИКА РЕЙСОВ ===
        flights_group = QGroupBox("✈️ Статистика рейсов")
        flights_layout = QHBoxLayout()
        
        self.total_flights_label = QLabel("Всего рейсов: 0")
        self.commuter_flights_label = QLabel("Коммутерских: 0")
        self.intl_flights_label = QLabel("Международных: 0")
        
        flights_layout.addWidget(self.total_flights_label)
        flights_layout.addWidget(self.commuter_flights_label)
        flights_layout.addWidget(self.intl_flights_label)
        
        flights_group.setLayout(flights_layout)
        layout.addWidget(flights_group)
        
        # === СТАТИСТИКА ПАССАЖИРОВ ===
        passengers_group = QGroupBox("👥 Статистика пассажиров")
        passengers_layout = QHBoxLayout()
        
        self.total_passengers_label = QLabel("Всего пассажиров: 0")
        self.first_class_pax_label = QLabel("First Class: 0")
        self.coach_pax_label = QLabel("Coach: 0")
        self.load_factor_label = QLabel("Загрузка: 0%")
        
        passengers_layout.addWidget(self.total_passengers_label)
        passengers_layout.addWidget(self.first_class_pax_label)
        passengers_layout.addWidget(self.coach_pax_label)
        passengers_layout.addWidget(self.load_factor_label)
        
        passengers_group.setLayout(passengers_layout)
        layout.addWidget(passengers_group)
        
        # === МЕТРИКИ РЕЙСОВ ===
        metrics_group = QGroupBox("📈 Метрики рейсов")
        metrics_layout = QHBoxLayout()
        
        self.avg_revenue_label = QLabel("Средний доход/рейс: $0.00")
        self.avg_profit_label = QLabel("Средняя прибыль/рейс: $0.00")
        self.avg_load_factor_label = QLabel("Средняя загрузка: 0%")
        
        metrics_layout.addWidget(self.avg_revenue_label)
        metrics_layout.addWidget(self.avg_profit_label)
        metrics_layout.addWidget(self.avg_load_factor_label)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        self.setLayout(layout)
    
    def update_economics(self, econ_stats: dict):
        """Обновить экономическую статистику"""
        if not econ_stats:
            return
        
        # Получить экономические данные (могут быть вложены в airport_economics)
        eco_data = econ_stats.get('airport_economics', econ_stats)
        
        # Финансовая сводка
        revenue = eco_data.get('total_revenue', 0)
        costs = eco_data.get('total_costs', 0)
        profit = eco_data.get('total_profit', 0)
        roi = eco_data.get('roi_percentage', 0)
        
        self.revenue_label.setText(f"Доход: ${revenue:,.2f}")
        self.costs_label.setText(f"Расходы: ${costs:,.2f}")
        self.profit_label.setText(f"Прибыль: ${profit:,.2f}")
        self.roi_label.setText(f"ROI: {roi:.1f}%")
        
        # Цветовое кодирование ROI
        if roi > 500:
            self.roi_label.setStyleSheet("color: darkgreen; font-weight: bold;")
        elif roi > 200:
            self.roi_label.setStyleSheet("color: green; font-weight: bold;")
        elif roi > 0:
            self.roi_label.setStyleSheet("color: blue; font-weight: bold;")
        else:
            self.roi_label.setStyleSheet("color: red; font-weight: bold;")
        
        # Доход по классам
        first_class_rev = eco_data.get('first_class_revenue', 0)
        coach_rev = eco_data.get('coach_revenue', 0)
        first_class_pct = eco_data.get('first_class_revenue_pct', 0)
        coach_pct = eco_data.get('coach_revenue_pct', 0)
        
        self.first_class_revenue_label.setText(f"First Class: ${first_class_rev:,.2f} ({first_class_pct:.1f}%)")
        self.coach_revenue_label.setText(f"Coach: ${coach_rev:,.2f} ({coach_pct:.1f}%)")
        self.first_class_bar.setValue(int(first_class_pct))
        self.coach_bar.setValue(int(coach_pct))
        
        # Статистика рейсов
        total_flights = eco_data.get('total_flights', 0)
        commuter_flights = eco_data.get('commuter_flights', 0)
        intl_flights = eco_data.get('international_flights', 0)
        
        self.total_flights_label.setText(f"Всего рейсов: {total_flights}")
        self.commuter_flights_label.setText(f"Коммутерских: {commuter_flights}")
        self.intl_flights_label.setText(f"Международных: {intl_flights}")
        
        # Статистика пассажиров
        total_pax = eco_data.get('total_passengers_served', 0)
        first_class_pax = eco_data.get('first_class_passengers', 0)
        coach_pax = eco_data.get('coach_passengers', 0)
        load_factor = eco_data.get('average_load_factor', 0)
        
        self.total_passengers_label.setText(f"Всего пассажиров: {total_pax}")
        self.first_class_pax_label.setText(f"First Class: {first_class_pax}")
        self.coach_pax_label.setText(f"Coach: {coach_pax}")
        self.load_factor_label.setText(f"Загрузка: {load_factor:.1f}%")
        
        # Метрики рейсов
        avg_revenue = eco_data.get('average_revenue_per_flight', 0)
        avg_profit = eco_data.get('average_profit_per_flight', 0)
        avg_load = eco_data.get('average_load_factor', 0)
        
        self.avg_revenue_label.setText(f"Средний доход/рейс: ${avg_revenue:,.2f}")
        self.avg_profit_label.setText(f"Средняя прибыль/рейс: ${avg_profit:,.2f}")
        self.avg_load_factor_label.setText(f"Средняя загрузка: {avg_load:.1f}%")
