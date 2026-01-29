# @log_action (логирование операций)
#core/decorators.py

import functools
import logging
from datetime import datetime
from typing import Callable

logger = logging.getLogger(__name__)


def log_action(action: str, verbose: bool = False) -> Callable:
    """
    Декоратор логирования доменных операций.
    """

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.utcnow().isoformat()
            result = "OK"

            try:
                if verbose:
                    before = kwargs.get("wallet_before")

                result_value = func(*args, **kwargs)

                return result_value

            except Exception as exc:
                result = "ERROR"
                error_type = type(exc).__name__
                error_message = str(exc)

                logger.info(
                    "%s user=%r result=%s error=%s:%s",
                    action,
                    kwargs.get("username") or kwargs.get("user_id"),
                    result,
                    error_type,
                    error_message,
                )

                raise  # ❗ исключение НЕ глотаем

            finally:
                log_parts = {
                    "action": action,
                    "user": kwargs.get("username") or kwargs.get("user_id"),
                    "currency": kwargs.get("currency_code"),
                    "amount": kwargs.get("amount"),
                    "rate": kwargs.get("rate"),
                    "base": kwargs.get("base_currency"),
                    "result": result,
                }

                message = " ".join(
                    f"{k}={v!r}" for k, v in log_parts.items() if v is not None
                )

                logger.info(message)

        return wrapper

    return decorator
