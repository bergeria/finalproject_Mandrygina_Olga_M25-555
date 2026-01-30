# currencies.py
# Иерархия валют (наследование и полиморфизм)

from abc import ABC, abstractmethod

from valutatrade_hub.core.exceptions import CurrencyNotFoundError

class Currency(ABC):
    def __init__(self, name: str, code: str) -> None:
        self.name = name
        self.code = code

    # ---------- properties ----------

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Название валюты не можеть быть пустой строкой")
        self._name = value.strip()

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Код валюты должен быть строкой")

        value = value.strip().upper()

        if not (2 <= len(value) <= 5) or " " in value:
            raise ValueError("Код валюты должен быть от 2-х до 5-ти символов")

        self._code = value

    # ---------- interface ----------

    @abstractmethod
    def get_display_info(self) -> str:
        """Метод должен перекрываться наследниками"""
        """Строковое представление для UI/логов"""
        raise NotImplementedError

    #Конец Currency


# Наследник FiatCurrency
# Добавляем - issuing_country
# переопределяем get_display_info() - добавляет страну/зону эмиссии

class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str) -> None:
        super().__init__(name, code)
        self.issuing_country = issuing_country

    @property
    def issuing_country(self) -> str:
        return self._issuing_country

    @issuing_country.setter
    def issuing_country(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Cтрана-эмитент не может быть пустой строкой")
        self._issuing_country = value.strip()

    def get_display_info(self) -> str:
        return (
            f"[FIAT] {self.code} — {self.name} "
            f"(Эмитент: {self.issuing_country})"
        )

    #Конец FiatCurrency


#Наследник CryptoCurrency
#Добавляем:
#algorithm - например, “SHA-256”, “Ethash”
#market_cap - market_cap: float (последняя известная капитализация)
#Переопределение: get_display_info() (алгоритм + краткая капитализация)
#форматированную капитализацию

class CryptoCurrency(Currency):
    def __init__(
            self,
            name: str,
            code: str,
            algorithm: str,
            market_cap: float,
    ) -> None:
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Алгоритм должен быть не пустой строкой")
        self._algorithm = value.strip()

    @property
    def market_cap(self) -> float:
        return self._market_cap

    @market_cap.setter
    def market_cap(self, value: float) -> None:
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Капитализаци должна быть положительным числом")
        self._market_cap = float(value)

    def get_display_info(self) -> str:
        return (
            f"[CRYPTO] {self.code} — {self.name} "
            f"(Алгоритм: {self.algorithm}, MCAP: {self.market_cap:.2e})"
        )

    #Пример [CRYPTO] BTC — Bitcoin (Algo: SHA-256, MCAP: 1.12e12)
    #Конец CryptoCurrency


# Реестр / фабрика валют
_CURRENCY_REGISTRY: dict[str, Currency] = {
    "USD": FiatCurrency(
        name="US Dollar",
        code="USD",
        issuing_country="United States",
    ),
    "EUR": FiatCurrency(
        name="Euro",
        code="EUR",
        issuing_country="Eurozone",
    ),
    "GBP": FiatCurrency(
        name="British pound sterling",
        code="GBP",
        issuing_country="United Kingdom",
    ),
    "JPY": FiatCurrency(
        name="Japanese yen",
        code="JPY",
        issuing_country="Japan",
    ),
    "RUB": FiatCurrency(
        name="Russian rouble",
        code="RUB",
        issuing_country="Russian Federation",
    ),
    "CNY": FiatCurrency(
        name="Chinese Yuan",
        code="CNY",
        issuing_country="China",
    ),
    "CHF": FiatCurrency(
        name="CHF Swiss franc",
        code="CHF",
        issuing_country="Switzerland",
    ),
    "BTC": CryptoCurrency(
        name="Bitcoin",
        code="BTC",
        algorithm="SHA-256",
        market_cap=1.12e12,
    ),
    "ETH": CryptoCurrency(
        name="Ethereum",
        code="ETH",
        algorithm="Ethash",
        market_cap=4.5e11,
    ),
    "SOL": CryptoCurrency(
        name="Solana",
        code="SOL",
        algorithm="SHA-256",
        market_cap=6.7e10,
    ),
    "USDT": CryptoCurrency(
        name="Ethereum",
        code="USDT",
        algorithm="Ethash",
        market_cap=1.86e11,
    ),
}

def get_currency(code: str) -> Currency:
    if not isinstance(code, str):
        raise TypeError("Код валюты должен быть строкой")

    code = code.strip().upper()

    try:
        return _CURRENCY_REGISTRY[code]
    except KeyError as exc:
        raise CurrencyNotFoundError(
            f"Валюта с кодом '{code}' не найдена"
        ) from exc

