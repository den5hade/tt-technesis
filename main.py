import os
import sqlite3
from dotenv import load_dotenv
import pandas as pd
import telebot
from telebot import types

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('sites.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        xpath TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("Загрузить файл")
    markup.add(btn)
    bot.send_message(message.chat.id, "Привет! Я бот для добавления сайтов для парсинга зюзюбликов. Нажми кнопку 'Загрузить файл', чтобы добавить новые сайты.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Загрузить файл")
def request_file(message):
    msg = bot.send_message(message.chat.id, "Пожалуйста, загрузите Excel-файл с данными о сайтах (поля: title, url, xpath).")
    bot.register_next_step_handler(msg, process_file)

def process_file(message):
    try:
        if message.document is None:
            bot.send_message(message.chat.id, "Пожалуйста, загрузите файл.")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_path = f"uploads/{message.document.file_name}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Чтение Excel файла
        df = pd.read_excel(file_path)
        print(df)
        # Проверка наличия необходимых колонок
        required_columns = ['title', 'url', 'xpath']
        if not all(col in df.columns for col in required_columns):
            bot.send_message(message.chat.id, "Файл должен содержать колонки: title, url, xpath")
            return
        
        # Сохранение в базу данных
        conn = sqlite3.connect('sites.db')
        df.to_sql('sites', conn, if_exists='append', index=False)
        conn.close()
        
        # Отправка содержимого пользователю
        bot.send_message(message.chat.id, f"Данные успешно сохранены. Вот содержимое файла:\n\n{df.to_string(index=False)}")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

@bot.message_handler(commands=['average'])
def get_average_prices(message):
    try:
        # Здесь должна быть логика парсинга и расчета средней цены
        # Это примерная реализация
        conn = sqlite3.connect('sites.db')
        sites = pd.read_sql('SELECT * FROM sites', conn)
        conn.close()
        
        # Примерные данные (реальный парсинг нужно реализовать)
        results = []
        for _, row in sites.iterrows():
            # В реальности здесь должен быть код парсинга сайта
            # Для примера используем случайные цены
            import random
            avg_price = random.randint(500, 1000)
            results.append(f"{row['title']}: {avg_price} руб.")
        
        bot.send_message(message.chat.id, "Средние цены зюзюбликов (Samsung Galaxy S23):\n\n" + "\n".join(results))
    
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при расчете средних цен: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()