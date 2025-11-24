"""
Система логирования
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """Получить логгер с форматированием"""
    
    logger = logging.getLogger(name)
    
    # Не добавлять обработчики повторно
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Формат для консоли
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
