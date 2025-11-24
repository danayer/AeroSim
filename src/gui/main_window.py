"""
Главное окно GUI приложения AeroSim EDU
"""

import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QSpinBox, QComboBox, QTextEdit,
    QProgressBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor

from src.core.simulator import AirportSimulator
from src.utils.logger import get_logger
from src.utils.export_manager import ExportManager


class SimulationThread(QThread):
    """Поток для выполнения симуляции в фоне"""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    status = pyqtSignal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.simulator = None
    
    def run(self):
        """Выполнить симуляцию"""
        try:
            self.status.emit("Инициализация симулятора...")
            self.simulator = AirportSimulator(self.config)
            
            self.status.emit("Запуск симуляции...")
            self.simulator.run()
            
            self.finished.emit(self.simulator.get_statistics())
        except Exception as e:
            self.status.emit(f"Ошибка: {str(e)}")


class AeroSimMainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.simulator = None
        self.simulation_thread = None
        self.current_stats = {}
        self.export_manager = ExportManager()
        
        self.init_ui()
        self.setWindowTitle("AeroSim EDU - Симулятор аэропорта")
        self.setGeometry(100, 100, 1200, 800)
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout()
        
        # Левая панель - управление
        left_panel = self.create_control_panel()
        
        # Правая панель - вкладки
        right_panel = self.create_tabs_panel()
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        
        main_widget.setLayout(main_layout)
    
    def create_control_panel(self):
        """Создать панель управления"""
        
        group = QGroupBox("Управление симуляцией")
        layout = QVBoxLayout()
        
        # Параметры
        params_layout = QGridLayout()
        
        # Длительность
        params_layout.addWidget(QLabel("Длительность (сек):"), 0, 0)
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(60)
        self.duration_spinbox.setMaximum(86400)
        self.duration_spinbox.setValue(3600)
        params_layout.addWidget(self.duration_spinbox, 0, 1)
        
        # ВПП
        params_layout.addWidget(QLabel("Количество ВПП:"), 1, 0)
        self.runways_spinbox = QSpinBox()
        self.runways_spinbox.setMinimum(1)
        self.runways_spinbox.setMaximum(10)
        self.runways_spinbox.setValue(2)
        params_layout.addWidget(self.runways_spinbox, 1, 1)
        
        # Терминалы
        params_layout.addWidget(QLabel("Количество терминалов:"), 2, 0)
        self.terminals_spinbox = QSpinBox()
        self.terminals_spinbox.setMinimum(1)
        self.terminals_spinbox.setMaximum(10)
        self.terminals_spinbox.setValue(3)
        params_layout.addWidget(self.terminals_spinbox, 2, 1)
        
        # Гейты
        params_layout.addWidget(QLabel("Гейтов в терминале:"), 3, 0)
        self.gates_spinbox = QSpinBox()
        self.gates_spinbox.setMinimum(5)
        self.gates_spinbox.setMaximum(50)
        self.gates_spinbox.setValue(20)
        params_layout.addWidget(self.gates_spinbox, 3, 1)
        
        # Начальные самолеты
        params_layout.addWidget(QLabel("Начальные самолеты:"), 4, 0)
        self.aircraft_spinbox = QSpinBox()
        self.aircraft_spinbox.setMinimum(1)
        self.aircraft_spinbox.setMaximum(50)
        self.aircraft_spinbox.setValue(5)
        params_layout.addWidget(self.aircraft_spinbox, 4, 1)
        
        layout.addLayout(params_layout)
        layout.addSpacing(20)
        
        # Кнопки
        self.start_button = QPushButton("▶ Запустить симуляцию")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.start_button.clicked.connect(self.start_simulation)
        layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("⏸ Пауза")
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.pause_simulation)
        layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("⏹ Остановить")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        self.stop_button.clicked.connect(self.stop_simulation)
        layout.addWidget(self.stop_button)
        
        layout.addSpacing(20)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Статус
        self.status_label = QLabel("Готов к запуску")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        layout.addSpacing(20)
        
        # Экспорт
        export_layout = QVBoxLayout()
        export_layout.addWidget(QLabel("Экспорт результатов:"))
        
        self.export_csv_button = QPushButton("💾 CSV")
        self.export_csv_button.clicked.connect(self.export_csv)
        export_layout.addWidget(self.export_csv_button)
        
        self.export_json_button = QPushButton("💾 JSON")
        self.export_json_button.clicked.connect(self.export_json)
        export_layout.addWidget(self.export_json_button)
        
        self.export_pdf_button = QPushButton("📄 PDF")
        self.export_pdf_button.clicked.connect(self.export_pdf)
        export_layout.addWidget(self.export_pdf_button)
        
        layout.addLayout(export_layout)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_tabs_panel(self):
        """Создать панель с вкладками"""
        
        tabs = QTabWidget()
        
        # Вкладка логов
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        tabs.addTab(self.log_text, "📋 Логи")
        
        # Вкладка статистики
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        tabs.addTab(self.stats_table, "📊 Статистика")
        
        # Вкладка событий
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(4)
        self.events_table.setHorizontalHeaderLabels(["Время", "Тип события", "Сущность", "Данные"])
        self.events_table.horizontalHeader().setStretchLastSection(True)
        tabs.addTab(self.events_table, "🔔 События")
        
        # Вкладка конфигурации
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        self.config_text.setFont(QFont("Courier", 9))
        tabs.addTab(self.config_text, "⚙️ Конфигурация")
        
        return tabs
    
    def start_simulation(self):
        """Запустить симуляцию"""
        
        config = {
            "duration": self.duration_spinbox.value(),
            "airport": {
                "num_runways": self.runways_spinbox.value(),
                "num_terminals": self.terminals_spinbox.value(),
                "gates_per_terminal": self.gates_spinbox.value(),
            },
            "aircraft": {
                "initial_aircraft": self.aircraft_spinbox.value(),
            }
        }
        
        # Показать конфигурацию
        import json
        self.config_text.setText(json.dumps(config, indent=2, ensure_ascii=False))
        
        # Создать и запустить поток
        self.simulation_thread = SimulationThread(config)
        self.simulation_thread.status.connect(self.update_status)
        self.simulation_thread.finished.connect(self.simulation_finished)
        
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        self.log_text.clear()
        self.log_text.append("🚀 Симуляция запущена...\n")
        
        self.simulation_thread.start()
    
    def pause_simulation(self):
        """Пауза симуляции"""
        self.update_status("⏸ Симуляция приостановлена")
    
    def stop_simulation(self):
        """Остановить симуляцию"""
        if self.simulation_thread:
            self.simulation_thread.quit()
            self.simulation_thread.wait()
        
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.update_status("⏹ Симуляция остановлена")
    
    def update_status(self, message):
        """Обновить статус"""
        self.status_label.setText(message)
        self.log_text.append(f"[Статус] {message}")
    
    def simulation_finished(self, stats):
        """Обработать завершение симуляции"""
        
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        self.update_status("✓ Симуляция завершена")
        
        # Показать статистику
        self.stats_table.setRowCount(0)
        for key, value in stats.items():
            row = self.stats_table.rowCount()
            self.stats_table.insertRow(row)
            self.stats_table.setItem(row, 0, QTableWidgetItem(str(key)))
            self.stats_table.setItem(row, 1, QTableWidgetItem(str(value)))
    
    def export_csv(self):
        """Экспортировать в CSV с полной статистикой"""
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
        """Экспортировать в JSON с полной статистикой"""
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
    
    def export_pdf(self):
        """Экспортировать в PDF"""
        QMessageBox.information(
            self,
            "PDF экспорт",
            "Функция PDF экспорта будет реализована в следующей версии.\n\n"
            "Для экспорта результатов используйте Excel или JSON формат."
        )

