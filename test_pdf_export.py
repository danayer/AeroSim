#!/usr/bin/env python3
"""
Тест экспорта PDF
"""

import json
from src.utils.export_manager import ExportManager
from datetime import datetime

def test_pdf_export():
    """Протестировать экспорт PDF"""
    
    # Создать тестовые данные
    test_stats = {
        'total_events_processed': 1247,
        'total_aircraft': 42,
        'total_passengers': 3856,
        'simulation_time': 3600,
        'throughput': 42.0,
        'avg_service_time': 18.5,
        'runway_utilization': 85.5,
        'gate_utilization': 92.3,
        'average_utilization': 88.9,
        'mode': 'Multi-Terminal',
        
        'luggage_queue_size': 145,
        'security_queue_size': 89,
        'luggage_utilization': 78.5,
        'security_utilization': 82.1,
        'staff_utilization': 91.2,
        'baggage_utilization': 85.5,
        'terminal_utilization': 88.9,
        'avg_wait_time': 425.5,
        'avg_delay_time': 85.3,
        'total_delays': 12,
        
        'airport_economics': {
            'total_flights': 42,
            'commuter_flights': 18,
            'international_flights': 24,
            'total_revenue': 245680.50,
            'first_class_revenue': 85450.00,
            'coach_revenue': 160230.50,
            'total_costs': 52300.00,
            'total_profit': 193380.50,
            'roi_percentage': 369.8,
            'total_passengers_served': 3856,
            'first_class_passengers': 812,
            'coach_passengers': 3044,
            'average_load_factor': 87.3,
            'average_revenue_per_flight': 5849.54,
            'average_profit_per_flight': 4604.30,
        },
        
        'terminal_stats': {
            'terminal_1_flights': 21,
            'terminal_2_flights': 21,
            'terminal_1_utilization': 87.5,
            'terminal_2_utilization': 89.2,
        },
        
        'active_flights': {}
    }
    
    # Создать менеджер экспорта
    manager = ExportManager()
    
    # Путь для сохранения
    pdf_path = '/tmp/test_simulation_report.pdf'
    
    # Экспортировать в PDF
    print("🔄 Тестирование экспорта PDF...")
    success = manager.export_pdf(test_stats, pdf_path)
    
    if success:
        print(f"✅ PDF успешно создан: {pdf_path}")
        
        # Проверить размер файла
        import os
        file_size = os.path.getsize(pdf_path)
        print(f"📊 Размер файла: {file_size} байт ({file_size/1024:.1f} КБ)")
        
        return True
    else:
        print(f"❌ Ошибка при создании PDF")
        return False


def test_all_formats():
    """Протестировать все форматы экспорта"""
    
    test_stats = {
        'total_events_processed': 1247,
        'total_aircraft': 42,
        'total_passengers': 3856,
        'simulation_time': 3600,
        'throughput': 42.0,
        'avg_service_time': 18.5,
        'runway_utilization': 85.5,
        'gate_utilization': 92.3,
        'average_utilization': 88.9,
        'airport_economics': {
            'total_flights': 42,
            'total_revenue': 245680.50,
            'total_profit': 193380.50,
        }
    }
    
    manager = ExportManager()
    results = {}
    
    # CSV
    print("\n🧪 Тестирование системы экспорта AeroSim EDU\n")
    
    csv_path = '/tmp/test_report.csv'
    csv_success = manager.export_csv(test_stats, csv_path)
    if csv_success:
        import os
        size = os.path.getsize(csv_path)
        print(f"✅ CSV экспорта...        Успешно! {size} байт")
        results['csv'] = True
    else:
        print(f"❌ CSV экспорта...        Ошибка")
        results['csv'] = False
    
    # JSON
    json_path = '/tmp/test_report.json'
    json_success = manager.export_json(test_stats, json_path)
    if json_success:
        import os
        size = os.path.getsize(json_path)
        print(f"✅ JSON экспорта...       Успешно! {size} байт")
        results['json'] = True
    else:
        print(f"❌ JSON экспорта...       Ошибка")
        results['json'] = False
    
    # XLSX
    try:
        xlsx_path = '/tmp/test_report.xlsx'
        xlsx_success = manager.export_xlsx(test_stats, xlsx_path)
        if xlsx_success:
            import os
            size = os.path.getsize(xlsx_path)
            print(f"✅ XLSX экспорта...       Успешно! {size} байт")
            results['xlsx'] = True
        else:
            print(f"❌ XLSX экспорта...       Ошибка")
            results['xlsx'] = False
    except:
        print(f"❌ XLSX экспорта...       Ошибка (openpyxl не установлен)")
        results['xlsx'] = False
    
    # PDF
    pdf_path = '/tmp/test_report.pdf'
    pdf_success = manager.export_pdf(test_stats, pdf_path)
    if pdf_success:
        import os
        size = os.path.getsize(pdf_path)
        print(f"✅ PDF экспорта...        Успешно! {size} байт")
        results['pdf'] = True
    else:
        print(f"❌ PDF экспорта...        Ошибка")
        results['pdf'] = False
    
    # Итоги
    total = len(results)
    successful = sum(1 for v in results.values() if v)
    print(f"\n✨ Результат: {successful}/{total} форматов успешно экспортированы")
    
    if successful == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return True
    else:
        print("⚠️ Некоторые тесты не прошли")
        return False


if __name__ == '__main__':
    test_all_formats()
