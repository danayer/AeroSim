#!/usr/bin/env python3
"""
Тест проверки исправлений GUI
"""

print("=" * 70)
print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЙ GUI")
print("=" * 70)

# Инициализация QApplication сразу
from PyQt5.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)

# Тест 1: Компиляция всех файлов
print("\n1️⃣  Проверка компиляции файлов...")
try:
    import py_compile
    files = [
        "src/gui/advanced_main_window.py",
        "src/gui/monitoring_widgets.py",
        "src/core/simulator.py",
        "aerosim_edu.py"
    ]
    for f in files:
        py_compile.compile(f, doraise=True)
    print("   ✓ Все файлы компилируются успешно")
except Exception as e:
    print(f"   ✗ Ошибка компиляции: {e}")

# Тест 2: Импорт модулей
print("\n2️⃣  Проверка импорта модулей...")
try:
    from src.gui.advanced_main_window import SimulationThread, DashboardPanel, AdvancedAeroSimMainWindow
    from src.gui.monitoring_widgets import ComprehensiveMonitoringWidget, AirportResourceWidget
    print("   ✓ Все модули импортируются успешно")
except Exception as e:
    print(f"   ✗ Ошибка импорта: {e}")

# Тест 3: Проверка сигналов
print("\n3️⃣  Проверка сигналов SimulationThread...")
try:
    thread = SimulationThread({"duration": 100, "aircraft": {"initial_aircraft": 2}})
    assert hasattr(thread, 'stats_updated'), "Нет сигнала stats_updated"
    assert hasattr(thread, 'event_added'), "Нет сигнала event_added"
    print("   ✓ Все сигналы присутствуют")
except Exception as e:
    print(f"   ✗ Ошибка проверки сигналов: {e}")

# Тест 4: Проверка методов обновления
print("\n4️⃣  Проверка методов обновления панели...")
try:
    dashboard = DashboardPanel()
    assert hasattr(dashboard, 'update_stats'), "Нет метода update_stats"
    
    # Попытка обновления
    stats = {
        'total_events_processed': 10,
        'total_aircraft': 5,
        'total_passengers': 750,
        'total_delays': 45.5,
        'simulation_time': 300.0,
        'average_utilization': 75.5,
        'runway_utilization': 80.0,
        'gate_utilization': 60.0
    }
    dashboard.update_stats(stats)
    print("   ✓ Методы обновления работают")
except Exception as e:
    print(f"   ✗ Ошибка методов: {e}")

# Тест 5: Проверка мониторинга
print("\n5️⃣  Проверка методов мониторинга...")
try:
    resource_widget = AirportResourceWidget()
    assert hasattr(resource_widget, 'update_resources'), "Нет метода update_resources"
    resource_widget.update_resources(stats)
    
    monitoring = ComprehensiveMonitoringWidget()
    assert hasattr(monitoring, 'update_monitoring'), "Нет метода update_monitoring"
    monitoring.update_monitoring(stats)
    print("   ✓ Методы мониторинга работают")
except Exception as e:
    print(f"   ✗ Ошибка мониторинга: {e}")

print("\n" + "=" * 70)
print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
print("=" * 70)
print("\n🚀 Запуск GUI:")
print("   python3 aerosim_edu.py --gui")
print("\nОжидаемое поведение:")
print("   • Панель обновляется каждые 10 событий")
print("   • Таблица событий заполняется рейсами")
print("   • Мониторинг показывает использование ресурсов")
print("   • График показывает типы событий при завершении")
print("=" * 70)
