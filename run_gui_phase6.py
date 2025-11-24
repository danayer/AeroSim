#!/usr/bin/env python3
"""
Быстрый старт GUI для AeroSim EDU Phase 6
Включает: экономика + контроль скорости + мониторинг в реальном времени
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
        
        print("🚀 Запуск AeroSim EDU GUI (Phase 6)")
        print("   - Экономика самолетов в реальном времени")
        print("   - Контроль скорости симуляции (0.1x - 10x)")
        print("   - Мониторинг пассажиров и терминалов")
        print()
        
        app = QApplication(sys.argv)
        window = AdvancedAeroSimMainWindow()
        window.show()
        
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
