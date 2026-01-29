# valutatrade_hub/infra/logging_config.py

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "actions.log"


def setup_logging(
    level: int = logging.INFO,
    to_console: bool = True,
    to_file: bool = True,
) -> None:
    """
    Единая настройка логирования для всего приложения
    """

    handlers: list[logging.Handler] = []

    formatter = logging.Formatter(
        "%(levelname)s %(asctime)s %(message)s", #%(name)s пока без имени модуля
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    if to_file:
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=5_000_000,  # ~5 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        handlers=handlers,
    )

