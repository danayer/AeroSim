#!/usr/bin/env python3
"""
Детальный тест экономических расчётов с объяснением
"""

import sys
from src.models.economics import (
    FlightEconomics, AirportEconomics, FlightType,
    PassengerClassRevenue, COMMUTER_CONFIG, INTERNATIONAL_CONFIG
)

def test_economics_detailed():
    """Тест: показать как рассчитываются экономические показатели"""
    
    print("=" * 80)
    print("🧪 ДЕТАЛЬНЫЙ ТЕСТ ЭКОНОМИЧЕСКИХ РАСЧЁТОВ")
    print("=" * 80)
    
    # === Создать аэропортовскую экономику ===
    airport_econ = AirportEconomics()
    
    print("\n" + "=" * 80)
    print("📝 ЭТАП 1: Рассчёт для КОММУТЕРСКОГО РЕЙСА")
    print("=" * 80)
    
    # Коммутерский рейс
    flight1 = FlightEconomics(
        flight_id="FL001",
        flight_type=FlightType.COMMUTER,
        aircraft_config=COMMUTER_CONFIG
    )
    
    print(f"\n🔧 Конфигурация самолёта (коммутерский):")
    print(f"   Вместимость: {COMMUTER_CONFIG.capacity} мест")
    print(f"   First Class мест: {COMMUTER_CONFIG.first_class_seats}")
    print(f"   Coach мест: {COMMUTER_CONFIG.coach_seats}")
    print(f"   Базовая цена билета: ${COMMUTER_CONFIG.base_ticket_price}")
    print(f"   First Class множитель: {COMMUTER_CONFIG.first_class_multiplier}x")
    
    # Добавить пассажиров
    flight1.passenger_revenue.first_class_passengers = 8
    flight1.passenger_revenue.coach_passengers = 38
    flight1.passenger_revenue.first_class_revenue = 8 * (COMMUTER_CONFIG.base_ticket_price * COMMUTER_CONFIG.first_class_multiplier)
    flight1.passenger_revenue.coach_revenue = 38 * COMMUTER_CONFIG.base_ticket_price
    
    # Рассчитать расходы
    flight1.calculate_costs()
    flight1.update_load_factor()
    
    print(f"\n💰 ДОХОДЫ (коммутерский рейс):")
    print(f"   First Class: {flight1.passenger_revenue.first_class_passengers} × ${COMMUTER_CONFIG.base_ticket_price * COMMUTER_CONFIG.first_class_multiplier} = ${flight1.passenger_revenue.first_class_revenue:,.2f}")
    print(f"   Coach: {flight1.passenger_revenue.coach_passengers} × ${COMMUTER_CONFIG.base_ticket_price} = ${flight1.passenger_revenue.coach_revenue:,.2f}")
    print(f"   ─────────────────────────────────────────")
    print(f"   ИТОГО ДОХОД: ${flight1.total_revenue:,.2f}")
    
    print(f"\n💸 РАСХОДЫ (коммутерский рейс):")
    print(f"   Топливо: ${flight1.fuel_cost:,.2f}")
    print(f"   Экипаж: ${flight1.crew_cost:,.2f}")
    print(f"   Обслуживание: ${flight1.maintenance_cost:,.2f}")
    print(f"   Сборы аэропорта: ${flight1.airport_fees:,.2f}")
    print(f"   ─────────────────────────────────────────")
    print(f"   ИТОГО РАСХОДЫ: ${flight1.total_costs:,.2f}")
    
    print(f"\n📊 МЕТРИКИ (коммутерский рейс):")
    print(f"   Прибыль: ${flight1.profit:,.2f}")
    print(f"   ROI: {flight1.roi_percentage:.2f}%")
    print(f"   Загрузка: {flight1.load_factor:.1f}%")
    print(f"   Средняя цена билета: ${flight1.passenger_revenue.average_ticket_price:.2f}")
    
    # Добавить в аэропортовскую экономику
    airport_econ.add_flight_economics(flight1)
    
    # === Создать второй рейс (международный) ===
    print("\n" + "=" * 80)
    print("📝 ЭТАП 2: Рассчёт для МЕЖДУНАРОДНОГО РЕЙСА")
    print("=" * 80)
    
    flight2 = FlightEconomics(
        flight_id="FL002",
        flight_type=FlightType.INTERNATIONAL,
        aircraft_config=INTERNATIONAL_CONFIG
    )
    
    print(f"\n🔧 Конфигурация самолёта (международный):")
    print(f"   Вместимость: {INTERNATIONAL_CONFIG.capacity} мест")
    print(f"   First Class мест: {INTERNATIONAL_CONFIG.first_class_seats}")
    print(f"   Coach мест: {INTERNATIONAL_CONFIG.coach_seats}")
    print(f"   Базовая цена билета: ${INTERNATIONAL_CONFIG.base_ticket_price}")
    print(f"   First Class множитель: {INTERNATIONAL_CONFIG.first_class_multiplier}x")
    
    # Добавить пассажиров (с хорошей загрузкой)
    flight2.passenger_revenue.first_class_passengers = 35
    flight2.passenger_revenue.coach_passengers = 155
    flight2.passenger_revenue.first_class_revenue = 35 * (INTERNATIONAL_CONFIG.base_ticket_price * INTERNATIONAL_CONFIG.first_class_multiplier)
    flight2.passenger_revenue.coach_revenue = 155 * INTERNATIONAL_CONFIG.base_ticket_price
    
    # Рассчитать расходы
    flight2.calculate_costs()
    flight2.update_load_factor()
    
    print(f"\n💰 ДОХОДЫ (международный рейс):")
    print(f"   First Class: {flight2.passenger_revenue.first_class_passengers} × ${INTERNATIONAL_CONFIG.base_ticket_price * INTERNATIONAL_CONFIG.first_class_multiplier} = ${flight2.passenger_revenue.first_class_revenue:,.2f}")
    print(f"   Coach: {flight2.passenger_revenue.coach_passengers} × ${INTERNATIONAL_CONFIG.base_ticket_price} = ${flight2.passenger_revenue.coach_revenue:,.2f}")
    print(f"   ─────────────────────────────────────────")
    print(f"   ИТОГО ДОХОД: ${flight2.total_revenue:,.2f}")
    
    print(f"\n💸 РАСХОДЫ (международный рейс):")
    print(f"   Топливо: ${flight2.fuel_cost:,.2f}")
    print(f"   Экипаж: ${flight2.crew_cost:,.2f}")
    print(f"   Обслуживание: ${flight2.maintenance_cost:,.2f}")
    print(f"   Сборы аэропорта: ${flight2.airport_fees:,.2f}")
    print(f"   ─────────────────────────────────────────")
    print(f"   ИТОГО РАСХОДЫ: ${flight2.total_costs:,.2f}")
    
    print(f"\n📊 МЕТРИКИ (международный рейс):")
    print(f"   Прибыль: ${flight2.profit:,.2f}")
    print(f"   ROI: {flight2.roi_percentage:.2f}%")
    print(f"   Загрузка: {flight2.load_factor:.1f}%")
    print(f"   Средняя цена билета: ${flight2.passenger_revenue.average_ticket_price:.2f}")
    
    # Добавить в аэропортовскую экономику
    airport_econ.add_flight_economics(flight2)
    
    # === Итоговая статистика ===
    print("\n" + "=" * 80)
    print("📈 ЭТАП 3: ИТОГОВАЯ СТАТИСТИКА АЭРОПОРТА")
    print("=" * 80)
    
    print(f"\n✈️  РЕЙСЫ:")
    print(f"   Всего: {airport_econ.total_flights}")
    print(f"   Коммутерских: {airport_econ.commuter_flights}")
    print(f"   Международных: {airport_econ.international_flights}")
    
    print(f"\n👥 ПАССАЖИРЫ:")
    print(f"   Всего: {airport_econ.total_passengers_served}")
    print(f"   First Class: {airport_econ.first_class_passengers}")
    print(f"   Coach: {airport_econ.coach_passengers}")
    
    print(f"\n💰 ФИНАНСЫ:")
    print(f"   First Class доход: ${airport_econ.first_class_revenue:,.2f}")
    print(f"   Coach доход: ${airport_econ.coach_revenue:,.2f}")
    print(f"   ─────────────────────────────────────────")
    print(f"   ВСЕГО ДОХОД: ${airport_econ.total_passenger_revenue:,.2f}")
    print(f"   ВСЕГО РАСХОДЫ: ${airport_econ.total_costs:,.2f}")
    print(f"   ─────────────────────────────────────────")
    print(f"   ПРИБЫЛЬ: ${airport_econ.total_profit:,.2f}")
    print(f"   ROI: {airport_econ.roi_percentage:.2f}%")
    
    print(f"\n📊 СРЕДНИЕ МЕТРИКИ:")
    print(f"   Доход/рейс: ${airport_econ.average_revenue_per_flight:,.2f}")
    print(f"   Прибыль/рейс: ${airport_econ.average_profit_per_flight:,.2f}")
    print(f"   Загрузка: {airport_econ.average_load_factor:.1f}%")
    
    # === ПРОВЕРКА МАТЕМАТИКИ ===
    print("\n" + "=" * 80)
    print("✅ ПРОВЕРКА МАТЕМАТИКИ")
    print("=" * 80)
    
    checks = []
    
    # Проверка 1: Доходы = First Class + Coach
    expected_revenue = airport_econ.first_class_revenue + airport_econ.coach_revenue
    if abs(airport_econ.total_passenger_revenue - expected_revenue) < 0.01:
        print("✓ Доход корректен: First Class + Coach = Итого")
        checks.append(True)
    else:
        print(f"✗ Ошибка доходов: {airport_econ.total_passenger_revenue} != {expected_revenue}")
        checks.append(False)
    
    # Проверка 2: Расходы = сумма расходов всех рейсов
    expected_costs = flight1.total_costs + flight2.total_costs
    if abs(airport_econ.total_costs - expected_costs) < 0.01:
        print("✓ Расходы корректны: FL001 + FL002 = Итого")
        checks.append(True)
    else:
        print(f"✗ Ошибка расходов: {airport_econ.total_costs} != {expected_costs}")
        checks.append(False)
    
    # Проверка 3: Прибыль = Доход - Расходы
    expected_profit = airport_econ.total_passenger_revenue - airport_econ.total_costs
    if abs(airport_econ.total_profit - expected_profit) < 0.01:
        print("✓ Прибыль корректна: Доход - Расходы = Итого прибыль")
        checks.append(True)
    else:
        print(f"✗ Ошибка прибыли: {airport_econ.total_profit} != {expected_profit}")
        checks.append(False)
    
    # Проверка 4: ROI = (Прибыль / Расходы) × 100
    if airport_econ.total_costs > 0:
        expected_roi = (airport_econ.total_profit / airport_econ.total_costs) * 100
        if abs(airport_econ.roi_percentage - expected_roi) < 0.01:
            print(f"✓ ROI корректен: (Прибыль / Расходы) × 100 = {airport_econ.roi_percentage:.2f}%")
            checks.append(True)
        else:
            print(f"✗ Ошибка ROI: {airport_econ.roi_percentage} != {expected_roi}")
            checks.append(False)
    
    # Проверка 5: Пассажиры = sum от всех рейсов
    expected_pax = flight1.passenger_revenue.total_passengers + flight2.passenger_revenue.total_passengers
    if airport_econ.total_passengers_served == expected_pax:
        print(f"✓ Пассажиры корректны: {expected_pax} = Итого")
        checks.append(True)
    else:
        print(f"✗ Ошибка пассажиров: {airport_econ.total_passengers_served} != {expected_pax}")
        checks.append(False)
    
    print("\n" + "=" * 80)
    passed = sum(checks)
    total = len(checks)
    print(f"РЕЗУЛЬТАТ: {passed}/{total} проверок пройдено")
    
    if passed == total:
        print("✅ ВСЕ РАСЧЁТЫ ВЕРНЫ!")
        return 0
    else:
        print("❌ ЕСТЬ ОШИБКИ!")
        return 1

if __name__ == "__main__":
    sys.exit(test_economics_detailed())
