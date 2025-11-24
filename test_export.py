#!/usr/bin/env python3
"""
Тест функциональности экспорта данных
"""

from src.utils.export_manager import ExportManager
import json
from pathlib import Path


def create_test_data():
    """Создать тестовые данные для экспорта"""
    return {
        'total_events_processed': 15423,
        'total_aircraft': 87,
        'total_passengers': 4521,
        'simulation_time': 3600.5,
        'throughput': 87.0,
        'avg_service_time': 41.43,
        'runway_utilization': 68.5,
        'gate_utilization': 72.3,
        'average_utilization': 70.4,
        'mode': 'Идеальное управление',
        'total_delays': 12,
        'luggage_queue_size': 45,
        'security_queue_size': 23,
        'luggage_utilization': 65.5,
        'security_utilization': 48.2,
        'staff_utilization': 52.0,
        'baggage_utilization': 34.0,
        'terminal_utilization': 68.0,
        'avg_wait_time': 6.8,
        'avg_delay_time': 0.45,
        'terminal_id': 'T1',
        'terminal_stats': {
            'passengers_processed': 4521,
            'flights_handled': 87,
            'avg_passengers_per_flight': 52,
            'queue_efficiency': 0.85,
        },
        'airport_economics': {
            'total_flights': 87,
            'commuter_flights': 45,
            'international_flights': 42,
            'total_revenue': 678150.0,
            'first_class_revenue': 169537.5,
            'coach_revenue': 508612.5,
            'total_costs': 150000.0,
            'total_profit': 528150.0,
            'roi_percentage': 352.1,
            'total_passengers_served': 4521,
            'first_class_passengers': 1125,
            'coach_passengers': 3396,
            'average_load_factor': 0.85,
            'average_revenue_per_flight': 7795.4,
            'average_profit_per_flight': 6073.56,
            'first_class_revenue_pct': 25.0,
            'coach_revenue_pct': 75.0,
        }
    }


def test_export():
    """Протестировать все форматы экспорта"""
    
    print("🧪 Тестирование системы экспорта AeroSim EDU\n")
    print("=" * 60)
    
    # Создать менеджер экспорта
    export_manager = ExportManager()
    test_data = create_test_data()
    
    # Создать директорию для тестов
    test_dir = Path('./export_tests')
    test_dir.mkdir(exist_ok=True)
    
    tests = [
        ('CSV', 'export_tests/test_report.csv', export_manager.export_csv),
        ('JSON', 'export_tests/test_report.json', export_manager.export_json),
        ('XLSX', 'export_tests/test_report.xlsx', export_manager.export_xlsx),
    ]
    
    results = []
    
    for format_name, file_path, export_func in tests:
        print(f"\n📝 Тестирование {format_name} экспорта...")
        print(f"   Путь: {file_path}")
        
        try:
            success = export_func(test_data, file_path)
            
            if success:
                file_size = Path(file_path).stat().st_size
                print(f"   ✅ Успешно!")
                print(f"   📦 Размер файла: {file_size} байт")
                results.append((format_name, True, file_size))
            else:
                print(f"   ❌ Ошибка при экспорте")
                results.append((format_name, False, 0))
        except Exception as e:
            print(f"   ⚠️  Исключение: {e}")
            results.append((format_name, False, 0))
    
    # Вывести итоги
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    success_count = 0
    for format_name, success, file_size in results:
        status = "✅ OK" if success else "❌ FAIL"
        size_info = f" ({file_size} байт)" if file_size > 0 else ""
        print(f"{format_name:10} {status}{size_info}")
        if success:
            success_count += 1
    
    print("=" * 60)
    print(f"\n✨ Результат: {success_count}/{len(tests)} форматов успешно экспортированы")
    
    if success_count == len(tests):
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return True
    else:
        print(f"\n⚠️  {len(tests) - success_count} тестов не прошли")
        if success_count < len(tests):
            print("\n💡 Подсказки:")
            if not results[2][1]:  # XLSX failed
                print("   • Для экспорта XLSX требуется: pip install openpyxl")
        return False


if __name__ == '__main__':
    import sys
    success = test_export()
    sys.exit(0 if success else 1)
