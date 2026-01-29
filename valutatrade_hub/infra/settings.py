# Singleton SettingsLoader (конфигурация)

#Что именно хранит SettingsLoader

#Минимальный набор конфигурации (по ТЗ):

#DATA_DIR            — путь к данным (json, портфели, курсы)
#RATES_TTL_SECONDS   — TTL курсов валют
#BASE_CURRENCY       — базовая валюта (например "USD")
#LOGS_DIR            — путь к логам
#LOG_FORMAT          — формат логирования


import json
#import os  # Будет использоваться
import tomllib  # Python 3.11+
from typing import Any


class SettingsLoader:
    """
    Singleton для загрузки и кеширования конфигурации проекта.
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str | None = None) -> None:
        # защита от повторной инициализации
        if self.__class__._initialized:
            return

        self._config_path = config_path
        self._settings: dict[str, Any] = {}

        self._load()
        self.__class__._initialized = True


    def _load(self) -> None:
        """
        Загружает конфигурацию из pyproject.toml или config.json
        """

        # 1️⃣ pyproject.toml
        if self._config_path and self._config_path.endswith(".toml"):
            with open(self._config_path, "rb") as f:
                data = tomllib.load(f)

            self._settings = data.get("tool", {}).get("valutatrade", {})

        # 2️⃣ config.json
        elif self._config_path and self._config_path.endswith(".json"):
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._settings = json.load(f)

        # 3️⃣ fallback defaults
        else:
            self._settings = {
                "DATA_DIR": "./data",
                "RATES_TTL_SECONDS": 300,
                "BASE_CURRENCY": "USD",
                "LOGS_DIR": "./logs",
                "LOG_FORMAT": "%(asctime)s - %(levelname)s - %(message)s",
            }

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def reload(self) -> None:
        self._load()


#[tool.valutatrade]
#DATA_DIR = "./data"
#RATES_TTL_SECONDS = 120
#BASE_CURRENCY = "USD"
#LOGS_DIR = "./logs"
#LOG_FORMAT = "%(levelname)s | %(message)s"

#Проверка Singleton-поведения
#s1 = SettingsLoader("pyproject.toml")
#s2 = SettingsLoader()


#Использование в usecases
#usecases/get_rate.py

settings = SettingsLoader()

def get_rate_usecase(from_code: str, to_code: str) -> float:
    ttl = settings.get("RATES_TTL_SECONDS", 300)

    # здесь логика кеша / API
    print(f"TTL курсов: {ttl} сек")


