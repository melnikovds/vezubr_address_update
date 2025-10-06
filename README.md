# VezubrUpdateAddresses

### Проверка массового обновления адресов


**Состав**

- сценарий создания 5 тысяч Адресов

- сценарий получения айдишников 5 тысяч адресов

- сценарий обновления 5 тысяч адресов


ежедневный лимит запросов в dadata 10к


**Установка зависимостей**

   pip install -r requirements.txt


**Запуск**

locust -f locustfile.py --host https://api.vezubr.com

либо в режиме headless с дополнительными настройками

locust -f locustfile.py --headless -u 1 -r 1
