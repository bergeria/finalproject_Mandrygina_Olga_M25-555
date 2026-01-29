# scheduler.py
# scheduler.py

from datetime import datetime
import logging
import threading
import time

logger = logging.getLogger(__name__)


def schedule_rates_update( updater, interval_seconds: int = 600):

    while True:
        start = datetime.now()
        logger.info("Scheduler: запуск обновления курсов")

        try:
            updater.run_update()
            logger.info("Scheduler: обновление завершено успешно")
        except Exception as e:
            logger.exception(f"Scheduler: ошибка обновления: {e}")

        elapsed = (datetime.now() - start).total_seconds()
        time.sleep(max(0, interval_seconds - elapsed))


def start_scheduler_in_background(updater, interval_seconds: int = 600) -> threading.Thread: # noqa E501
    """
    Запускает планировщик в фоне (daemon thread)
    """
    thread = threading.Thread(
        target=schedule_rates_update,
        args=(updater, interval_seconds),
        daemon=True,   # При выходе из программы, фоновый процесс закроется сам
        name="RatesUpdaterScheduler",
    )
    thread.start()
    logger.info("Scheduler запущен в фоновом режиме")
    return thread
