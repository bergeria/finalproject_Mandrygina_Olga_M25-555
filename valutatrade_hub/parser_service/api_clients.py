# работа с внешними API
# api_clients.py


from abc import ABC, abstractmethod

import requests
from requests.exceptions import RequestException

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import ParserConfig


class BaseApiClient(ABC):
    """
    Унифицированный интерфейс для получения курсов валют
    """

    @abstractmethod
    def fetch_rates(self) -> dict[str, float]:
        """
        Возвращает курсы в стандартизированном формате:
        {
            "BTC_USD": 59337.21,
            "EUR_USD": 1.09,
            ...
        }
        """
        raise NotImplementedError





class CoinGeckoClient( BaseApiClient): 
    def __init__(self, config: ParserConfig):
        self._config = config


    def fetch_rates(self) -> dict[str, float]:
        ids = ",".join(self._config.CRYPTO_ID_MAP.values())
        vs_currency = self._config.BASE_FIAT_CURRENCY.lower()

        params = {
            "ids": ids,
            "vs_currencies": vs_currency,
        }

        try:
            response = requests.get(
                self._config.COINGECKO_URL,
                params=params,
                timeout=self._config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except RequestException as exc:
            raise ApiRequestError(
                f"Ошибка при обращении к CoinGecko API: {exc}"
            ) from exc

        data = response.json()

        rates: dict[str, float] = {}

        for code, coin_id in self._config.CRYPTO_ID_MAP.items():
            try:
                price = data[coin_id][vs_currency]
                rates[f"{code}_{self._config.BASE_FIAT_CURRENCY}"] = float(price)
            except (KeyError, TypeError):
                raise ApiRequestError(
                    f"Некорректный ответ CoinGecko для {code}"
                )

        return rates



#ExchangeRateApiClient

class ExchangeRateApiClient( BaseApiClient):
    def __init__(self, config: ParserConfig):
        self._config = config

    def fetch_rates(self) -> dict[str, float]:
        url = (
            f"{self._config.EXCHANGERATE_API_URL}/"
            f"{self._config.EXCHANGERATE_API_KEY}/"
            f"latest/{self._config.BASE_FIAT_CURRENCY}"
        )

        try:
            response = requests.get(
                url,
                timeout=self._config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except RequestException as exc:
            raise ApiRequestError(
                f"Ошибка при обращении к ExchangeRate API: {exc}"
            ) from exc

        data = response.json()

        if data.get("result") != "success":
            raise ApiRequestError(
                f"ExchangeRate API вернул ошибку: {data.get('error-type')}"
            )

        rates_raw = data.get("conversion_rates")
        if not isinstance(rates_raw, dict):
            raise ApiRequestError("Некорректный формат ответа ExchangeRate API")

        rates: dict[str, float] = {}

        for code in self._config.FIAT_CURRENCIES:
            if code not in rates_raw:
                continue

            pair = f"{code}_{self._config.BASE_FIAT_CURRENCY}"
            rates[pair] = float(rates_raw[code])

        return rates



