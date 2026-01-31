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
            f"Недостаточно средств: доступно {available:16.8f} {code}, "
            f"требуется {required} {code}"
        )
        super().__init__(message)


class ApiRequestError(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Ошибка при обращении к внешнему API: {reason}")

