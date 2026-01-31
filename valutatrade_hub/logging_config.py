# valutatrade_hub/infra/logging_config.py

# logging_config.py
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    logs_dir: str | Path = "logs",
    level: int = logging.INFO,
    max_bytes: int = 2_000_000,  # ~2MB
    backup_count: int = 5,
) -> None:
    """
    Настраивает логирование доменных действий в файл с ротацией.
    Пишем в logs/actions.log.
    """

    logs_path = Path(logs_dir)
    logs_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("actions")
    logger.setLevel(level)
    logger.propagate = False  # чтобы не дублировать в root

    # Чтобы setup_logging можно было вызывать несколько раз без дублирования хэндлеров
    if logger.handlers:
        return

    log_file = logs_path / "actions.log"

    handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)

    # Человекочитаемый формат (уровень + timestamp + сообщение)
    formatter = logging.Formatter(
        fmt="%(levelname)s %(asctime)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
