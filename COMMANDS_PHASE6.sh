#!/usr/bin/bash
# AeroSim EDU Phase 6 - Команды для работы

# ============================================
# 🚀 БЫСТРЫЙ ЗАПУСК
# ============================================

# GUI с экономикой и контролем скорости
python3 run_gui_phase6.py

# или альтернативно
python3 aerosim_edu.py --gui

# ============================================
# 🧪 ТЕСТИРОВАНИЕ
# ============================================

# Запустить все тесты интеграции
python3 test_gui_integration.py

# ============================================
# 🎯 CLI РЕЖИМЫ
# ============================================

# Короткая симуляция (30 минут)
python3 aerosim_edu.py --cli --duration 1800

# Длинная симуляция (3 часа) с выводом
python3 aerosim_edu.py --cli --duration 10800 --verbose

# Экспорт в CSV
python3 aerosim_edu.py --cli --duration 3600 --export-csv results.csv

# ============================================
# 🌐 WEB ИНТЕРФЕЙС
# ============================================

# Запустить Web сервер на порту 5000
python3 aerosim_edu.py --web --port 5000

# на порту 8000
python3 aerosim_edu.py --web --port 8000

# ============================================
# 📊 ПРОФИЛИРОВАНИЕ
# ============================================

# Профилировать производительность
python3 -m cProfile -s cumulative aerosim_edu.py --cli --duration 300 | head -30

# ============================================
# 🔍 ОТЛАДКА
# ============================================

# Запустить с отладочным выводом
python3 aerosim_edu.py --cli --duration 300 --verbose 2>&1 | tee debug.log

# Запустить GUI с логированием
python3 run_gui_phase6.py 2>&1 | tee gui.log

# ============================================
# 📚 ДОКУМЕНТАЦИЯ
# ============================================

# Просмотреть полную документацию Phase 6
cat PHASE6_GUI_DOCUMENTATION.md

# Быстрый старт (5 минут)
cat QUICKSTART_PHASE6.md

# Статус всех компонентов
cat PHASE6_STATUS.md

# ============================================
# 📋 ПОЛЕЗНЫЕ СКРИПТЫ
# ============================================

# Проверить все файлы на ошибки
python3 -m py_compile src/**/*.py

# Посчитать строк кода
find src -name "*.py" -exec wc -l {} + | tail -1

# Список всех Python файлов
find . -name "*.py" -type f | grep -E "(src|test)" | sort

# ============================================
# 🔧 ОТЛАДКА GUI
# ============================================

# Проверить импорты
python3 -c "
from src.gui.economics_widget import EconomicsWidget
from src.gui.advanced_main_window import AdvancedAeroSimMainWindow
print('✅ Все импорты OK')
"

# Проверить симулятор
python3 -c "
from src.core.simulator import AirportSimulator
from config.default import DEFAULT_CONFIG
sim = AirportSimulator(DEFAULT_CONFIG)
print('✅ Симулятор инициализирован')
"

# ============================================
# 💾 РЕЗЕРВНЫЕ КОПИИ
# ============================================

# Создать резервную копию
cp -r . ../AeroSim_EDU_backup_$(date +%Y%m%d_%H%M%S)

# ============================================
# 🧹 ОЧИСТКА
# ============================================

# Удалить кэш Python
find . -type d -name __pycache__ -exec rm -rf {} +

# Удалить .pyc файлы
find . -type f -name "*.pyc" -delete

# ============================================
# 📈 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ============================================

# Пример 1: Быстрая симуляция и просмотр экономики в GUI
# 1. Запустите:
python3 run_gui_phase6.py
# 2. Нажмите "Запустить"
# 3. Выберите 600s (10 минут)
# 4. Перейдите на вкладку "💰 Экономика"
# 5. Измените скорость слайдером

# Пример 2: Запустить 180-секундную симуляцию и посмотреть результаты
python3 aerosim_edu.py --cli --duration 180 --verbose | grep -E "✈️|💰|ROI"

# Пример 3: Экспортировать результаты в CSV и открыть в Excel
python3 aerosim_edu.py --cli --duration 3600 --export-csv results.csv
libreoffice results.csv  # или открыть в Excel

# ============================================
# 🎓 ОБУЧЕНИЕ И ТЕСТИРОВАНИЕ
# ============================================

# Запустить тесты с подробным выводом
python3 -v test_gui_integration.py

# Запустить один конкретный тест
python3 -c "
import sys
sys.path.insert(0, '.')
from test_gui_integration import test_economics_data
test_economics_data()
"

# ============================================
# 📊 АНАЛИЗ РЕЗУЛЬТАТОВ
# ============================================

# Получить статистику за 180s
python3 aerosim_edu.py --cli --duration 180 | tail -20

# Получить статистику за 3600s (1 час)
python3 aerosim_edu.py --cli --duration 3600 | tail -20

# ============================================
# 🚀 ПРОИЗВОДСТВО
# ============================================

# Запустить GUI в background
nohup python3 run_gui_phase6.py > gui.log 2>&1 &

# Проверить процесс
ps aux | grep python3 | grep aerosim

# Убить процесс
pkill -f "python3 run_gui_phase6.py"

# ============================================
# 📝 ЗАМЕТКИ
# ============================================

# Phase 6 включает:
# ✅ Economics models (revenues, costs, ROI)
# ✅ GUI widget для экономики
# ✅ Speed control (0.1x - 10x)
# ✅ Integration tests (3/3 passed)
# ✅ Complete documentation

# Вкладки GUI:
# - 📊 Мониторинг
# - 👥 Пассажиры  
# - 📋 Очереди
# - 💰 Экономика (NEW)
# - 📋 События

# Скорость слайдер:
# - Min: 1 (0.1x speed)
# - Default: 10 (1.0x speed - реальное время)
# - Max: 100 (10x speed)

# ============================================
# ✨ ALL PHASE 6 COMMANDS READY!
# ============================================
