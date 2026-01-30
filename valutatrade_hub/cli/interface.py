#  Реализация командного интерфейса (CLI)
#Цель раздела
#Сделать консольный интерфейс, через который пользователь сможет:

import shlex

from valutatrade_hub.core.exceptions import (
    CurrencyNotFoundError
)

from valutatrade_hub.core.usecases import (
    buy,
    get_currency_info,
    deposit,
    get_rate,
    login,
    logout,
    register,
    sell,
    show_portfolio,
    show_rates,
    update_rates,
)
from valutatrade_hub.core.utils import (
    get_input,
    show_help,
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



# Словарь команд
COMMANDS = {
    "register": {"username", "password"},
    "login": {"username", "password"},
    "show-portfolio" :{},
    "buy" : {"currency", "amount"},
    "sell" : {"currency", "amount"},
    "get-rate" : {"from", "to"},
    "show-rates" : {"top", "currency", "base"},
    "update-rates" : {"source"}
}

#Глобальная переменная соловарь - хранит информацию о текущем пользователе
#current_user

# Разбираем комадну в словарь
def parse_command(command: str) -> dict:

    #Сначала разделяем 
    parts = shlex.split(command)

   # пусты команды отлавливаем раньше

    result = {
        "command": parts[0],
        "args": {}
    }

    i = 1
    while i < len(parts):
        if parts[i].startswith("--"):
            key = parts[i][2:]
            value = parts[i + 1] if i + 1 < len(parts) else None
            result["args"][key] = value
            i += 2
        else:
            i += 1

    return result


#    На выходе должно быть что-то типа такого
#    {
#     'command': 'register',
#     'args': {
#              'username': 'alice',
#              'password': '1234'
#             }
#    }

    # Конец parse_command


#Функция обработки команд
def process_command( command):
    
    """ Функция выполнения команды - изменение game_state """

    command.lower() # Приводим строку к нижнему регистру

    d_command = parse_command( command)

    match d_command["command"] :
        case "register": # Регистрация пользователя
            register( d_command["args"])

        case "login" : # Вход пользователя
            login( d_command["args"])

        case "logout" : # Выход пользователя
            if len(d_command["args"]) > 0 :
                print('\n\nНеверное количество параметров в команде\n\n')
                return
            logout()

        case "buy": # Купить валюту
            buy( d_command["args"])

        case "sell" :  # Продать валюту
            sell( d_command["args"])

        case "show-portfolio" :
            # показать все кошельки и итоговую стоимость в USD
            if len(d_command["args"]) > 0 :
                print('\n\nНеверное количество параметров в команде\n\n')
                return
            show_portfolio()

        case "get-rate" : # получить текущий курс одной валюты к другой
            get_rate( d_command["args"])

        case "get-info" : # получить текущий курс одной валюты к другой
            try:
                get_currency_info( d_command["args"] )
            except ValueError as e:
                print( e)
            except CurrencyNotFoundError as e :
                print( e)

        case  "show-rates":  # показать текущие курсы
            show_rates(d_command["args"])

        case "update-rates" : # обновить курсы
            print('\n\nНемного ждем .... !!!!\n\n')
            update_rates( d_command["args"])

        case "deposit":  # Выход из программы
            deposit( d_command["args"])

        case "quit":  # Выход из программы
            if len(d_command["args"]) > 0 :
                print('\n\nНеверное количество параметров в команде\n\n')
                return
            logout()

        case "help":
            show_help()

        case _:
            print('Команда не опознана\n')
            show_help()

def base_work() -> None:

    action = ""
    # здесь делаем обработку
    while not action == "quit":
        action = get_input('Введите команду - :')  # Запрашиваем команду от пользователя
        process_command(action)  # Вызываем обработчик команд


#try:
#    wallet.withdraw(10)
#except InsufficientFundsError as exc:
#    print(str(exc))
#except CurrencyNotFoundError as exc:
#    print(str(exc))
#except ApiRequestError as exc:
#    print(str(exc))
