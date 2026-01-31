"""Обновление и агрегация курсов валют."""

import logging
import time as time_module
from datetime import datetime, timezone

import requests
from requests.exceptions import RequestException

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.api_clients import BaseApiClient
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.storage import (
    BaseRatesStorage,
    ExchangeHistoryStorage,
    ExchangeRateRecord,
)

logger = logging.getLogger("actions")

class RatesUpdater:
    """
    Координирует процесс получения, объединения и сохранения курсов валют.
    """

    def __init__(
        self,
        clients: list[BaseApiClient],
        storage: BaseRatesStorage,
        storage_history: ExchangeHistoryStorage,
    ):
        self._clients = clients
        self._storage = storage
        self._storage_history  = storage_history
        #self._lock = threading.Lock()

    def run_update(self) -> None: #
        # Проверяем кто нас дернул
        #if not self._lock.acquire(blocking=False):
        #    logger.info(f"RatesUpdater уже выполняется (источник: {source})")
        #    return

        logger.info("Обновление курсов началось ...")

        all_rates: dict[str, float] = {}
        sources: list[str] = []

#        print('INFO: Процесс обновления курсов начался.....')

        # Чистый список для exchange_rates.json
        records = []

        # datetime для exchange_rates.json
        now = datetime.now(timezone.utc)

        for client in self._clients:
            client_name = client.__class__.__name__
            logger.info("Получение курсов от %s", client_name)

            start = time_module.perf_counter()
            try:
                rates = client.fetch_rates()
            except ApiRequestError as exc:
                logger.error(
                    "Не удалось получить курсы от  %s: %s",
                    client_name,
                    exc,
                )
                continue  # отказоустойчивость
            except Exception as exc:
                logger.exception(
                    "Неизвестная ошибка в %s",
                    client_name,
                    exc,
                )
                continue

            if not rates:
                logger.warning(
                    "Курсы от %s не получены",
                    client_name,
                )
                print(f"Курсы от {client_name} не получены")
                continue
            elapsed_ms = int((time_module.perf_counter() - start) * 1000)

            logger.info(
                "Получено %d курсов от %s",
                len(rates),
                client_name,
            )

            # Крипта приходит -> BTC_USD - сколько долларов дают за один BTC
            # Фиатные приходят -> EUR_USD - сколько EUR дают за один USD
            # Исходя из этого Фиатные "переворачиваем"
            for pair, rate in rates.items():
                from_cur, to_cur = pair.split("_")
                if client_name == "ExchangeRateApiClient":
                    rates[pair] = 1 / rate
                    rate = rates[pair]
                record = ExchangeRateRecord(
                    from_currency=from_cur,
                    to_currency=to_cur,
                    rate=rate,
                    source=client_name,
                    timestamp=now,
                    meta={
                        "status_code": 200,
                        "request_ms": elapsed_ms
                },
                )
                # Добавляем  словарь к списку
                records.append(record.to_dict())

            all_rates.update(rates)
            sources.append(client_name)

        if not all_rates:
            logger.error("Обновление курсов завершилось неудачей - попробуйте позже !")
            return

        # Формируем словарь в нужном формате для exchange_rates.json

        result = {
            "meta": {
                "last_refresh": datetime.now(timezone.utc).isoformat(),
                "sources": sources,
            },
            "rates": all_rates,
        }

        self._storage.save(result)
        self._storage_history.save(records)

        logger.info(
            "Обновление курсов прошло успешно (%d курсов(а))",
            len(all_rates),
        )


#CoinGeckoClient
class CoinGeckoClient(BaseApiClient):
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


class ExchangeRateApiClient(BaseApiClient):
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

