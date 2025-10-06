# locustfile.py
from locust import HttpUser, between, task
from auth import *
from payload_builder import *
import time
import threading
import json
import os

# --- настройки ---
INPUT_FILE = "addresses.json"         # файл со списком id
OUTPUT_FILE = "updated_addresses.json"
RATE_PER_SEC = 2                    # целевая скорость запросов в секунду
# --------------------

_lock = threading.Lock()
_ids = []
_index = 0            # индекс следующего id для обработки
_updated_ids = []     # куда положим успешно обновлённые id
_total = 0


def load_ids():
    global _ids, _total
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Файл с id не найден: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"В файле {INPUT_FILE} ожидается список id, а найдено: {type(data)}")
    # приводим к списку целых и фильтруем неинтовые значения
    cleaned = []
    for item in data:
        try:
            cleaned.append(int(item))
        except Exception:
            # пропускаем некорректные записи
            print(f"[warning] пропускаю некорректный id: {item}")
    _ids = cleaned
    _total = len(_ids)
    print(f"[locust] загружено {_total} id из {INPUT_FILE}")


class User(HttpUser):
    host = "https://api.vezubr.com"
    wait_time = between(0, 0)  # контролим паузы вручную через time.sleep

    def on_start(self):
        token = AuthHelper.login_as("customer")
        self.client.headers.update({
            "Authorization": token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        # загрузим ids при старте первого пользователя
        global _ids
        if not _ids:
            try:
                load_ids()
            except Exception as e:
                print(f"[locust] ошибка при загрузке {INPUT_FILE}: {e}")
                # Если не удалось загрузить — останавливаем runner
                try:
                    if self.environment and getattr(self.environment, "runner", None):
                        self.environment.runner.quit()
                except Exception:
                    pass

        print("[locust] авторизация выполнена, начало обновления адресов")

    @task
    def update_point(self):
        """
        Каждый вызов берёт следующий id из списка и отправляет запрос обновления.
        Когда список кончается — сохраняет результат и останавливает runner.
        """
        global _index, _updated_ids, _ids, _total

        # резервируем следующий id
        with _lock:
            if _index >= _total:
                # всё обработали — сохраняем и останавливаем
                if not os.path.exists(OUTPUT_FILE):
                    try:
                        # сохраняем успешно обновлённые id
                        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                            json.dump(_updated_ids, f, ensure_ascii=False, indent=2)  # type: ignore[arg-type]
                        print(f"[locust] сохранено {len(_updated_ids)} обновлённых id в {OUTPUT_FILE}")
                    except Exception as e:
                        print(f"[locust] ошибка при сохранении {OUTPUT_FILE}: {e}")

                try:
                    if self.environment and getattr(self.environment, "runner", None):
                        print("[locust] все id обработаны — останавливаю runner")
                        self.environment.runner.quit()
                except Exception as e:
                    print(f"[locust] не удалось корректно остановить runner: {e}")
                return

            cur_id = _ids[_index]
            _index += 1
            cur_num = _index  # 1-based номер текущего

        try:
            payload = PointPayloadBuilder.point_update()
            if isinstance(payload, dict):
                payload["id"] = cur_id
            else:
                try:
                    setattr(payload, "id", cur_id)
                except Exception:
                    # на случай необычной реализации — логируем и продолжаем
                    print(f"[locust] не удалось установить id в payload (id={cur_id}), payload type={type(payload)}")
        except Exception as e:
            print(f"[locust] исключение при построении payload для id={cur_id}: {e}")
            # чтобы не терять ход, просто ждём и возвращаемся
            time.sleep(1.0 / RATE_PER_SEC)
            return

        # посылаем запрос
        try:
            resp = self.client.post("/v1/api-ext/contractor-point/update", json=payload,
                                    name="/v1/api-ext/contractor-point/update")
        except Exception as e:
            print(f"[locust] исключение при запросе id={cur_id} (номер {cur_num}): {e}")
            resp = None

        if resp is not None and resp.status_code in (200, 201):
            # считаем успешным
            with _lock:
                _updated_ids.append(cur_id)
            print(f"[locust] OK {cur_num}/{_total} — id={cur_id} обновлён")
        else:
            code = resp.status_code if resp is not None else "нет-ответа"
            print(f"[locust] FAIL {cur_num}/{_total} — id={cur_id}, статус {code}; ответ: {getattr(resp, 'text', '')[:200]}")

        # пауза между запросами, чтобы держать примерно RATE_PER_SEC req/s
        time.sleep(1.0 / RATE_PER_SEC)
