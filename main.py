import shlex

from valutatrade_hub.cli.interface import (
    buy,
    get_rate,
    login,
    logout,
    register,
    sell,
    show_portfolio,
)
from valutatrade_hub.core.utils import clear_screen, get_input, show_help

# Словарь команд
COMMANDS = {
    "register": {"username", "password"},
    "login": {"username", "password"},
    "show-portfolio" :{},
    "buy" : {"currency", "amount"},
    "sell" : {"currency", "amount"},
    "get-rate" : {"from", "to"},
    "balance": set(),
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

        case "get-rate": # получить текущий курс одной валюты к другой
            get_rate( d_command["args"])

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


# По идее системы должна быть многопользовательская
# Поэтому к файлам данных обращаемся только по необходимости

def main():

    # Торговля валютами
    print('Программа торговли валютами')
   
    clear_screen()

    print("Добро пожаловать в систему Торговли валютами!  \n")
    
    show_help() # выводим список команд перед началом игры

    action = ""

    #основной цикл игры
    while not action == "quit" :
        action = get_input('Введите команду - :') # Запрашиваем команду от пользователя
        process_command( action) # Вызываем обработчик логики игры
    

if __name__ == "__main__":
    main() # Вызов основной функции
