#!/usr/bin/env python3
"""
Быстрый запуск GUI с мгновенным выполнением
Phase 6: Экономика + Контроль скорости + Мгновенное выполнение
"""

import sys
from pathlib import Path

# Добавить src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Запустить GUI"""
    try:
        from PyQt5.QtWidgets import QApplication
        from src.gui.advanced_main_window import AdvancedAeroSimMainWindow
        
        print("🚀 Запуск AeroSim EDU GUI (Phase 6 - Fast Mode)")
        print("   ⚡ Доступно: Мгновенное выполнение (10x скорость)")
        print("   ▶️ Доступно: Наблюдение в реальном времени с регулировкой")
        print("   💰 Экономика: Отслеживание доходов в реальном времени")
        print()
        
        app = QApplication(sys.argv)
        window = AdvancedAeroSimMainWindow()
        window.show()
        
        # Автоматически запустить мгновенное выполнение если передан аргумент
        if len(sys.argv) > 1 and sys.argv[1] == 'instant':
            print("⚡ Запуск мгновенного выполнения...")
            window.instant_execution()
        elif len(sys.argv) > 1 and sys.argv[1] == 'realtime':
            print("▶ Запуск наблюдения в реальном времени...")
            window.realtime_simulation()
        
        sys.exit(app.exec_())
    
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("\nУбедитесь, что установлены зависимости:")
        print("  pip3 install PyQt5 PyQtChart PyQtWebEngine")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
