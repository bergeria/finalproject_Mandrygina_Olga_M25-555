# finalproject\_Mandrygina\_Olga\_M25-555



Платформа для отслеживания и симуляции торговли валютами





 Платформа - которая позволяет пользователям регистрироваться,

управлять своим ВИРТУАЛЬНЫМ портфелем фиатных и крипто валют, совершать сделки

по покупке/продаже, а также отслеживать актуальные курсы в реальном времени.





Реализован весь функционал первой части задания

Доработан механизм обработки ошибок

Доработан механизм обновления валют из внешних источников

Планируется добавить механизм планировщика обновления валют



Для запуска достаточно выполнить команду





python3 main.py



или



python main.py -



Доступные команды



register       : зарегистрироваться - Пример register --username alice --password 1234

login"         : войти в систему - Пример login --username alice --password 1234

show-portfolio : посмотреть свой портфель и балансы

buy            : купить - Пример buy --currency BTC --amount 0.05

sell           : продать - Пример sell --currency EUR --amount 100

get-rate       : получить курс - Пример get-rate --from USD --to BTC

get-info       : Информация о валюте - get-info --currency BTC

show-rates     : Все имеющиеся курсы

update-rates   : обновить курсы - Пример --source coingecko | exchangerate - По умолчанию — оба источника

deposit        : Внести на баланс deposit --currency EUR --amount 100

logout         : Выйти из системы

quit           : Выйти из программы

help           : Показать это сообщение







register зарегистрироваться ();



Пример - register --username alice --password 1234



login войти в систему ();



Пример - Login --username alice --password 1234



show-portfolio - посмотреть свой портфель и балансы;



buy купить валюту;



Пример - buy --currency EUR --amount 100



sell продать валюту ();



Пример - sell --currency EUR --amount 100



get-rate - получить курс валюты.



Пример - get-rate --from USD --to BTC



get-info - информация о валюте



Пример - get-info --currency BTC



show-rates - Все имеющиеся курсы - команда без параметров



update-rates -обновить курсы



Пример --source coingecko | exchangerate - Если без параметров то из обоих источников



deposit - Внести средства на баланс



Пример -  deposit --currency EUR --amount 100



logout - выход пользователя



quit - выход из программы







Пока без asciinema



