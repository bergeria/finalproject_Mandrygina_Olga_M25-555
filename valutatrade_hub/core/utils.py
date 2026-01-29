# вспомогательные функци
import os

# COMMANDS - Help
COMMANDS = {
  "register" : "зарегистрироваться - register --username alice --password 1234",
  "login" : "войти в систему - Пример login --username alice --password 1234",
  "show-portfolio" : "посмотреть свой портфель и балансы ",
  "get-info" : " Информация о валюте - get-info --currency BTC",
  "buy" : "купить - Пример buy --currency BTC --amount 0.05",
  "sell" : "продать - Пример sell --currency EUR --amount 100",
  "get-rate" : "получить курс - Пример get-rate --from USD --to BTC",
  "show-rates" : "Все курсы | --top 2 | --currency RUB",
  "update-rates" : "обновить курсы --source coingecko | exchangerate - По умолчанию — оба источника", # noqa: E501
  "deposit" : "Внести на баланс (для тестов) - deposit --currency EUR --amount 100 ",
  "logout" : "выйти из системы",
  "quit" : "выйти из программы",
  "help" : "показать это сообщение\n\n",
}


# Функция show_help
def show_help():

    print("\nДоступные команды:\n\n")

    for key, value in COMMANDS.items():
        print(f"{key:<16}  {value}")


#очистка экрана
def clear_screen():
    # Проверяем операционную систему
    # 'nt' для Windows, иначе для Linux/macOS
    os.system('cls' if os.name == 'nt' else 'clear')



#Функция get_input
def get_input(prompt="> "):

    """ Функция принимает от пользователя ввод запрошенной информации"""

    act = ''

    try:
        while len(act) == 0 :
            #сообщаем пользователю что мы от него ждем
            print('\n Ответ не может быть пустым -- \n\n\n', prompt, '\n')
            act = input()
        return act
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из программы.")
        return 'quit'

