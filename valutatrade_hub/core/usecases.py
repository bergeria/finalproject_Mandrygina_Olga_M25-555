# бизнес-логика 
#usecases.py 


import json
import os

from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.models import (
    Portfolio,
    User,
    current_portf,
    current_user,
)
from valutatrade_hub.parser_service.api_clients import (
    CoinGeckoClient,
    ExchangeRateApiClient,
)
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.storage import (
    ExchangeHistoryStorage,
    JsonRatesStorage,
)
from valutatrade_hub.parser_service.updater import RatesUpdater


# обновить курсы - Пример update-rates --source coingecko
# обновить курсы - Пример update-rates --source exchangerate
# Пример update-rates - если без параметров то используем оба источника
def update_rates( __arg_list : dict):
    """Обновление курсов из внешних источников"""

    try:
        config = ParserConfig() # Кучка параметров
    except (Exception) as e:
        print(f"\nОшибка : - {e}")


    # Чисты список клиентов
    clients = []


    #(Файл/JSON storage)
    storage_rates = JsonRatesStorage(config.RATES_FILE_PATH)
    storage_history = ExchangeHistoryStorage(config.HISTORY_FILE_PATH)

    #Если есть параметр
    match __arg_list.get("source") :
        case "coingecko": # CoinGecko
            clients.append( CoinGeckoClient(config))

        case "exchangerate": # ExchangeRateApiClient
            clients.append( ExchangeRateApiClient(config))

        case _:  # Если нет параметров - то оба источника
            clients.append( CoinGeckoClient(config))
            clients.append( ExchangeRateApiClient(config))


    # класс RatesUpdater - запрашивает курсы из внешних источников
    updater = RatesUpdater( clients, storage_rates, storage_history)
    updater.run_update()

    return

#Команда show_rates - из rates.json
def show_rates( __args : dict ) -> None :
    """Назначение: показать все курсы rates.json"""

    try:
        config = ParserConfig() # Кучка параметров
    except (Exception) as e:
        print(f"\nОшибка : - {e}")

    storage_rates = JsonRatesStorage( config.RATES_FILE_PATH)
    curses = storage_rates.load()
    print(f'Дата обновления {curses["meta"]["last_refresh"]}\n')
    print(f'Источники обновления {curses["meta"]["sources"]}\n')

    if __args.get("top") is not None: # самые дорогие из всех
        # Сортируем по убыванию value
        cnt = int(__args.get("top"))
        sorted_data = dict(sorted(curses["rates"].items(), key=lambda item: item[1], reverse=True)[:cnt])
        for key, value in sorted_data.items():
            print(f" -  {key}: {value:16.8f}")
        return

    if __args.get("currency") is not None: # Курс одной валюты
        if __args.get("currency").upper == "USD" :
            print(f' -  "USD_USD" = 1.00\n')
            return
        c_name = "".join(f'{__args.get("currency")}_USD')
        crs = curses["rates"].get(c_name)
        if crs is None :
            print(f'Курс не найден {curses["rates"].get("currency")}\n')
            return
        print(f' -  {c_name} : {crs:16.8f}\n')
        return

    # Курсы всех валют
    for item in curses["rates"] :
        val = curses["rates"][item]
        print(f'Источники обновления {item} - {val:.8f}\n')

    # Конец show_rates

#Команда get-rate - из rates.json
# Пример
# > get-rate --from USD --to BTC
#    Курс USD→BTC: 0.00001685 (обновлено: 2025-10-09 00:03:22)
#    Обратный курс BTC→USD: 59337.21
# Если курс свежий (например, моложе 5 минут) — показать его.
# Иначе — запросить у Parser Service (или использовать заглушку) → обновить кеш.
# Но пока заглушка

def get_rate( __arg_list : dict) :

    """Назначение: получить текущий курс одной валюты к другой из rates.json"""
    global current_portf

    __from = __arg_list.get( "from", None)
    __to = __arg_list.get( "to", None)

    if __from is None or __to is None :
        print('Некорректная команда')
        return

    match True:
        case x if __to == "USD": # Типа прямой курс
            d_curs = Portfolio._get_exchange_rates( __from, __to)
            if d_curs is None :
                print("Нет информации о курсах !!\n")
                return
            print(f'Найденный курс {d_curs:16.4f} !!\n') # Формат 16.4f

        case x if  __from == "USD": # Обратный курс
            d_curs = Portfolio._get_exchange_rates(__to, __from)
            if d_curs is None :
                print("Нет информации о курсах !!\n")
                return
            d_curs = 1/d_curs # Ну вряд ли курс может быть равен 0
            print(f'Найденный курс {d_curs:16.8f} !!\n') # Формат 16.8f

        case x if "USD" not in [__from, __to]:  # Кросс курс
            print('Все курсы привязаны к доллару - попробуем найти кросс курс !!!\n')
            print(f'Запрошен курс {__from} к {__to} !!!\n')
            d_curs = Portfolio._get_exchange_rates(__from, __to)
            if d_curs is None:
                print("Нет информации о курсах !!\n")
                return
            print(f'Найденный курс {__from} к {__to} - {d_curs:16.8f} !!\n')

    return

    # Конец get-rate

#Команда sell
#   Аргументы:
#   *    --currency <str> — код валюты.
#   *    --amount <float> — количество продаваемой валюты.
#Пример:
#    > sell --currency EUR --amount 100

def sell( __arg_list : dict) :

    """Назначение: продать валюту"""

    global current_user
    global current_portf

    #Прверяем есть ли активный пользователь
    if current_user is None :
        print('\n\nСначала войдите в систему\n\n')
        return

    __currency = __arg_list.get( "currency", None) 
    __amount = float(__arg_list.get( "amount", None))

    if __currency is None or __amount is None :
        print('Некорректная команда')
        return

    #Прверяем желаемое количество валюты
    if __amount <= 0 :
        print("\n\n Количество желаемой валюты должно быть больше 0\n\n")
        return

    # Портфолито до продажи
    #current_portf.show_portfolio()

    # Обработка исключений
    try:
        current_portf.sell_currency( __currency, __amount)
    except ValueError as e:
        print(f"Ошибка операции: {e}")

    # Ссохраняем Портфолито
    current_portf.save_portfolio()

    # Портфолито после продажи
    #quitcurrent_portf.show_portfolio()

    #Пример команды - sell --currency EUR --amount 150
    #Логика - продать валюту 150 EUR, полученные $ в кошелек

    #Конец sell


#купить валюту (buy);
#   --currency <str> — код покупаемой валюты (например, BTC).
#   --amount <float> — количество покупаемой валюты (в штуках, не в долларах).
def buy( __arg_list : dict) -> None:

    """Назначение: купить валюту"""

    global current_user
    global current_portf

    #Прверяем есть ли активный пользователь
    if current_user is None :
        print('\n\nСначала войдите в систему\n\n')
        return

    __currency = __arg_list.get( "currency", None) 
    __amount = float(__arg_list.get( "amount", None))

    if __currency is None or __amount is None :
        print('Некорректная команда')
        return

    #Прверяем желаемое количество валюты
    if __amount <= 0 :
        print("\n\n Количество желаемой валюты должно быть больше 0\n\n")
        return

    # Портфолито до покупки
    #current_portf.show_portfolio()

    # Обработка исключений
    try:
        current_portf.buy_currency( __currency, __amount)
    except ValueError as e:
        print(f"Ошибка операции: {e}")

    # Ссохраняем Портфолито
#    current_portf.save_portfolio()

    # Портфолито после покупки
    #current_portf.show_portfolio()

    #Пример команды - buy --currency EUR --amount 150.05
    #Логика - купить валюту EUR на  150.05$

    #Конец Buy

#Внести деньги на баланс
def deposit( __args : dict) -> None:

    global current_user
    global current_portf

    #Прверяем есть ли активный пользователь
    if current_user is None :
        print('\n\nСначала войдите в систему\n\n')
        return

    currency_code = __args.get("currency", None)
    amount = __args.get("amount", None)

    if currency_code is None or amount is None :
        print('\n\nКоманда не опознана \n\n')
        return

    # Если такого кошелька еще не было - добавляем
    if currency_code not in current_portf._wallets:
        current_portf.add_currency(currency_code)
    #Берем кошелек - нужно проверить наличие кошелька
    target_wallet = current_portf.get_wallet( __args["currency"])

    #Пополняем кошелек
    target_wallet.deposit( float(amount))

    # Ссохраняем Портфолито
    current_portf.save_portfolio()



#показать все кошельки и итоговую стоимость в базовой валюте (по умолчанию USD).
def show_portfolio() : #__base = "USD"

    """показать все кошельки и итоговую стоимость в базовой валюте (по умолчанию USD)"""

    global current_user
    global current_portf

    #Прверяем есть ли активный пользователь
    if current_user is None :
        print('\n\nСначала войдите в систему\n\n')
        return

    current_portf.show_portfolio()

    # Конец show_portfolio


def register( __arg_list : dict) :
    
    """Регистрация нового пользователя"""

    global current_user
    global current_portf

    #Прверяем есть ли активный пользователь
    if current_user is not None :
        print('Сначала закройте сессию теущего пользователя')
        return

    if len(__arg_list) != 2:
        print('Некорректная команда')
        return

    __username = __arg_list.get("username", None)
    __password = __arg_list.get("password", None)

    if __username is None or __password is None :
        print('Некорректная команда')
        return

    #Прверяем длину пароля
    if len(__password) < 4 :
        print('\n\nОшибка - Пароль должен быть не менее 4-х символов !!!\n\n')
        return

    #Возвращает текущую рабочую директорию.
    c_path = os.getcwd()
    # файл со списком пользователей
    f_users = os.path.join( c_path, 'data', 'users.json')

    # Бывают прикольчики
    if os.path.exists(f_users) and (os.path.getsize(f_users) == 0) :
        os.remove(f_users)

    tst = -1 # начальный user_id
    content = [] #Готовим чистый список

    if os.path.exists(f_users): #если файл есть и он не пустой
        with open(f_users, 'r', encoding='utf-8') as f:
            content = json.load(f) # Читаем и разбираем json формат
        #Проверяем имя пользователя
        for d_item in content :
            if d_item["username"] != __username :
                if d_item["user_id"]  > tst :
                    tst = d_item["user_id"] # Ищем "последнее" значение "user_id"
            else : # если пользователь есть - то Ошибка
                print(f' Имя занято - {d_item["username"]}!!!\n')
                return

    # Был файл или небыл -> продолжаем
    # И имя пользователя является уникальным

    # создаем экземпляр Users и храним его в глобальной переменной current_user
    # в методе __init__ есть именованные аргументы
    current_user = User( user_id=tst + 1, username=__username, password=__password)

    list_dict = current_user.to_dict()

    # добавляем к списку
    content.append(list_dict)
    
    # перезаписываем файл если он был, а если не был то создаем новый
    with open( f_users, 'w', encoding='utf-8') as f:
        json.dump( content, f, indent=4, ensure_ascii=False)

    # Создать экземпляр класа Portfolio для пользователя
    current_portf = Portfolio( current_user)

    # Добавляем нового пользователя Portfolio в 'portfolios.json'
    #current_portf.add_portfolio_to_file()

    #Вроде успех
    print(f'\n {list_dict["username"]} зарегистрирован id({list_dict["user_id"]})\n')

    #очищаем current_user И current_portf - регистрация - это не логин
    current_user = None
    current_portf = None

    print(f'\nВойдите: login --username {list_dict["username"]} --password ****\n')

    # Конец register


#войти в систему
def login( __arg_list : dict) :

    """Вход пользователя в систему"""

    global current_user
    global current_portf

    #Прверяем есть ли активный пользователь
    if current_user is not None :
        print('Сначала закройте сессию теущего пользователя')
        return

    if len(__arg_list) != 2:
        print('Некорректная команда')
        return

    #print('Список аргументов __arg_list - ', __arg_list, '\n')

    __username = __arg_list.get("username", None)
    __password = __arg_list.get("password", None)

    if __username is None or __password is None :
        print('Некорректная команда')
        return

    #Получаем текущую рабочую директорию.
    c_path = os.getcwd()
    # файл со списком пользователей
    f_users = os.path.join( c_path, 'data', 'users.json')

    # Бывают прикольчики
    if ( not os.path.exists(f_users)) or ( os.path.getsize(f_users) and (os.path.getsize(f_users) == 0)) : # noqa: E501
        print("Пользователь с таким логином не найден\n\n")
        return

    #Если мы здесь - то файл есть и он не пустой
    with open(f_users, 'r', encoding='utf-8') as f:
        content = json.load(f) # Читаем и разбираем json формат

    #Ищем имя пользователя в списке всех пользователей
    t_user = {}

    for d_item in content :
        if d_item["username"] == __username : # может лучше d_item.get()
            t_user = d_item # Нашли пользователя
            break

    if len(t_user) == 0 :
        print("Нет такого пользователя → \n\nПользователь '", __username, "' не найден")
        return

    #Если мы здесь - значит пользователь найден и нужно проверить пароль
   
    #Получаем хеш пароля из логина
    t_pass = User._h_password( __password, t_user["salt"])

    if t_pass != t_user["hashed_password"] :
        print('\n\nОшибка - Неверный пароль !!!\n\n')
        return
    
    #Инициализируем экземпляр класса - и заполняем глобальную переменную
    current_user = User.from_dict( t_user)

    # Создать экземпляр класа Portfolio и дать ему пользователя
    current_portf = Portfolio( current_user)

    print('\n\nВы вошли как - ', t_user["username"], '\n\n')
    return
    #Конец login


#выйти из системы
def logout() :

    """Выход пользователя из системы"""

    global current_user
    global current_portf

    if current_user is None :
        return # Если не было login

    #Типа выходим - заполняем глобальные переменные

    # Очищаем профиль текущего ползователя
    current_portf = None

    # Очищаем текущего ползователя
    current_user = None

    print( " Выход пользователя из системы - logout\n")

    #Конец logout


# Вывод информации о конкретной валюте
def get_currency_info ( __args : dict) :

    code = __args.get("currency", None)
    if code is None :
        raise ValueError("Ошибка в параметрах !!!")

    currency = get_currency(code)
    print(currency.get_display_info())



#from core.decorators import log_action


#@log_action("BUY")
#def buy(
#    *,
#    user_id: int,
#    currency_code: str,
#    amount: float,
#    rate: float,
#   base_currency: str = "USD",
#):


#@log_action("SELL", verbose=True)
#def sell(
#    *,
#    user_id: int,
#    currency_code: str,
#    amount: float,
#    rate: float,
#    base_currency: str = "USD",
#):

#@log_action("REGISTER")
#def register(username: str, password: str):

#import json
#import os

#from valutatrade_hub.core.models import (
#    Portfolio,
#    User,
#    current_portf,
#    current_user,
#)

# Обработка исключений
#try:
#    f()
#except ValueError as e:
#    print(f"Ошибка значения: {e}")
#except KeyError as e:
#    print(f"Нет такой валюты: {e}")
#except Exception as e:
#    print(f"Неизвестная ошибка: {e}")
#finally:
#    print("Операция завершена")
