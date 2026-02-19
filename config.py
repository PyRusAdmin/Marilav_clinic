"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Получаем строку и превращаем в список int
ADMIN_IDS = [
    int(admin_id.strip())
    for admin_id in os.getenv("ADMIN_IDS", "").split(",")
    if admin_id.strip()
]

# ID администратора
# ADMIN_IDS = int(os.getenv('ADMIN_ID', 0))

# ID канала для публикации
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Максимальная длина вопроса
MAX_QUESTION_LENGTH = 1000

# Проверка наличия обязательных параметров
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в .env файле")

if not ADMIN_IDS:
    raise ValueError("ADMIN_ID не установлен в .env файле")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID не установлен в .env файле")
