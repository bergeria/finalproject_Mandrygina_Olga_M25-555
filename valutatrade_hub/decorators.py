from __future__ import annotations

import functools
import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional

_actions_logger = logging.getLogger("actions")


@dataclass(frozen=True)
class ActionLogData:
    action: str
    username: Optional[str] = None
    user_id: Optional[str] = None
    currency_code: Optional[str] = None
    amount: Optional[Any] = None
    rate: Optional[Any] = None
    base: Optional[str] = None
    result: str = "OK"
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    verbose_before: Optional[str] = None
    verbose_after: Optional[str] = None


def _pick(d: dict[str, Any], keys: list[str]) -> Any:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def _fmt_value(v: Any) -> str:
    if v is None:
        return "None"
    return str(v)


def _to_message(data: ActionLogData) -> str:
    # Пример:
    # BUY user='alice' currency='BTC' amount=0.0500 rate=59300.00 base='USD' result=OK
    who = None
    if data.username is not None:
        who = f"user='{data.username}'"
    elif data.user_id is not None:
        who = f"user_id='{data.user_id}'"
    else:
        who = "user='unknown'"

    parts = [
        data.action,
        who,
    ]

    if data.currency_code is not None:
        parts.append(f"currency='{data.currency_code}'")
    if data.amount is not None:
        parts.append(f"amount={_fmt_value(data.amount)}")
    if data.rate is not None:
        parts.append(f"rate={_fmt_value(data.rate)}")
    if data.base is not None:
        parts.append(f"base='{data.base}'")

    parts.append(f"result={data.result}")

    if data.result == "ERROR":
        if data.error_type:
            parts.append(f"error_type={data.error_type}")
        if data.error_message:
            parts.append(f"error_message='{data.error_message}'")

    if data.verbose_before is not None or data.verbose_after is not None:
        parts.append(f"ctx='{data.verbose_before}→{data.verbose_after}'")

    return " ".join(parts)


def log_action(action: str, *, verbose: bool = False) \
        -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для прозрачной трассировки доменных операций.
    - Логирует INFO.
    - Не глотает исключения.
    - verbose=True добавляет контекст "было→стало" (если удаётся получить).
    """
    action = action.upper()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 1) Пытаемся вытащить входные параметры из kwargs
            username = _pick(kwargs, ["username", "user", "login"])
            user_id = _pick(kwargs, ["user_id", "uid"])
            currency_code = _pick(kwargs, ["currency_code", "code", "currency"])
            amount = _pick(kwargs, ["amount", "qty", "value"])
            rate = _pick(kwargs, ["rate", "price"])
            base = _pick(kwargs, ["base", "base_currency"])

            # 2) verbose контекст: "было"
            before = None
            after = None
            if verbose:
                # Если первый аргумент — объект usecase,
                # то попробуем взять у него wallet/account
                # делаем чтобы не сломать
                self_obj = args[0] if args else None
                before = _extract_wallet_state(self_obj,
                                               username=username,
                                               user_id=user_id)

            try:
                result = func(*args, **kwargs)
                if verbose:
                    self_obj = args[0] if args else None
                    after = _extract_wallet_state(self_obj,
                                                  username=username,
                                                  user_id=user_id)

                data = ActionLogData(
                    action=action,
                    username=username,
                    user_id=user_id,
                    currency_code=currency_code,
                    amount=amount,
                    rate=rate,
                    base=base,
                    result="OK",
                    verbose_before=before,
                    verbose_after=after,
                )
                _actions_logger.info(_to_message(data))
                return result

            except Exception as exc:
                if verbose:
                    self_obj = args[0] if args else None
                    after = _extract_wallet_state(self_obj,
                                                  username=username,
                                                  user_id=user_id)

                data = ActionLogData(
                    action=action,
                    username=username,
                    user_id=user_id,
                    currency_code=currency_code,
                    amount=amount,
                    rate=rate,
                    base=base,
                    result="ERROR",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                    verbose_before=before,
                    verbose_after=after,
                )
                # Требование: логировать INFO даже при ошибках
                _actions_logger.info(_to_message(data))
                raise

        return wrapper

    return decorator


def _extract_wallet_state(self_obj: Any, *, username: Any, user_id: Any) \
        -> Optional[str]:
    """
    Пытаемся извлечь состояние кошелька для verbose-лога.
    Эта функция специально "мягкая": если структуры нет — вернёт None.
    """
    if self_obj is None:
        return None

    # Частые паттерны: self.wallet_repo / self.accounts / self.user_repo
    # Пробуем несколько вариантов, ничего не требуя жёстко.
    try:
        repo = (getattr(self_obj, "wallet_repo", None) or
                getattr(self_obj, "account_repo", None))
        if repo is None:
            return None

        # Пытаемся получить кошелёк/аккаунт
        if username is not None and hasattr(repo, "get_by_username"):
            w = repo.get_by_username(username)
        elif user_id is not None and hasattr(repo, "get_by_user_id"):
            w = repo.get_by_user_id(user_id)
        elif username is not None and hasattr(repo, "get"):
            w = repo.get(username)
        else:
            return None

        # Формат состояния — под твой домен:
        # - balance + currency_code
        bal = getattr(w, "balance", None) or getattr(w, "_balance", None)
        cur = getattr(w, "currency_code", None) or getattr(w, "currency", None)
        return f"balance={bal} {cur}"
    except Exception:
        return None
