#storage.py


import json
import os
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable


def get_safe_path(path: str) -> Path:
    """
    Приводит путь к корректному виду для текущей ОС.
    Для Windows исправляет \r, \n, \t → \
    Для других ОС оставляет как есть.
    """
    #исправляем путь типа 'data\rates.json' - важно для windows

    fixed = path.strip()

    # Проверяем ОС
    if os.name == "nt":  # Windows
        fixed = (
            fixed
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )
    else:
        # На Unix-подобных системах, обычно, ничего менять не нужно
        fixed = fixed.replace("\t", "_")  # пример минимальной коррекции, если нужно

    return Path(fixed)


class BaseRatesStorage(ABC):
    @abstractmethod
    def save(self, data: dict) -> None:
        """Сохраняет итоговый объект курсов"""
        raise NotImplementedError


#Класс хранения - снимок текущего мира - кеш курсов
class JsonRatesStorage(BaseRatesStorage):
    def __init__(self, rates_path: str):

        # Берем текущую рабочую директорию +
        c_path = os.getcwd()
        # имя файла -> Целевой файл с курсами
        self._file_path = os.path.join( c_path, get_safe_path(rates_path))

    def save(self, data: Dict) -> None:
        """
        Сохраняет данные в JSON-файл.
        Файл перезаписывается полностью.
        """

        # Если каталог не существует - его надо создать
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)

        #разделяем полное имя на имя и расширение
        file_name, file_ext = os.path.splitext( self._file_path)

        #временный файл
        tmp_path = os.path.join( os.path.dirname(self._file_path), f'{file_name}.tmp')

        with open( tmp_path, "w", encoding="utf-8") as f:
            json.dump( data, f, indent=4, ensure_ascii=False)

        # замена файла
        os.replace( tmp_path, self._file_path)

    def load(self) -> Dict:
        """
        Загружает данные из JSON-файла.
        Если файл отсутствует — возвращает пустой словарь.
        """
        if not os.path.exists(self._file_path):
            return {}

        with open(self._file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    #Конец JsonRatesStorage

#Класс для формирования формата хранение курсов
@dataclass(frozen=True)
class ExchangeRateRecord:
    from_currency: str
    to_currency: str
    rate: float
    source: str
    timestamp: datetime
    meta: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        ts = self.timestamp.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z") # noqa: E501
        return f"{self.from_currency}_{self.to_currency}_{ts}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "from_currency": self.from_currency,
            "to_currency": self.to_currency,
            "rate": self.rate,
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "source": self.source,
            "meta": self.meta,
        }


#Хранилище истории (ExchangeHistoryStorage)
class ExchangeHistoryStorage(BaseRatesStorage):
    def __init__(self, hist_path: str):

        # Берем текущую рабочую директорию.
        c_path = os.getcwd()
        # имя файла -> Целевой файл с курсами
        self._file_path = os.path.join( c_path, get_safe_path(hist_path))

    def load(self) -> dict:
        # Если файла нет то возвращаем пустой словарь
        if not os.path.exists(self._file_path):
            return {}

        # Если файл "Чудесный", то удаляем и возвращаем пустой словарь
        if os.path.getsize(self._file_path) == 0 :
            os.remove(self._file_path)
            return {}

        with open(self._file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, records: Iterable[dict]) -> None:
        data = self.load()

        for record in records:
            data.setdefault(record["id"], record)

        self._atomic_write(data)

    def _atomic_write(self, data: dict) -> None:

        #Проверяем наличие каталога, если не то создаем
        directory = os.path.dirname(self._file_path)
        os.makedirs(directory, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            delete=False,
        ) as tmp:
            json.dump(data, tmp, indent=2, ensure_ascii=False)
            tmp_path = tmp.name

        os.replace(tmp_path, self._file_path)



