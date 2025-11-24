#!/bin/bash

# AeroSim EDU - Быстрый старт для Linux

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  AeroSim EDU - Симулятор аэропорта для образовательных целей  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Проверить Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Пожалуйста установите Python 3.8 или выше"
    exit 1
fi

echo "✓ Python найден: $(python3 --version)"
echo ""

# Опции
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Использование: ./quickstart.sh [ОПЦИЯ]"
    echo ""
    echo "Опции:"
    echo "  --cli           Запустить CLI режим (по умолчанию)"
    echo "  --duration N    Длительность в секундах (по умолчанию: 3600)"
    echo "  --test          Запустить тесты"
    echo "  --verbose       Подробный вывод"
    echo "  --help          Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  ./quickstart.sh                  # Запуск на 1 час"
    echo "  ./quickstart.sh --duration 600   # Запуск на 10 минут"
    echo "  ./quickstart.sh --test           # Запуск тестов"
    exit 0
fi

# Параметры
MODE="cli"
DURATION=3600
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --cli)
            MODE="cli"
            shift
            ;;
        --test)
            MODE="test"
            shift
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo "Режим: $MODE"
echo "Длительность: $DURATION сек"
echo ""

# Запуск
if [ "$MODE" = "cli" ]; then
    echo "🚀 Запуск симуляции на $DURATION секунд..."
    echo ""
    python3 aerosim_edu.py --cli --duration $DURATION $VERBOSE
elif [ "$MODE" = "test" ]; then
    echo "🧪 Запуск тестов..."
    echo ""
    python3 -m unittest tests.test_simulator -v
fi

echo ""
echo "✓ Готово!"
