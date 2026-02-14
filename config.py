"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ID администратора
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

# ID канала для публикации
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Максимальная длина вопроса
MAX_QUESTION_LENGTH = 1000

# Проверка наличия обязательных параметров
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в .env файле")

if not ADMIN_ID:
    raise ValueError("ADMIN_ID не установлен в .env файле")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID не установлен в .env файле")
