#  Реализация командного интерфейса (CLI)
#Цель раздела
#Сделать консольный интерфейс, через который пользователь сможет:

import json
import os

from valutatrade_hub.core.models import (
    Portfolio,
    User,
    current_portf,
    current_user,
)

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

#Команда get-rate -  из затычки
# Пример
# > get-rate --from USD --to BTC
#    Курс USD→BTC: 0.00001685 (обновлено: 2025-10-09 00:03:22)
#    Обратный курс BTC→USD: 59337.21
# Если курс свежий (например, моложе 5 минут) — показать его.
# Иначе — запросить у Parser Service (или использовать заглушку) → обновить кеш.
# Но пока заглушка

def get_rate( __arg_list : dict) :

    """Назначение: получить текущий курс одной валюты к другой из затычки"""


    print('Команды ', __arg_list)

    __from = __arg_list.get( "from", None) 
    __to = __arg_list.get( "to", None)

    if __from is None or __to is None :
        print('Некорректная команда')
        return

    print('Команды ', __from, __to)


    # Обработка исключений
    try:
        t_rate_dict = Portfolio._get_exchange_rates( __from)
    except ValueError as e:
        print(f"Ошибка : {e}")
        return # Ничего и не далаем

    # Обработка исключений
    try:
        t_curs = t_rate_dict.get( __to, None)
    except ValueError as e:
        print(f"Ошибка : {e}")
        return # Ничего и не далаем

    if t_curs is None :
         print(' Курс не найден\n')
         return

    # Типа дата обновления
    t_date = Portfolio._get_exchange_rates( "last_refresh")

    # Прямой курс    
    print(f' Курс {__from} -> {__to} - {t_curs:12.8f}\n')
    print(f' обновлено : {t_date}\n')

    # ПОбратный курс    
    t_rate_dict = Portfolio._get_exchange_rates( __to)
    t_curs = t_rate_dict.get( __from, None)
    print(f' Обратный курс {__to} -> {__from} : {t_curs:12.8f} \n\n')

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
    finally:
        return # Собственно ничего и не далали

    # Портфолито после покупки
    #current_portf.show_portfolio()

    #Пример команды - buy --currency EUR --amount 150.05
    #Логика - купить валюту EUR на  150.05$

    #Конец Buy


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

    print('Список аргументов __arg_list - ', __arg_list, '\n')

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

    # Сохраняем состояние кошельков
    current_portf.save_portfolio()

    # Очищаем профиль текущего ползователя
    current_portf = None

    # Очищаем текущего ползователя
    current_user = None

    print( " Выход пользователя из системы - logout\n")

    #Конец logout


