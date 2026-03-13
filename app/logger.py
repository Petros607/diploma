"""
Модуль настройки логирования через loguru.

Использует параметры из app.config.settings:
- logging_filename: путь к файлу лога
- logging_rotation: условие ротации (например, "10 MB")
- logging_retention: срок хранения старых логов (например, "7 days")
"""

import sys
from pathlib import Path

from loguru import logger as _logger

from app.config import settings


def setup_logger(service_name: str = "") -> None:
    """Настраивает loguru для сервиса.

    Args:
        service_name: имя сервиса (добавляется к имени файла лога)
    """
    # Удаляем стандартный handler
    _logger.remove()

    # Добавляем консольный вывод
    _logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        ),
        level="INFO",
    )

    # Формируем путь к файлу лога
    log_filename = settings.logging_filename
    if service_name:
        log_path = Path(log_filename)
        log_filename = str(
            log_path.parent / f"{log_path.stem}_{service_name}{log_path.suffix}"
        )

    # Создаём директорию если не существует
    Path(log_filename).parent.mkdir(parents=True, exist_ok=True)

    # Добавляем файловый handler с ротацией
    _logger.add(
        log_filename,
        rotation=settings.logging_rotation,
        retention=settings.logging_retention,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
    )

    _logger.info(f"Logger initialized for service: {service_name or 'default'}")


# expose same name for convenience
logger = _logger
