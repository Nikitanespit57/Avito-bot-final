import time
from datetime import datetime
import pytz
import requests
import os

CLIENT_ID = os.getenv("AVITO_CLIENT_ID")
CLIENT_SECRET = os.getenv("AVITO_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("AVITO_REFRESH_TOKEN")

def get_access_token():
    try:
        response = requests.post(
            "https://api.avito.ru/token",
            data={
                "grant_type": "refresh_token",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": REFRESH_TOKEN
            }
        )
        if response.ok:
            token = response.json().get("access_token")
            print(f"Получен access_token: {token}")  # Выводим токен в консоль
            return token
        else:
            print("Ошибка получения access_token:", response.text)
            return None
    except Exception as e:
        print(f"Ошибка при запросе токена: {e}")
        return None

def is_after_7pm_moscow():
    moscow_tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(moscow_tz)
    return now.hour >= 19 or now.hour < 11

def check_and_respond():
    while True:
        if is_after_7pm_moscow():
            print("Работаем после 19:00 — отправляем автоответы...")
            token = get_access_token()
            if not token:
                print("Не удалось получить токен, повторная попытка через 5 минут.")
                time.sleep(300)  # Ждем 5 минут перед повторной попыткой
                continue

            headers = {"Authorization": f"Bearer {token}"}
            try:
                response = requests.get("https://api.avito.ru/messenger/v1/messages", headers=headers)
                if response.ok:
                    messages = response.json().get("messages", [])
                    print(f"Получены сообщения: {messages}")  # Отладочная информация

                    for message in messages:
                        if not message.get("is_read"):
                            reply_data = {
                                "message": (
                                    "Приветствуем Вас! В данный момент магазин закрыт. "
                                    "В рабочее время с Вами свяжется наш менеджер и ответит на Ваши вопросы.\n"
                                    "График магазина: с 11:00 до 19:00.\n"
                                    "Благодарим за понимание!"
                                )
                            }
                            reply_response = requests.post(
                                f"https://api.avito.ru/messenger/v1/messages/{message['id']}/reply",
                                headers=headers, json=reply_data
                            )
                            print(f"Ответ отправлен, статус: {reply_response.status_code}")  # Статус отправки
                            print(f"Ответ от API: {reply_response.text}")  # Ответ API
                else:
                    print(f"Ошибка получения сообщений: {response.status_code}")
            except Exception as e:
                print(f"Ошибка при запросе сообщений: {e}")
        else:
            print("Сейчас рабочее время. Бот спит.")

        time.sleep(60)

if __name__ == "__main__":
    check_and_respond()