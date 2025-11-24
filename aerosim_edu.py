#!/usr/bin/env python3
"""
AeroSim EDU - Симулятор аэропорта для образовательных целей
Главный файл приложения
"""

import sys
import argparse
import json
from pathlib import Path

# Добавить src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.simulator import AirportSimulator
from src.utils.logger import get_logger
from config.default import DEFAULT_CONFIG


def parse_arguments():
    """Парсить аргументы командной строки"""
    
    parser = argparse.ArgumentParser(
        description="AeroSim EDU - Симулятор аэропорта для образовательных целей",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python3 aerosim_edu.py --cli --duration 3600
  python3 aerosim_edu.py --cli --duration 1800 --verbose
  python3 aerosim_edu.py --gui
  python3 aerosim_edu.py --web --port 5000
  python3 aerosim_edu.py --cli --export-csv /path/to/file.csv
        """
    )
    
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Запустить в режиме командной строки"
    )
    
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Запустить графический интерфейс (требует PyQt5)"
    )
    
    parser.add_argument(
        "--web",
        action="store_true",
        help="Запустить Web сервер"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Порт для Web сервера (по умолчанию: 5000)"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_CONFIG["duration"],
        help=f"Длительность симуляции в секундах (по умолчанию: {DEFAULT_CONFIG['duration']})"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Путь к JSON файлу конфигурации"
    )
    
    parser.add_argument(
        "--export-csv",
        type=str,
        help="Экспортировать результаты в CSV"
    )
    
    parser.add_argument(
        "--export-json",
        type=str,
        help="Экспортировать результаты в JSON"
    )
    
    parser.add_argument(
        "--export-pdf",
        type=str,
        help="Экспортировать результаты в PDF"
    )
    
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Создать визуализации результатов"
    )
    
    parser.add_argument(
        "--save-db",
        action="store_true",
        help="Сохранить результаты в БД"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Подробный вывод логов"
    )
    
    parser.add_argument(
        "--foreground",
        action="store_true",
        help="Запустить в foreground режиме"
    )
    
    return parser.parse_args()


def load_config(config_path: str = None) -> dict:
    """Загрузить конфигурацию из файла или использовать по умолчанию"""
    
    if config_path:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**DEFAULT_CONFIG, **config}
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            return DEFAULT_CONFIG
    
    return DEFAULT_CONFIG


def run_cli(args) -> None:
    """Запустить CLI режим"""
    
    logger = get_logger(__name__)
    logger.info("=" * 70)
    logger.info("AeroSim EDU - Симулятор аэропорта для образовательных целей")
    logger.info("=" * 70)
    
    # Загрузить конфигурацию
    config = load_config(args.config)
    config["duration"] = args.duration
    
    # Создать и запустить симулятор
    simulator = AirportSimulator(config)
    simulator.run()
    
    # Получить статистику
    stats = simulator.get_statistics()
    logger.info("\nИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    logger.info(f"  Всего обработано событий: {stats['total_events_processed']}")
    logger.info(f"  Время симуляции: {simulator.current_time:.1f} сек")
    
    # PHASE 6: Вывести экономическую статистику
    econ = stats.get('airport_economics', {})
    if econ:
        logger.info("\n💰 ЭКОНОМИЧЕСКАЯ СТАТИСТИКА (PHASE 6):")
        logger.info(f"  Рейсы: {econ.get('total_flights', 0)} всего ({econ.get('commuter_flights', 0)} коммутерских, {econ.get('international_flights', 0)} междунар.)")
        logger.info(f"  Пассажиры обслужены: {econ.get('total_passengers_served', 0)} ({econ.get('first_class_passengers', 0)} First Class, {econ.get('coach_passengers', 0)} Coach)")
        logger.info(f"  Доход: ${econ.get('total_revenue', 0):.2f}")
        logger.info(f"    ├─ First Class: ${econ.get('first_class_revenue', 0):.2f} ({econ.get('first_class_revenue_pct', 0):.1f}%)")
        logger.info(f"    └─ Coach: ${econ.get('coach_revenue', 0):.2f} ({econ.get('coach_revenue_pct', 0):.1f}%)")
        logger.info(f"  Расходы: ${econ.get('total_costs', 0):.2f}")
        logger.info(f"  Прибыль: ${econ.get('total_profit', 0):.2f} (ROI: {econ.get('roi_percentage', 0):.1f}%)")
        logger.info(f"  Средний коэффициент загрузки: {econ.get('average_load_factor', 0):.1f}%")
        logger.info(f"  Среднее наполнение на рейс: {econ.get('average_revenue_per_flight', 0):.2f}")
        logger.info(f"  Средняя прибыль на рейс: ${econ.get('average_profit_per_flight', 0):.2f}")


def run_gui(args) -> None:
    """Запустить GUI режим"""
    
    logger = get_logger(__name__)
    try:
        from src.gui.app import run_gui
        run_gui()
    except ImportError:
        logger.error("GUI требует PyQt5. Установите: pip install PyQt5")


def run_web(args) -> None:
    """Запустить Web сервер"""
    
    logger = get_logger(__name__)
    try:
        from src.web.app import run_web_server
        run_web_server(host='127.0.0.1', port=args.port, debug=args.verbose)
    except ImportError:
        logger.error("Web требует Flask. Установите: pip install flask")


def run_cli_with_features(args) -> None:
    """Запустить CLI с дополнительными функциями"""
    
    logger = get_logger(__name__)
    logger.info("=" * 70)
    logger.info("AeroSim EDU - Симулятор аэропорта для образовательных целей")
    logger.info("=" * 70)
    
    # Загрузить конфигурацию
    config = load_config(args.config)
    config["duration"] = args.duration
    
    # Создать и запустить симулятор
    simulator = AirportSimulator(config)
    simulator.run()
    
    # Получить статистику
    stats = simulator.get_statistics()
    
    # Вывести итоговую статистику
    logger.info("\nИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    logger.info(f"  Всего обработано событий: {stats['total_events_processed']}")
    logger.info(f"  Время симуляции: {simulator.current_time:.1f} сек")
    
    # PHASE 6: Вывести экономическую статистику
    econ = stats.get('airport_economics', {})
    if econ:
        logger.info("\n💰 ЭКОНОМИЧЕСКАЯ СТАТИСТИКА (PHASE 6):")
        logger.info(f"  Рейсы: {econ.get('total_flights', 0)} всего ({econ.get('commuter_flights', 0)} коммутерских, {econ.get('international_flights', 0)} междунар.)")
        logger.info(f"  Пассажиры обслужены: {econ.get('total_passengers_served', 0)} ({econ.get('first_class_passengers', 0)} First Class, {econ.get('coach_passengers', 0)} Coach)")
        logger.info(f"  Доход: ${econ.get('total_revenue', 0):.2f}")
        logger.info(f"    ├─ First Class: ${econ.get('first_class_revenue', 0):.2f} ({econ.get('first_class_revenue_pct', 0):.1f}%)")
        logger.info(f"    └─ Coach: ${econ.get('coach_revenue', 0):.2f} ({econ.get('coach_revenue_pct', 0):.1f}%)")
        logger.info(f"  Расходы: ${econ.get('total_costs', 0):.2f}")
        logger.info(f"  Прибыль: ${econ.get('total_profit', 0):.2f} (ROI: {econ.get('roi_percentage', 0):.1f}%)")
        logger.info(f"  Средний коэффициент загрузки: {econ.get('average_load_factor', 0):.1f}%")
        logger.info(f"  Среднее наполнение на рейс: {econ.get('average_revenue_per_flight', 0):.2f}")
        logger.info(f"  Средняя прибыль на рейс: ${econ.get('average_profit_per_flight', 0):.2f}")
    
    # Экспорт результатов
    if args.export_csv or args.export_json or args.export_pdf:
        from src.utils.exporter import ResultsExporter
        exporter = ResultsExporter(stats)
        
        if args.export_csv:
            if exporter.export_csv(args.export_csv):
                logger.info(f"✓ CSV экспортирован: {args.export_csv}")
            else:
                logger.error(f"✗ Ошибка при экспорте CSV")
        
        if args.export_json:
            if exporter.export_json(args.export_json):
                logger.info(f"✓ JSON экспортирован: {args.export_json}")
            else:
                logger.error(f"✗ Ошибка при экспорте JSON")
        
        if args.export_pdf:
            if exporter.export_pdf(args.export_pdf):
                logger.info(f"✓ PDF экспортирован: {args.export_pdf}")
            else:
                logger.error(f"✗ Ошибка при экспорте PDF")
    
    # Визуализация
    if args.visualize:
        try:
            from src.utils.visualizer import SimulationVisualizer
            visualizer = SimulationVisualizer(stats)
            output_dir = "results/plots"
            results = visualizer.export_all_plots(output_dir)
            logger.info(f"✓ Графики созданы в {output_dir}")
        except ImportError:
            logger.error("Визуализация требует matplotlib. Установите: pip install matplotlib")
        except Exception as e:
            logger.error(f"Ошибка при создании графиков: {e}")
    
    # Сохранение в БД
    if args.save_db:
        try:
            from src.utils.database import SimulationDatabase
            with SimulationDatabase() as db:
                sim_id = db.save_simulation(stats, config)
                logger.info(f"✓ Результаты сохранены в БД (ID: {sim_id})")
        except Exception as e:
            logger.error(f"Ошибка при сохранении в БД: {e}")


def main():
    """Главная функция"""
    
    args = parse_arguments()
    
    # Если не указан режим, использовать CLI
    if not args.cli and not args.gui and not args.web:
        args.cli = True
    
    try:
        if args.cli:
            run_cli_with_features(args)
        elif args.gui:
            run_gui(args)
        elif args.web:
            run_web(args)
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
