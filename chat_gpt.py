import openai
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Загрузка переменных окружения из файла .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID")

# Настройка учетных данных для Google Cloud
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Функции для работы с базой данных
def create_session():
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (start_time) VALUES (?)", (datetime.now(),))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id

def end_session(session_id):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET end_time = ? WHERE session_id = ?", (datetime.now(), session_id))
    conn.commit()
    conn.close()

def add_message(session_id, role, content, is_important=False):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (timestamp, role, content, session_id, is_important) VALUES (?, ?, ?, ?, ?)",
                   (datetime.now(), role, content, session_id, is_important))
    conn.commit()
    message_id = cursor.lastrowid
    cursor.execute("INSERT INTO context (message_id) VALUES (?)", (message_id,))
    cursor.execute("SELECT COUNT(*) FROM context")
    count = cursor.fetchone()[0]
    if count > 100:
        cursor.execute("DELETE FROM context WHERE context_id = (SELECT MIN(context_id) FROM context)")
    conn.commit()
    conn.close()
    return message_id

def add_event(session_id, event_type, description):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (timestamp, event_type, description, session_id) VALUES (?, ?, ?, ?)",
                   (datetime.now(), event_type, description, session_id))
    conn.commit()
    conn.close()

def determine_importance(message):
    # Пример определения важности на основе ключевых слов
    important_keywords = ['важно', 'заметка', 'внимание', 'запомнить']
    for keyword in important_keywords:
        if keyword in message.lower():
            return True
    return False

def get_recent_history(chat_history, n=50):
    return chat_history[-n:]

def chat_with_gpt(prompt, chat_history, session_id):
    chat_history.append({"role": "user", "content": prompt})

    # Ограничение контекста до N последних сообщений
    recent_history = get_recent_history(chat_history, n=50)

    # Запрос к модели
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=recent_history,
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Получение ответа модели
    message = response.choices[0].message['content'].strip()

    # Проверка на важность сообщения
    is_important = determine_importance(prompt)

    if is_important:
        add_event(session_id, "important", prompt)

    # Добавляем ответ модели в историю
    chat_history.append({"role": "assistant", "content": message})

    return message, is_important

def load_chat_history():
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM messages ORDER BY timestamp")
    messages = cursor.fetchall()
    chat_history = [{"role": role, "content": content} for role, content in messages]
    conn.close()
    return chat_history

def get_important_events():
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT event_id, timestamp, description FROM events WHERE event_type = 'important' ORDER BY timestamp")
    events = cursor.fetchall()
    conn.close()
    return events

def delete_event(event_id):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
    conn.commit()
    conn.close()

def needs_internet_search(message):
    return any(keyword in message.lower() for keyword in ["найти", "поиск", "интернет", "информация", "сколько времени", "новости", "погода"])

def fetch_data_from_internet(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": google_cse_id,
        "key": google_api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("items", [])
        return "\n".join([item["snippet"] for item in results])
    else:
        return f"Ошибка при выполнении запроса: {response.status_code} - {response.text}"

def fetch_news(query):
    url = "https://newsapi.org/v2/everything"
    params = {
        "apiKey": news_api_key,
        "q": query
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("articles", [])
        return "\n".join([f"{article['title']}: {article['description']}" for article in results[:5]])
    else:
        return f"Ошибка при выполнении запроса к новостному API: {response.status_code} - {response.text}"

def fetch_weather(location):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "appid": weather_api_key,
        "q": location,
        "units": "metric",
        "lang": "ru"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return f"Погода в {location}: {data['main']['temp']}°C, {data['weather'][0]['description']}"
    elif response.status_code == 404:
        return "Город не найден. Пожалуйста, проверьте правильность написания."
    else:
        return f"Ошибка при выполнении запроса к погодному API: {response.status_code} - {response.text}"

def process_message_with_model(session_id, chat_history, user_message):
    if needs_internet_search(user_message):
        if "новости" in user_message.lower():
            result = fetch_news(user_message)
            return f"News: {result}", False
        elif "погода" in user_message.lower():
            location = user_message.split("погода")[-1].strip()
            result = fetch_weather(location)
            return f"Weather: {result}", False
        else:
            result = fetch_data_from_internet(user_message)
            return f"Internet: {result}", False

    # Запрос к модели для всех остальных случаев
    chat_history.append({"role": "user", "content": user_message})
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=chat_history,
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    model_response = response.choices[0].message['content'].strip()
    is_important = determine_importance(user_message)

    if is_important:
        add_event(session_id, "important", user_message)

    add_message(session_id, "user", user_message)
    add_message(session_id, "assistant", model_response, is_important)

    return model_response, is_important
