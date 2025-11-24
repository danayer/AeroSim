#!/usr/bin/env python3
"""
Тестирование интеграции GUI компонентов Phase 6
Проверка: экономика + контроль скорости
"""

import sys
sys.path.insert(0, '.')

from src.core.simulator import AirportSimulator
from config.default import DEFAULT_CONFIG

def test_economics_data():
    """Тест: экономические данные передаются в статистику"""
    print("\n🧪 Тест 1: Экономические данные в статистике")
    print("=" * 50)
    
    config = DEFAULT_CONFIG.copy()
    config['duration'] = 30  # Коротко для теста
    
    simulator = AirportSimulator(config)
    if hasattr(simulator, 'initialize'):
        simulator.initialize()
    
    # Обработать первые события
    for _ in range(20):
        if simulator.event_queue.size() > 0:
            event = simulator.event_queue.pop()
            simulator.process_event(event)
    
    # Получить статистику
    stats = simulator.get_statistics()
    
    # Проверить наличие экономики
    if 'airport_economics' in stats:
        eco = stats['airport_economics']
        print(f"✅ airport_economics найден в stats")
        print(f"   - total_revenue: ${eco.get('total_revenue', 0):,.2f}")
        print(f"   - total_costs: ${eco.get('total_costs', 0):,.2f}")
        print(f"   - roi_percentage: {eco.get('roi_percentage', 0):.1f}%")
        print(f"   - total_flights: {eco.get('total_flights', 0)}")
        return True
    else:
        print("❌ airport_economics НЕ найден в stats!")
        print(f"   Доступные ключи: {list(stats.keys())}")
        return False

def test_economics_widget_parsing():
    """Тест: EconomicsWidget корректно парсит данные"""
    print("\n🧪 Тест 2: Парсинг данных в EconomicsWidget")
    print("=" * 50)
    
    try:
        from PyQt5.QtWidgets import QApplication
        from src.gui.economics_widget import EconomicsWidget
        
        # Создать QApplication для тестирования
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        widget = EconomicsWidget()
        
        # Создать тестовые данные
        test_data = {
            'airport_economics': {
                'total_revenue': 50000,
                'total_costs': 20000,
                'total_profit': 30000,
                'roi_percentage': 150,
                'first_class_revenue': 15000,
                'coach_revenue': 35000,
                'first_class_revenue_pct': 30,
                'coach_revenue_pct': 70,
                'total_flights': 5,
                'commuter_flights': 3,
                'international_flights': 2,
                'total_passengers_served': 450,
                'first_class_passengers': 60,
                'coach_passengers': 390,
                'average_load_factor': 85.5,
                'average_revenue_per_flight': 10000,
                'average_profit_per_flight': 6000,
            }
        }
        
        # Обновить виджет
        widget.update_economics(test_data)
        
        # Проверить что-нибудь видимое
        if widget.revenue_label.text():
            print(f"✅ EconomicsWidget успешно обновлён")
            print(f"   - {widget.revenue_label.text()}")
            print(f"   - {widget.profit_label.text()}")
            print(f"   - {widget.roi_label.text()}")
            return True
        else:
            print("❌ EconomicsWidget не обновился!")
            return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании EconomicsWidget: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_speed_multiplier():
    """Тест: множитель скорости в SimulationThread"""
    print("\n🧪 Тест 3: Множитель скорости")
    print("=" * 50)
    
    try:
        from src.gui.advanced_main_window import SimulationThread
        
        config = DEFAULT_CONFIG.copy()
        thread = SimulationThread(config)
        
        # Проверить начальное значение
        if thread.speed_multiplier == 1.0:
            print(f"✅ Начальное значение speed_multiplier: {thread.speed_multiplier}")
        else:
            print(f"❌ Неправильное начальное значение: {thread.speed_multiplier}")
            return False
        
        # Проверить установку значения
        thread.set_speed_multiplier(2.5)
        if thread.speed_multiplier == 2.5:
            print(f"✅ set_speed_multiplier(2.5) работает: {thread.speed_multiplier}")
        else:
            print(f"❌ set_speed_multiplier не работает: {thread.speed_multiplier}")
            return False
        
        # Проверить граничные значения
        thread.set_speed_multiplier(15.0)  # Должно быть ограничено до 10.0
        if thread.speed_multiplier == 10.0:
            print(f"✅ Верхний лимит работает: {thread.speed_multiplier}")
        else:
            print(f"❌ Верхний лимит не работает: {thread.speed_multiplier}")
            return False
        
        thread.set_speed_multiplier(0.05)  # Должно быть ограничено до 0.1
        if thread.speed_multiplier == 0.1:
            print(f"✅ Нижний лимит работает: {thread.speed_multiplier}")
        else:
            print(f"❌ Нижний лимит не работает: {thread.speed_multiplier}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Ошибка при тестировании speed_multiplier: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 ТЕСТИРОВАНИЕ ФАЗЫ 6 - GUI ИНТЕГРАЦИЯ")
    print("="*50)
    
    results = []
    
    # Запустить тесты
    results.append(("Экономические данные", test_economics_data()))
    results.append(("Парсинг EconomicsWidget", test_economics_widget_parsing()))
    results.append(("Множитель скорости", test_speed_multiplier()))
    
    # Итоги
    print("\n" + "="*50)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*50)
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    total_passed = sum(1 for _, r in results if r)
    total_tests = len(results)
    print(f"\nВсего: {total_passed}/{total_tests} тестов прошло успешно")
    
    sys.exit(0 if total_passed == total_tests else 1)
