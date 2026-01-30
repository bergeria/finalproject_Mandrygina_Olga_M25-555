# конфигурация API и параметров обновления

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParserConfig:
    """
    Конфигурация парсера курсов валют.
    Все изменяемые параметры вынесены сюда.
    """

    # И откуда взять ключ - может просто здесь сохранить
    EXCHANGERATE_API_KEY: str = field(
        default_factory=lambda: os.getenv("EXCHANGERATE_API_KEY")
    )

    #"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,tether&vs_currencies=usd"
    # URL'ы - сервисов
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price?"

    # https://v6.exchangerate-api.com/v6/d7cf6fad79c863ee3aede32b/latest/USD
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    # Базовая валюта
    BASE_FIAT_CURRENCY: str = "USD"

    FIAT_CURRENCIES: tuple[str, ...] = ("EUR", "GBP", "RUB", "JPY", "GBP", "CNY", "CHF")
    CRYPTO_CURRENCIES: tuple[str, ...] = ("BTC", "ETH", "SOL", "USDT")

    #Словарь для сопоставления кодов и ID для CoinGecko 
    CRYPTO_ID_MAP: dict[str, str] = field(
        default_factory=lambda: {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "USDT" : "tether"
        }
   )

    # Относительные пути
    RATES_FILE_PATH: str = "data\rates.json"
    HISTORY_FILE_PATH: str = "data\exchange_rates.json"

    # Интервал для завпросов
    REQUEST_TIMEOUT: int = 10

    def __post_init__(self):
        if not self.EXCHANGERATE_API_KEY:
            raise RuntimeError(
                "EXCHANGERATE_API_KEY не задан в переменных окружения"
            )
