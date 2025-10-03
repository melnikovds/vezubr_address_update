import requests

class AuthHelper:
    BASE_URL = "https://api.vezubr.com"
    LOGIN_ENDPOINT = "/v1/api-ext/user/login"

    USERS = {
        "api_customer": {
            "username": "florenzateal@powerscrews.com",
            "password": "1n-T2v4T"
        },
        "default_customer": {
            "username": "coppernaval@somoj.com",
            "password": "/4lken&_K`"
        }
    }

    @classmethod
    def login_as(cls, role: str) -> str:
        """
        авторизуется под заданной ролью и возвращает строку с токеном.
        """
        if role not in cls.USERS:
            raise ValueError(f"Неизвестная роль: {role}")

        credentials = cls.USERS[role]
        url = cls.BASE_URL + cls.LOGIN_ENDPOINT
        response = requests.post(url, json=credentials)

        if response.status_code != 200:
            raise Exception(f"Ошибка авторизации для роли '{role}': {response.status_code} - {response.text}")

        token = response.json().get("token")
        if not token:
            raise Exception(f"Не удалось получить токен для роли '{role}'")

        return token