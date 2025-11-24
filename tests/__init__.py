"""
Основная документация проекта
"""

import unittest

if __name__ == "__main__":
    # Запустить все тесты
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Вернуть код выхода в зависимости от результатов
    exit(0 if result.wasSuccessful() else 1)
