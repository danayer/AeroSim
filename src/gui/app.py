"""
Приложение GUI для AeroSim EDU
"""

import sys
from PyQt5.QtWidgets import QApplication

# Используем расширенную версию GUI
from src.gui.advanced_main_window import AdvancedAeroSimMainWindow


def run_gui(advanced: bool = True):
    """
    Запустить GUI приложение
    
    Args:
        advanced: Использовать ли расширенный GUI (по умолчанию True)
    """
    
    app = QApplication(sys.argv)
    
    if advanced:
        window = AdvancedAeroSimMainWindow()
    else:
        from src.gui.main_window import AeroSimMainWindow
        window = AeroSimMainWindow()
    
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
