#settins.py

#config.json <- ключи храним здесь

#список ключей
#paths.data_dir — путь к data/
#paths.rates_json — путь к файлу с кешем курсов
#paths.exchange_json - путь к файлу с историей курсов
#paths.portfolios_json - путь к файлу с портфолио
#paths.users_json - путь к файлу с информацией о пользователях
#paths.logs_dir — путь к папке логов
#rates.ttl_seconds — TTL курсов

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

#Данные конфигурации по умолчанию
DEFAULT_CFG = {
  "paths": {
    "data_dir": "data",
    "rates_json": "rates.json",
    "exchange_json": "exchange_rates.json",
    "portfolios_json": "portfolios.json",
    "users_json": "users.json",
    "logs_dir": "logs"
  },
  "rates": {
    "ttl_seconds": 1200
  }
}


class SettingsLoader:
    """
    Singleton для конфигурации приложения.

    Реализация через __new__:
    - гарантирует единый экземпляр даже если SettingsLoader() вызывают многократно.
    Загружает config.json, и кеширует данные в памяти.
    """

    _instance: "SettingsLoader | None" = None
    _initialized: bool = False

    def __new__(cls, config_path: str | Path = "config.json") -> "SettingsLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str | Path = "config.json") -> None:
        #Важно: __init__ при Singleton будет вызываться каждый раз при SettingsLoader()
        # поэтому делаем "инициализацию один раз".
        if self.__class__._initialized:
            return

        self._config_path = Path(config_path)
        self._data: dict[str, Any] = {}
        self.reload()  # первичная загрузка

        self.__class__._initialized = True

    @property
    def config_path(self) -> Path:
        return self._config_path

    def reload(self) -> None:
        """Перезагрузить конфиг из JSON и обновить кеш."""
        if not self._config_path.exists():
            print(f"Файл конфигурации не найден: {self._config_path}")
            print(f"Используюу параметры по умолчанию: {DEFAULT_CFG}")
            self._data = DEFAULT_CFG
            return

        with self._config_path.open("r", encoding="utf-8") as f:
            loaded = json.load(f)

        if not isinstance(loaded, dict):
            print(f"Файл конфигурации должен быть в формате JSON: {self._config_path}")
            print(f"Используюу параметры по умолчанию: {DEFAULT_CFG}")
            self._data = DEFAULT_CFG
            return

        self._data = loaded

    def get(self, key1: str, key2: str) -> Any:
        """
        Получить значение по ключу.
        Если ключ не найден — возвращает default.
        """
        level1 = self._data.get(key1, None)
        if level1 is None:
            raise KeyError("Отсутствует список путоей к фалам данных !!!")

        level2 = level1.get(key2, None)
        if level2 is None:
            raise KeyError("Имя файла данных !!!")
        return level2

    def require(self, key: str) -> Any:
        """
        Получить значение по ключу, но если отсутствует — бросить KeyError.
        Удобно для обязательных настроек.
        """
        value = self.get(key, default=None)
        if value is None:
            raise KeyError(f"Отсутствует обязательный параметр конфигурации: {key}")
        return value


