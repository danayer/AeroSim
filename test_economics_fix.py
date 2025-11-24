#!/usr/bin/env python3
"""
Тест для проверки исправления экономических расчётов
"""

import sys
import time
from src.core.simulator import AirportSimulator

def test_economics():
    """Тест: проверить, что экономические данные рассчитываются корректно"""
    
    print("=" * 70)
    print("🧪 ТЕСТ ЭКОНОМИЧЕСКИХ РАСЧЁТОВ")
    print("=" * 70)
    
    # Инициализировать симулятор
    config = {
        'duration': 300,  # 5 минут
        'enable_incidents': False,  # Без форс-мажоров для чистого теста
    }
    
    simulator = AirportSimulator(config)
    simulator.initialize()
    
    # Запустить симуляцию
    start_time = time.time()
    
    print("\n⏳ Запуск симуляции...")
    
    # Проверить статус перед запуском
    print("\nДо запуска:")
    stats_before = simulator.get_statistics()
    econ_before = stats_before.get('airport_economics', {})
    print(f"   Рейсов: {econ_before.get('total_flights', 0)}")
    print(f"   Пассажиров: {econ_before.get('total_passengers_served', 0)}")
    
    # Запустить симуляцию
    simulator.run()
    
    elapsed = time.time() - start_time
    print(f"\n✅ Симуляция завершена за {elapsed:.2f}с")
    print(f"   Время симуляции: {simulator.current_time:.1f}с")
    
    # Получить финальную статистику
    final_stats = simulator.get_statistics()
    econ = final_stats.get('airport_economics', {})
    
    print("\n" + "=" * 70)
    print("📈 ФИНАЛЬНАЯ ЭКОНОМИЧЕСКАЯ СТАТИСТИКА")
    print("=" * 70)
    
    total_flights = econ.get('total_flights', 0)
    commuter_flights = econ.get('commuter_flights', 0)
    intl_flights = econ.get('international_flights', 0)
    total_revenue = econ.get('total_revenue', 0)
    first_class_rev = econ.get('first_class_revenue', 0)
    coach_rev = econ.get('coach_revenue', 0)
    total_costs = econ.get('total_costs', 0)
    total_profit = econ.get('total_profit', 0)
    roi = econ.get('roi_percentage', 0)
    total_pax = econ.get('total_passengers_served', 0)
    first_class_pax = econ.get('first_class_passengers', 0)
    coach_pax = econ.get('coach_passengers', 0)
    avg_load_factor = econ.get('average_load_factor', 0)
    avg_revenue_per_flight = econ.get('average_revenue_per_flight', 0)
    avg_profit_per_flight = econ.get('average_profit_per_flight', 0)
    
    print(f"\n✈️  РЕЙСЫ:")
    print(f"   Всего: {total_flights}")
    print(f"   Коммутерских: {commuter_flights}")
    print(f"   Международных: {intl_flights}")
    
    print(f"\n👥 ПАССАЖИРЫ:")
    print(f"   Всего: {total_pax}")
    print(f"   First Class: {first_class_pax}")
    print(f"   Coach: {coach_pax}")
    print(f"   Средняя загрузка: {avg_load_factor:.1f}%")
    
    print(f"\n💰 ФИНАНСЫ:")
    print(f"   Доход First Class: ${first_class_rev:,.2f}")
    print(f"   Доход Coach: ${coach_rev:,.2f}")
    print(f"   ВСЕГО ДОХОД: ${total_revenue:,.2f}")
    print(f"   ВСЕГО РАСХОДЫ: ${total_costs:,.2f}")
    print(f"   ─────────────────────")
    print(f"   ПРИБЫЛЬ: ${total_profit:,.2f}")
    print(f"   ROI: {roi:.2f}%")
    
    print(f"\n📊 МЕТРИКИ:")
    print(f"   Средний доход/рейс: ${avg_revenue_per_flight:,.2f}")
    print(f"   Средняя прибыль/рейс: ${avg_profit_per_flight:,.2f}")
    
    # Проверка: убедиться что данные не нулевые
    print("\n" + "=" * 70)
    print("✅ ПРОВЕРКА РЕЗУЛЬТАТОВ")
    print("=" * 70)
    
    checks = []
    
    # Проверка 1: Должны быть рейсы
    if total_flights > 0:
        print("✓ Рейсы рассчитаны корректно")
        checks.append(True)
    else:
        print("✗ ОШИБКА: Количество рейсов = 0")
        checks.append(False)
    
    # Проверка 2: Должны быть пассажиры
    if total_pax > 0:
        print("✓ Пассажиры рассчитаны корректно")
        checks.append(True)
    else:
        print("✗ ОШИБКА: Количество пассажиров = 0")
        checks.append(False)
    
    # Проверка 3: Доход должен быть > 0
    if total_revenue > 0:
        print(f"✓ Доход рассчитан корректно: ${total_revenue:,.2f}")
        checks.append(True)
    else:
        print("✗ ОШИБКА: Доход = $0")
        checks.append(False)
    
    # Проверка 4: Расходы должны быть > 0
    if total_costs > 0:
        print(f"✓ Расходы рассчитаны корректно: ${total_costs:,.2f}")
        checks.append(True)
    else:
        print("✗ ОШИБКА: Расходы = $0")
        checks.append(False)
    
    # Проверка 5: Прибыль должна быть рассчитана (может быть отрицательной)
    if total_revenue > 0 and total_costs > 0:
        expected_profit = total_revenue - total_costs
        if abs(total_profit - expected_profit) < 0.01:  # Допускаем небольшую ошибку округления
            print(f"✓ Прибыль рассчитана корректно: ${total_profit:,.2f}")
            checks.append(True)
        else:
            print(f"✗ ОШИБКА: Прибыль не совпадает (ожидается {expected_profit:.2f}, получено {total_profit:.2f})")
            checks.append(False)
    
    # Проверка 6: ROI должен быть рассчитан
    if total_costs > 0:
        expected_roi = (total_profit / total_costs) * 100
        if abs(roi - expected_roi) < 0.01:
            print(f"✓ ROI рассчитан корректно: {roi:.2f}%")
            checks.append(True)
        else:
            print(f"✗ ОШИБКА: ROI не совпадает (ожидается {expected_roi:.2f}%, получено {roi:.2f}%)")
            checks.append(False)
    
    # Итоговый результат
    print("\n" + "=" * 70)
    passed = sum(checks)
    total = len(checks)
    print(f"РЕЗУЛЬТАТ: {passed}/{total} проверок пройдено")
    
    if passed == total:
        print("✅ ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
        return 0
    else:
        print("❌ ЕСТЬ ОШИБКИ!")
        return 1

if __name__ == "__main__":
    sys.exit(test_economics())
