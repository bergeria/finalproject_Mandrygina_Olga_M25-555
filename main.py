#Основной цикл работы с пользователем

import os

from valutatrade_hub.cli.interface import base_work
from valutatrade_hub.core.utils import clear_screen, show_help
from valutatrade_hub.infra.settings import SettingsLoader
from valutatrade_hub.logging_config import setup_logging

#заготовка под sheduler
#from valutatrade_hub.parser_service.scheduler import start_scheduler_in_background
#from valutatrade_hub.parser_service.updater.rates_updater import RatesUpdater
#from valutatrade_hub.parser_service.storage.JsonRatesStorage, ExchangeHistoryStorage
#from valutatrade_hub.parser_service.config ParserConfig


# По идее система должна быть многопользовательская
# Поэтому к файлам данных обращаемся только по необходимости

def main():

    """ Торговля валютами"""

    # Инициализируем SettingsLoader - Паттерн Singleton
    config_path = os.path.join( os.getcwd(), "config.json")
    settings = SettingsLoader(config_path)

    __logs_dir = os.path.join( os.getcwd(), settings.get("paths", "logs_dir"))

    #Запуск логгера
    setup_logging( logs_dir = __logs_dir)

    print('Программа торговли валютами')

#   storage_rates = JsonRatesStorage(config.RATES_FILE_PATH)
#   storage_history = ExchangeHistoryStorage(config.HISTORY_FILE_PATH)
#   clients = []
#   clients.append( CoinGeckoClient(config))
#   clients.append( ExchangeRateApiClient(config))

#updater = RatesUpdater( clients, storage_rates, storage_history)
#start_scheduler_in_background(updater, interval_seconds=600)
   
    clear_screen()

    print("Добро пожаловать в систему Торговли валютами!  \n")
    
    show_help() # выводим список команд перед началом работы

    #основной цикл находится в модуле interface
    base_work()  #base_work( updater)


if __name__ == "__main__":
    main() # Вызов основной функции
