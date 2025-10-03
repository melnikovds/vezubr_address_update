from locust import HttpUser, between, task
from typing import TextIO
from auth import *
from payload_builder import *
import time
import threading
import json
import os

# Настройки
TARGET_TOTAL = 5000       # всего адресов
RATE_PER_SEC = 10          # запросов в секунду
OUTPUT_FILE = "addresses.json"

_created_count = 0
_created_ids = []
_lock = threading.Lock()


class User(HttpUser):
    # задаём базовый URL
    host = "https://api.vezubr.com"
    # интервал между задачами
    wait_time = between(0, 0)

    # авторизация перед началом сессии
    def on_start(self):
        token = AuthHelper.login_as("customer")
        self.client.headers.update({
            "Authorization": token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        print("[locust] авторизация выполнена")

    # задача создания адресов
    @task
    def create_point(self):
        global _created_count, _created_ids

        # проверка достижения лимита
        with _lock:
            if _created_count >= TARGET_TOTAL:
                if not os.path.exists(OUTPUT_FILE):
                    try:
                        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                            json.dump(_created_ids, f, ensure_ascii=False, indent=2)  # type: ignore[arg-type]
                        print(f"[locust] сохранено {_created_count} id в файл {OUTPUT_FILE}")
                    except Exception as e:
                        print(f"[locust] ошибка при сохранении файла: {e}")

                try:
                    if self.environment and getattr(self.environment, "runner", None):
                        print("[locust] останавливаю runner")
                        self.environment.runner.quit()
                except Exception as e:
                    print(f"[locust] не удалось корректно остановить runner: {e}")
                return

            # резервируем место для следующего запроса
            _created_count += 1
            current_idx = _created_count

        # делаем запрос
        payload = PointPayloadBuilder.point_create()
        try:
            resp = self.client.post(
                "/v1/api-ext/contractor-point/update",
                json=payload,
                name="/v1/api-ext/contractor-point/update"
            )
        except Exception as e:
            print(f"[locust] исключение при запросе ({current_idx}): {e}")
            resp = None

        # парсим ответ
        if resp is not None and resp.status_code in (200, 201):
            try:
                j = resp.json()
                new_id = j.get("id") if isinstance(j, dict) else None
                if new_id is None:
                    print(f"[locust] предупреждение: в ответе {current_idx} отсутствует поле 'id'. Ответ: {j}")
                else:
                    with _lock:
                        _created_ids.append(new_id)
            except Exception as e:
                print(f"[locust] не удалось распарсить JSON ({current_idx}): {e}")
        else:
            code = resp.status_code if resp is not None else "нет-ответа"
            print(f"[locust] неуспешный статус ({code}) для запроса #{current_idx}")

        # держим скорость примерно RATE_PER_SEC запросов в секунду
        time.sleep(10.0 / RATE_PER_SEC)



    # задача обновление адресов






