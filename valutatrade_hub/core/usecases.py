import json
import os

from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.models import (
    Portfolio,
    User,
)
from valutatrade_hub.decorators import log_action
from valutatrade_hub.infra.settings import SettingsLoader
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

"""Модуль основной логик"""

#Глобальные переменные текущий пользователь и его портфолио
current_portf = None
current_user = None

def get_user_filename() -> str :

    #беерм настройки из Singleton
    settings = SettingsLoader()
    try:
        _path = settings.get( "paths", "data_dir")
    except KeyError:
        raise ValueError('Имя файла со списком пользователей\n')
        return

    try:
        _name = settings.get( "paths", "users_json")
    except KeyError :
        raise ValueError('Относительный путь к файлу со списком пользователей\n')
        return

    #Получаем текущую рабочую директорию.
    c_path = os.getcwd()
    # файл со списком пользователей
    f_name = os.path.join( c_path, _path, _name)

    return f_name

# обновить курсы - Пример update-rates --source coingecko
# обновить курсы - Пример update-rates --source exchangerate
# Пример update-rates - если без параметров то используем оба источника
#@log_action("UPDATE_RATES", verbose=True)
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
        __t_val = __args.get("top")
        try :
            cnt = int(__t_val)
        except ValueError :
            raise ValueError('\nКоличество валют должно быть целым числом\n')
        sorted_data = dict(sorted(curses["rates"].items(),
                                  key=lambda item: item[1],
                                  reverse=True)[:cnt])
        for key, value in sorted_data.items():
            print(f" -  {key}: {value:16.8f}")
        return

    if __args.get("currency") is not None: # Курс одной валюты
        if __args.get("currency").upper == "USD" :
            print(' -  "USD_USD" = 1.00\n')
            return
        c_name = "".join(f'{__args.get("currency")}_USD')
        crs = curses["rates"].get(c_name)
        if crs is None :
            print(f'Курс не найден {c_name}\n')
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

    try:
        __from = __arg_list["from"]
        __to = __arg_list[ "to"]
    except KeyError :
        raise ValueError("Не верные параметры !!\n")

    # Прежде чем искать курсы
    # Проверяем корректность кодов валют
    get_currency( __from)
    get_currency( __to)

    d_curs = Portfolio._get_exchange_rates(__from, __to)
    if d_curs is None:
        raise ValueError("Нет информации о курсах !!\n")

    print(f'Найденный курс {d_curs:16.4f} !!\n')  # Формат 16.4f

    # Конец get-rate


#Для логирования
@log_action("SELL", verbose=True)
def __sell(  username: str, currency_code: str, amount: float ) -> None :
    pass

#Команда sell
#   Аргументы:
#   *    --currency <str> — код валюты.
#   *    --amount <float> — количество продаваемой валюты.
def sell( __arg_list : dict) :

    """Назначение: продать валюту"""

    global current_user
    global current_portf

    #Проверяем есть ли активный пользователь
    if current_user is None :
        raise ValueError("\n\n !!! Сначала войдите в систему !!!\n\n")

    # Параметры по ключам, если нет -> KeyError Неверные параметры
    try:
        __currency = __arg_list["currency"]
        __amount = __arg_list["amount"]
    except KeyError :
        raise ValueError("\n\n !!! Не верные параметры !!!\n\n")

    # Проверяем код валюты на наличие в курсах
    get_currency(__currency)

    # Проверяем количество на предмет числового значения
    try :
        __amount = float(__amount)
    except ValueError:
        raise ValueError('Сумма указана не верно !!!\n')
    except TypeError:
        raise ValueError('Сумма указана не верно !!!\n')

    #Прверяем желаемое количество валюты
    if __amount <= 0 :
        raise ValueError('Сумма должна быть больше 0 !!!\n')

    # Обработка исключений в interface.py
    current_portf.sell_currency( __currency, __amount)

    # Сохраняем портфолио
    current_portf.save_portfolio()

    #Для логировнаия
    __sell(  username = current_user.username,
            currency_code = __currency,
            amount = __amount)

    #Конец sell

#Для логирования
@log_action("BUY", verbose=True)
def __buy(  username: str, currency_code: str, amount: float ) -> None :
    pass

#купить валюту (buy);
#   --currency <str> — код покупаемой валюты (например, BTC).
#   --amount <float> — количество покупаемой валюты (в штуках, не в долларах).
def buy( __arg_list : dict) -> None:

    """Назначение: купить валюту"""

    global current_user
    global current_portf

    #Проверяем есть ли активный пользователь
    if current_user is None :
        raise ValueError("\n\n !!! Сначала войдите в систему !!!\n\n")

    # Параметры по ключам, если нет -> KeyError Неверные параметры
    try:
        __currency = __arg_list["currency"]
        __amount = __arg_list["amount"]
    except KeyError :
        raise ValueError("Не верные параметры !!\n")

    # Здесь нужно проверить код валюты на наличие в курсах
    get_currency(__currency)

    # Проверяем количество на предмет числового значения
    try :
        __amount = float(__amount)
    except ValueError:
        raise ValueError('Сумма указана не верно !!!\n')
    except TypeError:
        raise ValueError('Сумма указана не верно !!!\n')

    #Прверяем желаемое количество валюты
    if __amount <= 0 :
        raise ValueError('Сумма должна быть больше 0 !!!\n')

    # Портфолито до покупки
    #current_portf.show_portfolio()

    current_portf.buy_currency( __currency, __amount)

    #Если до этого места возникнут исключения - то мы суда не придем
    # Сохраняем портфолио
    current_portf.save_portfolio()

    #Для логировнаия
    __buy(  username = current_user.username,
            currency_code = __currency,
            amount = __amount)

    #Конец Buy

#Для логирования
@log_action("DEPOSIT", verbose=True)
def __depopsit(  username: str, currency_code: str, amount: float ) -> None :
    pass

#Внести деньги на баланс
def deposit( __args : dict) -> None:

    global current_user
    global current_portf

    #Прверяем есть ли активный пользователь
    if current_user is None :
        raise ValueError('\n\nСначала войдите в систему\n\n')

    # Если нужных параметров нет, то будет исключение KeyError
    try:
        currency_code = __args["currency"]
        amount = __args["amount"]
    except KeyError :
        raise ValueError("Не верные параметры !!\n")

    if currency_code is None or amount is None : # это уже наверное перебор
        raise ValueError('\n\nНеверные параметры команды !!!\n\n')

    #Проверяем amount - на предмет числового значения
    try:
        amount = float(amount)
    except ValueError :
        raise ValueError('\n Количество валюты должно быть числом\n')

    if amount <= 0 :
        raise ValueError('\n Количество валюты должно быть > 0\n')

    # Здесь нужно проверить код валюты на наличие в курсах
    get_currency(currency_code)

    # Нужно проверить наличие кошелька
    # Если такого кошелька еще не было - добавляем
    if currency_code not in current_portf._wallets:
        current_portf.add_currency(currency_code)

    # Берем кошелек
    target_wallet = current_portf.get_wallet( currency_code)

    #Пополняем кошелек
    target_wallet.deposit( amount)

    # Ссохраняем Портфолито
    current_portf.save_portfolio()

    #Для логирования
    __depopsit(  username = current_user.username,
                 currency_code = currency_code,
                 amount = amount)

    #Конец deposit


#показать все кошельки и итоговую стоимость в базовой валюте (по умолчанию USD).
def show_portfolio(  __args : dict) : # в указанной валюте

    """показать все кошельки и итоговую стоимость в базовой валюте (по умолчанию USD)"""

    global current_user
    global current_portf

    #Прверяем есть ли активный пользователь
    if current_user is None :
        raise ValueError('\n\nСначала войдите в систему\n\n')

    # Для контроля параметров
    __currency_code = None

    #Если есть какие-то параметры - то пробуем их разобрать
    if len(__args) != 0:
        try:
            __currency_code = __args["base"]
        except KeyError: # Если нет ключа "base"
            raise ValueError('Неверные параметры !!!!\n\n')

    if __currency_code is None:
        __currency_code = "USD" # Если кода нет - то USD

    # код есть, его надо проверить на наличие
    get_currency(__currency_code)

    # Показываем портфолио
    current_portf.show_portfolio( __currency_code)
    # И общую сумму в нужной валюте

    # Конец show_portfolio

@log_action("REGISTER")
def __register( username: str, user_id: int) :
    pass

def register( __arg_list : dict) :
    
    """Регистрация нового пользователя"""

    global current_user
    global current_portf

    #Прверяем есть ли активный пользователь
    if current_user is not None :
        raise ValueError("\n!!! Сначала закройте сессию текущего пользователя !!!\n")

    try:
        __username = __arg_list["username"]
        __password = __arg_list["password"]
    except KeyError :
        raise ValueError("Не верные параметры !!\n")

    if __username is None or __password is None :
        raise ValueError("\n\n !!! Неверные пркаметры !!!\n\n")

    #Прверяем длину пароля
    if len(__password) < 4 :
        raise ValueError("\n Пароль должен быть не менее 4-х символов !!!\n")

    #Получаем полное имя файла с данными пользователей
    f_users = get_user_filename()

    # Бывают прикольчики
    if os.path.exists(f_users) and (os.path.getsize(f_users) == 0) :
        os.remove(f_users)

    tst = -1 # начальный user_id
    content = [] #Готовим чистый список

    if os.path.exists(f_users): #если файл есть и он не пустой
        with open(f_users, 'r', encoding='utf-8') as f:
            content = json.load(f) # Читаем и разбираем json формат
        if not isinstance(content, list):
            raise ValueError('Файл данных должен быть в формате JSON')
        #Проверяем имя пользователя
        for d_item in content :
            if d_item["username"] != __username :
                if d_item["user_id"]  > tst :
                    tst = d_item["user_id"] # Ищем "последнее" значение "user_id"
            else : # если пользователь есть - то Ошибка
                raise ValueError(f' Имя занято - {d_item["username"]}!!!\n')

    # Был файл или не был -> продолжаем
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

    # Создать экземпляр класса Portfolio для пользователя
    current_portf = Portfolio( current_user)
    # Добавляем базовый кошелек новому пользователю
    current_portf.add_currency("USD") # а может и не надо

    # Сохраняем портфолио
    current_portf.add_portfolio_to_file()

    #Вроде успех
    print(f'\n {list_dict["username"]} зарегистрирован id({list_dict["user_id"]})\n')

    #Для логирования
    __register( username = list_dict["username"], user_id = list_dict["user_id"])

    #очищаем current_user И current_portf - регистрация - это не логин
    current_user = None
    current_portf = None

    print(f'\nВойдите: login --username {list_dict["username"]} --password ****\n')

    # Конец register

@log_action("LOGIN")
def __login(  username: str, user_id: int) :
    pass


#войти в систему
#@log_action("LOGIN")
def login( __arg_list : dict) :

    """Вход пользователя в систему"""

    global current_user
    global current_portf

    #Проверяем есть ли активный пользователь
    if current_user is not None :
        raise ValueError("\n\n Сначала закройте сессию текущего пользователя\n\n")

    if len(__arg_list) != 2:
        raise ValueError("\n\n !!! Неверные параметры !!!\n\n")

    try:
        __username = __arg_list["username"]
        __password = __arg_list["password"]
    except KeyError :
        raise ValueError("Не верные параметры !!\n")

    if __username is None or __password is None :
        raise ValueError("\n\n !!! Неверные параметры !!!\n\n")

    #Получаем полное имя файла с данными пользователей
    f_users = get_user_filename()

    # Бывают прикольчики
    if (( not os.path.exists(f_users)) or # Файл не найден
            ( os.path.getsize(f_users) and
              (os.path.getsize(f_users) == 0))) : # Файл пустой
        raise ValueError(f'\nПользователь - {__username} - не найден\n')

    #Если мы здесь - то файл есть и он не пустой
    with open(f_users, 'r', encoding='utf-8') as f:
        content = json.load(f) # Читаем и разбираем json формат

    if not isinstance(content, list):
        print("Неверный формат файла с регистрационными данными пользователей !!!")
        return

    #Ищем имя пользователя в списке всех пользователей
    t_user = {}

    for d_item in content :
        if d_item["username"] == __username : # может лучше d_item.get()
            t_user = d_item # Нашли пользователя
            break

    if len(t_user) == 0 :
        raise ValueError(f'\nПользователь - {__username} - не найден\n')

    #Если мы здесь - значит пользователь найден и нужно проверить пароль
   
    #Получаем хеш пароля из логина
    t_pass = User._h_password( __password, t_user["salt"])

    if t_pass != t_user["hashed_password"] :
        raise ValueError('\n\nОшибка - Неверный пароль !!!\n\n')

    #Инициализируем экземпляр класса - и заполняем глобальную переменную
    current_user = User.from_dict( t_user)

    # Создать экземпляр класса Portfolio и дать ему пользователя
    current_portf = Portfolio( current_user)
    current_portf.load_portfolio()

    print('\n\nВы вошли как - ', t_user["username"], '\n\n')

    #Для логирования
    __login( username = t_user["username"], user_id = t_user["user_id"])
    #Конец login


#Для логирования
@log_action("LOGOUT", verbose=True)
def __logout(  username: str, user_id: int) :
    pass

#выйти из системы
def logout() :

    """Выход пользователя из системы"""

    global current_user
    global current_portf

    if current_user is None :
        raise ValueError('\n Нет текущего пользователя \n') # Если не было login

    #Для логирования
    __logout( username = current_user.username, user_id = current_user.user_id)

    # Типа выходим - заполняем глобальные переменные

    # Очищаем профиль текущего пользователя
    current_portf = None

    # Очищаем текущего пользователя
    current_user = None

    print( " Вы вышли из системы\n")

    #Конец logout


# Вывод информации о конкретной валюте
def get_currency_info ( __args : dict) :

    code = __args.get("currency", None)
    if code is None :
        raise ValueError("Ошибка в параметрах !!!")

    #Если такой валюты нет то будет исключение CurrencyNotFound
    currency = get_currency( code)

    print('\n', currency.get_display_info())
