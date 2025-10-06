import requests
import time
import json
from typing import List

API_URL = "https://api.vezubr.com/v1/api/contractor-point/list-info"
OUTPUT_FILE = "addresses.json"

def collect_addresses_ids(
    token: str,
    page_start: int = 1,
    page_end: int = 10,
    items_per_page: int = 500,
    date_from: str = "2025-09-25",
    date_till: str = "2025-10-02"
) -> List[int]:
    """
    Собирает id адресов из ответов
    """
    if not token.strip().lower().startswith("bearer "):
        token = "Bearer " + token.strip()

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://client.vezubr.com",
    }

    session = requests.Session()
    session.headers.update(headers)

    found_ids = []
    for page in range(page_start, page_end + 1):
        payload = {
            "itemsPerPage": items_per_page,
            "toStartAtDateFrom": date_from,
            "toStartAtDateTill": date_till,
            "page": page
        }

        try:
            resp = session.post(API_URL, json=payload, timeout=30)
        except Exception as e:
            print(f"[Ошибка] исключение при запросе page={page}: {e}")
            # ждём и идём дальше
            time.sleep(5)
            continue

        if resp.status_code != 200:
            print(f"[Ошибка] статус {resp.status_code} для page={page}, тело ответа: {resp.text[:500]}")
            time.sleep(5)
            continue

        try:
            j = resp.json()
        except Exception as e:
            print(f"[Ошибка] не удалось распарсить JSON для page={page}: {e}")
            time.sleep(5)
            continue

        points = j.get("points")
        if not isinstance(points, list):
            print(f"[Предупреждение] в ответе page={page} нет списка 'points' или он не список. Ответ: {j}")
            time.sleep(5)
            continue

        count_before = len(found_ids)
        for p in points:
            if isinstance(p, dict) and "id" in p:
                found_ids.append(p["id"])

        print(f"[OK] page={page}: найдено {len(points)} точек, всего ids собралось {len(found_ids)} (добавлено {len(found_ids)-count_before})")

        time.sleep(5)

    unique_ids = list(dict.fromkeys(found_ids))  # сохраняет порядок и убирает дубликаты
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(unique_ids, f, ensure_ascii=False, indent=2)  # type: ignore[arg-type]
        print(f"[Готово] сохранено {len(unique_ids)} уникальных id в файл ./{OUTPUT_FILE}")
    except Exception as e:
        print(f"[Ошибка] не удалось сохранить файл {OUTPUT_FILE}: {e}")

    return unique_ids


if __name__ == "__main__":

    # токен нужно взять от пользователя "default_customer"
    TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3NTk3MzkxMTEsImV4cCI6MTc2MzMzOTExMSwidXNlcm5hbWUiOiJmNzdiOTE2Zjc0ZmZiMjdjYTI5NzQyZjcwNDg0NzNkZGRhOTEzNjZhZWJiNDFiOTViODZiYTZhMjA3MzdlOGMzIiwiY29udHJhY3RvcklkIjozNDg1LCJjb250cmFjdG9yS2V5IjoiMzhkYTE3NTIiLCJpZCI6MTE0MzAsInVzZXJJZCI6MTE4MDMsInVzZXJLZXkiOiJlYzBiNTUyMiIsImNlbnRyaWZ1Z29Ub2tlbiI6ImV5SjBlWEFpT2lKS1YxUWlMQ0poYkdjaU9pSklVekkxTmlKOS5leUp6ZFdJaU9pSXhNVFF6TUNJc0ltVjRjQ0k2TVRjMU9UZ3lOVFV4TVN3aWFXNW1ieUk2ZXlKMWMyVnlibUZ0WlNJNmJuVnNiSDE5LlRMRkJFbm5CODQtblpwaHFCWmJCVFVSUzdGWlhLQUwxWnFmT0ZoUmV3RFEiLCJoZWxwRGVza0VkZHlUb2tlbiI6ImV5SjBlWEFpT2lKS1YxUWlMQ0poYkdjaU9pSklVekkxTmlKOS5leUpwWVhRaU9qRTNOVGszTXpreE1URXNJbXAwYVNJNklqTXhaVGRrWm1FMUxUSTRZVFl0TkdKaE9DMWlaRGRoTFRVM1pEQXlORFE1WkdFMlpDSXNJbVZ0WVdsc0lqb2lZMjl3Y0dWeWJtRjJZV3hBYzI5dGIyb3VZMjl0SWl3aWJtRnRaU0k2SW14dllXUkFURXRhTG1OdmJTQnNiMkZrUUV4TFdpNWpiMjBpTENKdmNtZGhibWw2WVhScGIyNGlPaUpzYjJGa1FFeExXaTVqYjIwaUxDSndhRzl1WlNJNmJuVnNiSDAubmtmS0NVZ0hDQUlXTHZXOHlKSU9kb0VxU2xrQXpiSmVVeVBpem5wa2xDZyIsImVtcGxveWVlUm9sZXMiOlsxMywxXX0.t4KlIp_9KMt_nBDcC58xG7bUcHMDDlyL27ppv60ZeBnusTz-jWml66AJJY1zrFcRGXCdiNic5gxhpbKf31nHkkU3HRNrvtk5mgeil1817rudnLOPsQ0J2T4b8HWY8XabyAV4Wae9DP4pkLBbE8KQu7uLAk2J_d5ZmuqLmVZwiEl5hHGVQpj38M01IpIjfyjj36DEHYNMAHjeEQmrX_FSYZwOWjfSnP9f9brO6gd-4iq50H88mMqs06sTsFI8RTbXpFw9UmL-IGOpRr4Zw2IAcv8osIw1uf0eLn6yH0IV7V0bJPJVcy4yYEM5tVJXG0CMqw3biegKzd99fdQMJhJ2vPHJVrW2-JMWLcEbmO9i10DRYCl4MxlxyUjy3u9ohu7LRscd6HTNi8oDAEnJ02itRZoMF2vokYEQmgC0fIObdQelkI78qszR__Z9nITM1jhaygRdr1JAc_Yl1D2t69LehTE2f2XEEZX-uDsmrcE5V2K99vidIgmjtsm4s77iCtXQqAB8YEEbLb3FKg0OSViiFmio0SADOmtbhYNJdJ05NUVGlWol5IBlK58cVbLyF_8XHE9KmXYjwqic-1czNiBebhXXMjM5liAPU3lbjquHb7yXzBnoVHpie5YrF3hvUEYyvFzFASI9BBo1YYgC5vMELtUDIYatvJNI3ge4BS6Tpz4"  # можно передать как с "Bearer " так и без
    ids = collect_addresses_ids(TOKEN)
