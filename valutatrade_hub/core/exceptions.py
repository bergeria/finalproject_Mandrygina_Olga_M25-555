# exceptions.py
#Пользовательские исключения

#Цель: Обработка исключений
#Правки:
##buy(user_id, currency_code, amount):
#Валидация amount > 0, currency_code → get_currency().
#Автосоздание кошелька при отсутствии валюты.
#wallet.deposit(amount); при необходимости — оценочная стоимость:
#Логирование через @log_action.
#sell(user_id, currency_code, amount):
#Валидация входа.
#Проверка кошелька и средств — иначе InsufficientFundsError.
#wallet.withdraw(amount); оценочная выручка в USD (если нужно).
#Логирование через @log_action.
#get_rate(from_code, to_code):
#Валидация кодов через get_currency() — иначе CurrencyNotFoundError.
#Использовать TTL из SettingsLoader: если кеш rates.json устарел
# — попытаться обновить (иначе ApiRequestError).
#Возврат значение курса + updated_at.
#Задачи:
#Переписать логику валидации валют через currencies.py.
#Включить бросание и проброс исключений в соответствующих местах.
#Вызовы DatabaseManager/JSON-хранилища обернуть в безопасные операции
# (чтение→модификация→запись).


#Обновления CLI (cli/interface.py)
#Цель: Поддержать новые ошибки, логику и (опционально) служебные команды.
#Изменения команд:
#buy, sell — обогащённые сообщения об успехе/ошибках.
#get-rate — точные сообщения при CurrencyNotFoundError и ApiRequestError.




#from exceptions import CurrencyNotFoundError
#from valutatrade_hub.core.currencies import Currency


class CurrencyError(Exception):
    """Базовое исключение для валютного домена"""
    pass


class CurrencyNotFoundError(CurrencyError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Неизвестная валюта '{code}'")


class InsufficientFundsError(Exception):
    def __init__(self, available: float, required: float, code: str) -> None:
        self.available = available
        self.required = required
        self.code = code

        message = (
            f"Недостаточно средств: доступно {available} {code}, "
            f"требуется {required} {code}"
        )
        super().__init__(message)


class ApiRequestError(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Ошибка при обращении к внешнему API: {reason}")



#def get_currency(code: str) -> Currency:
#    if not isinstance(code, str):
#        raise TypeError("Currency code must be a string")#

#    normalized = code.strip().upper()

##    try:
 #       return _CURRENCY_REGISTRY[normalized]
 #   except KeyError:
 #       raise CurrencyNotFoundError(normalized)


# wallet.py
#from exceptions import InsufficientFundsError
#from currencies import Currency
#

#class Wallet:
#    def __init__(self, currency: Currency, balance: float = 0.0) -> None:
#        self.currency = currency
#        self.balance = float(balance)

#    def withdraw(self, amount: float) -> None:
#        if amount <= 0:
#            raise ValueError("Withdraw amount must be positive")

#        if self.balance < amount:
#            raise InsufficientFundsError(
#                available=self.balance,
#                required=amount,
#                code=self.currency.code,
#            )

#        self.balance -= amount


# usecases/sell.py
#from wallet import Wallet

#
#def sell(wallet: Wallet, amount: float) -> None:
#    """
#    Use-case продажи актива.
#    Может выбросить InsufficientFundsError.
#    """
#    wallet.withdraw(amount)

    # логика продажи (заглушка)
    # send order to exchange


# services/rates.py
#from exceptions import ApiRequestError


#def get_rate(from_code: str, to_code: str) -> float:
#    """
#    Получение курса валют.
#    """
#    try:
#        # заглушка внешнего API
#        raise TimeoutError("Request timeout")
#    except Exception as exc:
#        raise ApiRequestError(str(exc)) from exc


#try:
#    wallet.withdraw(10)
#except InsufficientFundsError as exc:
#    print(str(exc))
#except CurrencyNotFoundError as exc:
#    print(str(exc))
#except ApiRequestError as exc:
#    print(str(exc))


#[ Domain ]
#  Currency
#  Wallet
#  Exceptions  ← ВАЖНО: здесь живут сообщения

#[ Application ]
#  sell()
#  buy()

#[ Infrastructure ]
#  get_rate()
#  external APIs
