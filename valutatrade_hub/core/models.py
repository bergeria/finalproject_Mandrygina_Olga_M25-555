# реализация классов

import hashlib
import json
import os
import random
import string
from datetime import datetime
from typing import Dict

#Глобалная переменная - хранит текущего пользователя
current_user = None

#Глобалная переменная - хранит портфолио текущего пользователя
current_portf = None

# Может и одного current_portf будет достаточно

#класс Wallet
class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        #Простой конструктор
        self.currency_code = currency_code
        self.balance = balance  # через сеттер

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:

        if not isinstance(value, (int, float)):
            raise TypeError("Баланс должен быть числом")

        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")

        self._balance = float(value)

    @property
    def currency_code(self) -> str:
        return self._currency_code

    @currency_code.setter
    def currency_code(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("Код валюты должен быть непустой строкой")

        self._currency_code = value.upper()

    # Увеличиваем сумму
    def deposit(self, amount: float) -> None:
        self._validate_amount(amount)
        self._balance += amount

    # Уменьшаем сумму
    def withdraw(self, amount: float) -> None:
 
        self._validate_amount(amount)

        if amount > self._balance:
            raise ValueError("Недостаточно средств на балансе")

        self._balance -= amount

   # Возвращаем текущий баланс 
    def get_balance_info(self) -> dict :
        return {
            "currency": self._currency_code,
            "balance": self._balance
        }

    @staticmethod
    def _validate_amount(amount: float) -> None:
        if not isinstance(amount, (int, float)):
            raise TypeError("Сумма должна быть числом")

        if amount < 0:
            raise ValueError("Сумма должна быть положительной")

   # По сути тоже что и get_balance_info
    def to_dict(self) -> dict:
        return {
            self._currency_code :  
            {"balance": self._balance}
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Wallet":

        """ Создаёт экземпляр Wallet из словаря """

        if not isinstance(data, dict):
            print("Ожидается словарь\n")
            return

        # образец ожидаемого словаря
        #{"currency_code": "BTC", "balance": 0.05}
        #{"currency_code": "USD", "balance": 1200.0}

        return cls(
            currency_code=data["currency_code"],
            balance=data["currency_code"].get("balance")
        )
    # Конец Wallet


# Логика где-то здесь User -> Portfolio -> Wallet

#Пример использования
#portfolio.get_wallet("USD").deposit(1000)
#print(portfolio.get_total_value("USD"))

# Класс Portfolio - Ключевой
class Portfolio:
    def __init__(self, user : "User"): # user - это : "User"
        self._user = user
        self._user_id = user.user_id
        self._wallets: Dict[str, Wallet] = {}

        # Чтобы лишний раз файлы не перезаписывать
        self._has_changed = False

        # Получаем текущую рабочую директорию.
        c_path = os.getcwd() 

        # Полный путь файла всех портфолио
        self._f_portfolios = os.path.join( c_path, 'data', 'portfolios.json')

        # по умолчанию создаём USD-кошелёк
        #self.add_currency("USD")
        #self.add_currency("BTC")
        # загружаем портфолио пользователя из файла
        self.load_portfolio()


    @property
    def user(self):
        """Возвращает объект пользователя"""
        return self._user

    @property
    def wallets(self) -> dict:
        """Возвращает копию словаря кошельков"""
        return self._wallets.copy()

    def add_currency(self, currency_code: str) -> None:
        currency_code = currency_code.upper()

        if currency_code in self._wallets:
            print(f"Кошелёк {currency_code} уже существует")
            return

        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Wallet:
        currency_code = currency_code.upper()

        if currency_code not in self._wallets:
            raise KeyError(f"Кошелёк {currency_code} не найден")

        return self._wallets[currency_code]

    def get_total_value(self, base_currency: str = "USD") -> float:
        
        """Пересчет общего баланса в разные валюты- по умолчанию USD"""

        #На всякий случай верний регистр
        base_currency = base_currency.upper()

        #Курс целевой валюты
        exchange_rates = self._get_exchange_rates(base_currency)

        total = 0.0
        for code, wallet in self._wallets.items():
            if code not in exchange_rates:
                continue
            total += wallet.balance * exchange_rates[code]

        return round(total, 4)


    def buy_currency(self, currency_code: str, amount_usd: float) -> None:
        
        """Покупка валюты за USD"""

        #На всякий случай верний регистр
        currency_code = currency_code.upper()

        #Это тупизм
        if currency_code == "USD":
            raise ValueError("Нельзя покупать USD за USD")

        #Если такого кошелька еще не было - добавляем
        if currency_code not in self._wallets:
            self.add_currency(currency_code)

        #Добрались до кошельков - вроде до копий
        usd_wallet = self.get_wallet("USD")
        target_wallet = self.get_wallet(currency_code)

        #Берем словарь курсов к USD
        exchange_rates = self._get_exchange_rates("USD")
        print(' Курсы - ',exchange_rates,'\n')

        #Мы в пролете
        if currency_code not in exchange_rates:
            raise ValueError("Нет курса для данной валюты")

        #Берем курс USD к currency_code
        rate = exchange_rates[currency_code]

        #Ищем сколько нужно израсходовать USD
        currency_amount = amount_usd / rate

        #Снимаем деньги с кошелька USD
        usd_wallet.withdraw(amount_usd)

        #Кладем деньги на кошельк currency_code
        target_wallet.deposit(currency_amount)

        # Файл нужно будет перезаписывать
        self._has_changed = True


    def sell_currency(self, currency_code: str, amount: float) -> None:

        """Продажа валюты за USD"""

        #На всякий случай верний регистр
        currency_code = currency_code.upper()

        #Снова тупизм
        if currency_code == "USD":
            raise ValueError("Нельзя продавать USD")

        #Добрались до кошельков - вроде до копий
        wallet = self.get_wallet(currency_code)
        usd_wallet = self.get_wallet("USD")

        #Берем словарь курсов к USD
        exchange_rates = self._get_exchange_rates("USD")

        #И опять в пролете
        if currency_code not in exchange_rates:
            raise ValueError("Нет курса для данной валюты")

        #Берем курс currency_code к USD
        rate = exchange_rates[currency_code]
        usd_amount = amount * rate

        #Снимаем деньги с кошелька currency_code
        wallet.withdraw(amount)

        #Кладем деньги на кошельк USD
        usd_wallet.deposit(usd_amount)

        # Файл нужно будет перезаписывать
        self._has_changed = True

    @staticmethod
    def _get_exchange_rates(base_currency: str) -> dict:
        """
        Фиктивные курсы:
        1 единица валюты = X base_currency
        """
        rates = {
            "USD": {"USD": 1.0, "EUR": 1.1, "BTC": 87866.00, "RUB": 0.01300},
            "EUR": {"EUR": 1.0, "USD": 0.91, "BTC": 79885, "RUB":0.01094},
            "BTC": {"USD": 0.00001138, "EUR": 0.00001252, "BTC": 1.0, "RUB":0.00000015},
            "RUB": {"RUB": 1.0, "USD": 76.91, "EUR": 91.45, "BTC": 6757741.3},
            "source": "ParserService",
            "last_refresh": "2026-01-26T16:35:00"
        }

        if base_currency not in rates:
            raise ValueError("Базовая валюта не поддерживается")

        return rates[base_currency]

    def wallets_to_dict(self) -> dict:
        """
        Возвращает портфель в виде,
        готовом для сохранения в JSON
        """

        data = {}
        data["user_id"] = self._user_id
        data["wallets"] = {}

        # Теперь добавляем в data["wallets"] - кошельки в виде словарей
        for code, itm in self._wallets.items() :
            tmp = self.wallets[code].to_dict()
            data["wallets"][code] = tmp[code]

        return data


    # Добавляем portfolio для нового пользователя
    def add_portfolio_to_file(self) -> None :
        """
           Добавляем portfolio для нового пользователя
        """

        content = [] #Готовим чистый список

        if os.path.exists(self._f_portfolios) and (os.path.getsize(self._f_portfolios) ==0 ): # noqa: E501
            os.remove(self._f_portfolios)

        if os.path.exists(self._f_portfolios): #если файл есть и он не пустой
            with open( self._f_portfolios, 'r', encoding='utf-8') as f:
                content = json.load(f) # Читаем и разбираем json формат

        user_portf = self.wallets_to_dict()

        #print( user_portf)

        #Добавляем Portfolio пользователя в общий список
        content.append(user_portf)

        #print(content)

        # перезаписываем файл если он был, если не был то создаем новый
        with open( self._f_portfolios, 'w', encoding='utf-8') as f:
            json.dump( content, f, indent=4, ensure_ascii=False)

    # Конец add_portfolio_to_file


    # Загружаем портфолио из фала
    # этот метод нужно вызывать в методе __init__
    def load_portfolio(self) -> None :
        """ Загружаем портфолио из фала """       
 
        # Бывают прикольчики
        if not os.path.exists( self._f_portfolios) :
            print("Файл портфолио не найден !!!\n\n")
            return

        if os.path.getsize(self._f_portfolios) == 0 :
            print("Файл портфолио испорчен !!!\n\n")
            return

        content = [] #Готовим чистый список

        # файл есть и он не пустой
        with open( self._f_portfolios, 'r', encoding='utf-8') as f:
            content = json.load(f) # Читаем и разбираем json формат

        #Ищем кошелек текущего пользователя
        t_wallets = None
        for d_item in content :
            if d_item["user_id"] == self._user_id :
                t_wallets = d_item["wallets"] # Нашли кошельки пользователя
                break

        # Типа новый пользователь - добавиляем кошелек новичку
        if t_wallets is None :
            self.add_portfolio_to_file()
            return

        #print(f'Нашли кошельки пользователя - {t_wallets}\n\n')

        # образец ожидаемого словаря для Wallet.from_dict(dict)
        #{"currency_code": "BTC", "balance": 0.05}
        #{"currency_code": "USD", "balance": 1200.0}

        # пока Заполняем данные кошельков вручную
        for t_item in t_wallets :
            #Добавляем кошелек
            self.add_currency(t_item)
            #Вносим сумму валюты в кошелек
            self.get_wallet(t_item).deposit( float(t_wallets[t_item]["balance"]))

       # Отладочная информация
       #print(f' Валюта - t_item = {t_item}\n\n')
       #print(f' Кошелек - t_wallets[t_item] = {t_wallets[t_item]}\n\n')
       #print(f'Сумма t_wallets[t_item]["balance"] = {t_wallets[t_item]["balance"]}\n')


    # Конец load_portfolio

    # Показываем портфолио текущего ползователя
    # посмотреть свой портфель и балансы (show-portfolio);
    def show_portfolio(self) -> None :

        """ Показываем портфолио текущего пользователя - оно уже в памяти """

        print("\n Портфель пользователя ", self.user.username, ":\n" ) #(база: USD)

        # берем курсы к USD - пока из затычки
        t_rate = self._get_exchange_rates("USD")

        # идем по кошелькам
        for item in self._wallets :
            t_wal = self.get_wallet(item).get_balance_info()
            t_calc = t_wal["balance"] * t_rate[item]
            print(f' - {item} :  {t_wal["balance"]:10.4f} -> {t_calc:10.4f}\n')

        print(' -----------------------------------------------')
        print(f' ИТОГО :  {self.get_total_value("USD"):10.4f}  USD')

    # Конец show_portfolio

    def save_portfolio( self) -> None :

        """Схраняем текущее состояние портфолио пользователя"""

        # Если False - не торговали
        if not self._has_changed :
            print(' Кошельки без изменений\n')
            return

        # Бывают прикольчики
        if not os.path.exists( self._f_portfolios) :
            print("Файл портфолио не найден - создаем новый !!!\n\n")
            self.add_portfolio_to_file()
            return

        if os.path.getsize(self._f_portfolios) == 0 :
            print("Файл портфолио испорчен - создаем новый  !!!\n\n")
            self.add_portfolio_to_file()
            return

        content = [] #Готовим чистый список

        # файл есть и он не пустой
        with open( self._f_portfolios, 'r', encoding='utf-8') as f:
            content = json.load(f) # Читаем и разбираем json формат

        #Берем текущее состояние кошельков в нужном нам формате
        user_portf = self.wallets_to_dict()

        #Ищем кошелек текущего пользователя в данных из файла
        for d_item in content :
            if d_item["user_id"] == self._user_id :
                d_item["wallets"] = user_portf["wallets"] # Нашли кошельки пользователя
                break

        # И перезаписываем файл если он был
        with open( self._f_portfolios, 'w', encoding='utf-8') as f:
            json.dump( content, f, indent=4, ensure_ascii=False)

        #Конец save_portfolio

    # Конец портфолио


# класс User пользователь системы
# По идее класс должен управлять хранением в файле users.json
# Например через @staticmethod'ы 
# А может и не должен
class User:
    def __init__(
                 self, 
                 user_id : int,
                 username : str,
                 *,
                 password : str | None = None,
                 salt : str | None = None,
                 hashed_password : str | None = None,
                 registration_date : datetime | None = None
                ) :

        self._user_id = user_id # уникальный идентификатор пользователя - int
        self._username = username # имя пользователя - str
        self._registration_date = registration_date or datetime.now().strftime("%Y-%m-%dT%H:%M") # noqa: E501

        # если параметры есть
        if salt and hashed_password:
            # значения из словаря или хранилища
            self._salt = salt
            self._hashed_password = hashed_password
        elif password is not None: # если есть пароль
            self._salt = self._get_salt() # соль пользователя - str
            self._hashed_password = self._h_password( password, self._salt) #Хеш
        else:
            raise ValueError(
                "А вот этой ситуации быть не должно - типа чего-то не хватает"
            )


    @staticmethod # может и зря staticmetod
    def _get_salt() -> str:
        """ Генерим уникальную соль для пользователя """
        characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
        slt = ''.join(random.choice(characters) for _ in range(10))
        return slt

    @staticmethod # может и зря staticmetod
    def _h_password( __pass : str, _slt : str) -> str:
        """ Генерим hash password — для пользователя """
        sum_str = __pass + _slt
        return hashlib.sha256( sum_str.encode()).hexdigest()

    @property # возвращаем user_id
    def user_id(self) -> int:
        return self._user_id

    @property # возвращаем user_name
    def username(self) -> str:
        return self._username

    @property # возвращаем registration_date
    def registration_date(self) -> datetime:
        return self._registration_date

    # возвращает информацию о пользователе (без пароля).
    def get_user_info( self) -> dict :
        u_dict = {}
        u_dict["user_id"] = self._user_id
        u_dict["username"] = self._username
        u_dict["registration_date"] = self._registration_date
        return u_dict
   
    # изменяет пароль пользователя, с хешированием нового пароля.
    def change_password( self, new_password: str) -> None :
        # Создаем Хеш для нового пароля
        self._hashed_password = self._h_password( new_password, self._salt)
        #теперь нужно изменить пароль в файле users.json - будет попозже

    # проверяет введённый пароль на совпадение - пока не поняла как испоользовать
    def verify_password( self, password: str) -> bool :
        t_pass = self._hash_password(password, self._salt)
        return t_pass == self._hashed_password

    # возвращает словарь данных пользователя
    def to_dict(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password" : self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date
        }

    @classmethod # Создаем экземпляр класса из словаря
    def from_dict(cls, data: dict) -> "User" :
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            salt=data["salt"],
            hashed_password=data["hashed_password"],
            registration_date=data["registration_date"],
        )

#Как временное решение
#Кодыв валют в списке

LIST_VAL = ['ZWL',
            'ZMW',
            'ZAR',
            'YER',
            'VND',
            'VEF',
            'UZS',
            'UYU',
            'UYI',
            'USD',
            'UGX',
            'UAH',
            'TZS',
            'TWD',
            'TTD',
            'TRY',
            'TOP',
            'TND',
            'TMT',
            'TJS',
            'THB',
            'SZL',
            'SYP',
            'SVC',
            'STD',
            'SSP',
            'SRD',
            'SOS',
            'SLL',
            'SGD',
            'SEK',
            'SAR',
            'RWF',
            'RUB',
            'RSD',
            'RON',
            'QAR',
            'PLN',
            'PKR',
            'PHP',
            'PGK',
            'PEN',
            'PAB',
            'OMR',
            'NZD',
            'NOK',
            'MYR',
            'MDL',
            'KZT',
            'KRW',
            'KGS',
            'JPY',
            'ILS',
            'EUR',
            'EGP',
            'CZK',
            'CNY',
            'CHF',
            'BRL',
            'AZN',
            'AWG',
            'AUD',
            'ARS',
            'AMD',
            'ALL',
            'AFN',
            'AED',
            'BTC']	
