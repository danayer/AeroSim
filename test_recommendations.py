#!/usr/bin/env python3
"""
Тест для проверки рекомендаций после исправления
"""

import sys
from src.gui.recommendations_widget import RecommendationsWidget

def test_recommendations():
    """Тест: проверить что рекомендации генерируются корректно"""
    
    print("=" * 80)
    print("🧪 ТЕСТ РЕКОМЕНДАЦИЙ")
    print("=" * 80)
    
    # Создать виджет рекомендаций
    widget = RecommendationsWidget()
    
    print("\n📝 Сценарий 1: ПЛОХАЯ ЭКОНОМИКА (ROI < 100)")
    print("-" * 80)
    
    # Тестовые данные с плохой экономикой
    stats_bad = {
        'total_delays': 50,
        'runway_utilization': 45,
        'gate_utilization': 40,
        'checkin_queue_length': 10,
        'security_queue_length': 5,
        'boarding_queue_length': 20,
        'average_utilization': 40,
        'airport_economics': {
            'total_profit': 0,
            'roi_percentage': 0,
            'total_flights': 5,
            'total_passengers_served': 200
        }
    }
    
    widget.generate_recommendations(stats_bad)
    text = widget.recommendations_text.toPlainText()
    
    # Проверка
    if "ЭКОНОМИЧЕСКАЯ ПРОБЛЕМА" in text and "roi_percentage: 0" not in text:
        print("✅ Рекомендация по плохой экономике сгенерирована корректно")
        print("\nТекст рекомендации:")
        for line in text.split('\n'):
            if 'ЭКОНОМИЧЕСКАЯ ПРОБЛЕМА' in line or 'ROI:' in line or 'Прибыль:' in line or 'Рекомендация:' in line:
                print(f"  {line}")
    else:
        print("❌ Ошибка: рекомендация не содержит правильных данных")
        return 1
    
    print("\n" + "=" * 80)
    print("📝 Сценарий 2: ХОРОШАЯ ЭКОНОМИКА (ROI > 400)")
    print("-" * 80)
    
    # Тестовые данные с хорошей экономикой
    stats_good = {
        'total_delays': 50,
        'runway_utilization': 45,
        'gate_utilization': 40,
        'checkin_queue_length': 10,
        'security_queue_length': 5,
        'boarding_queue_length': 20,
        'average_utilization': 40,
        'airport_economics': {
            'total_profit': 375700,
            'roi_percentage': 593.99,
            'total_flights': 10,
            'total_passengers_served': 1214
        }
    }
    
    widget.generate_recommendations(stats_good)
    text = widget.recommendations_text.toPlainText()
    
    # Проверка
    if "ОТЛИЧНАЯ РЕНТАБЕЛЬНОСТЬ" in text and "ROI: 593.99" in text:
        print("✅ Рекомендация по хорошей экономике сгенерирована корректно")
        print("\nТекст рекомендации:")
        for line in text.split('\n'):
            if 'ОТЛИЧНАЯ РЕНТАБЕЛЬНОСТЬ' in line or 'ROI:' in line or 'Прибыль:' in line or 'Статус:' in line:
                print(f"  {line}")
    else:
        print("❌ Ошибка: рекомендация не содержит правильных данных")
        return 1
    
    print("\n" + "=" * 80)
    print("📝 Сценарий 3: НОРМАЛЬНАЯ ЭКОНОМИКА (100 < ROI < 400)")
    print("-" * 80)
    
    # Тестовые данные с нормальной экономикой
    stats_normal = {
        'total_delays': 50,
        'runway_utilization': 45,
        'gate_utilization': 40,
        'checkin_queue_length': 10,
        'security_queue_length': 5,
        'boarding_queue_length': 20,
        'average_utilization': 40,
        'airport_economics': {
            'total_profit': 50000,
            'roi_percentage': 250.0,
            'total_flights': 5,
            'total_passengers_served': 500
        }
    }
    
    widget.generate_recommendations(stats_normal)
    text = widget.recommendations_text.toPlainText()
    
    # Проверка
    if "ЗДОРОВАЯ РЕНТАБЕЛЬНОСТЬ" in text and "ROI: 250" in text:
        print("✅ Рекомендация по нормальной экономике сгенерирована корректно")
        print("\nТекст рекомендации:")
        for line in text.split('\n'):
            if 'ЗДОРОВАЯ РЕНТАБЕЛЬНОСТЬ' in line or 'ROI:' in line or 'Прибыль:' in line or 'Статус:' in line:
                print(f"  {line}")
    else:
        print("❌ Ошибка: рекомендация не содержит правильных данных")
        return 1
    
    print("\n" + "=" * 80)
    print("✅ ВСЕ ТЕСТЫ РЕКОМЕНДАЦИЙ ПРОЙДЕНЫ!")
    print("=" * 80)
    
    print("\n💡 РЕЗУЛЬТАТЫ:")
    print("  ✓ Рекомендации теперь корректно извлекают данные из airport_economics")
    print("  ✓ Поддерживаются 3 сценария: плохая, хорошая, нормальная экономика")
    print("  ✓ ROI больше не показывает 0% в рекомендациях")
    print("  ✓ Пользователь увидит правильные рекомендации")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_recommendations())
