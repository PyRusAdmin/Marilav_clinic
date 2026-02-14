#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы бота
"""
import asyncio
import sys
from dotenv import load_dotenv

# Загрузка конфигурации
load_dotenv()

# Цветной вывод
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title):
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    print(f"{RED}❌ {message}{RESET}")


def print_info(message):
    print(f"{YELLOW}ℹ️  {message}{RESET}")


async def test_bot_connection():
    """Проверка подключения к Telegram"""
    try:
        from aiogram import Bot
        from config import BOT_TOKEN
        
        bot = Bot(token=BOT_TOKEN)
        
        me = await bot.get_me()
        print_success(f"Подключение к боту успешно")
        print_info(f"Имя бота: @{me.username}")
        print_info(f"ID: {me.id}")
        print_info(f"Имя: {me.first_name}")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print_error(f"Ошибка подключения к боту: {e}")
        return False


async def test_channel_access():
    """Проверка доступа к каналу"""
    try:
        from aiogram import Bot
        from config import BOT_TOKEN, CHANNEL_ID
        
        bot = Bot(token=BOT_TOKEN)
        
        # Попытка получить информацию о канале
        chat = await bot.get_chat(CHANNEL_ID)
        print_success(f"Доступ к каналу получен")
        print_info(f"Название: {chat.title}")
        print_info(f"ID: {chat.id}")
        
        # Проверка прав администратора
        try:
            bot_member = await bot.get_chat_member(CHANNEL_ID, (await bot.get_me()).id)
            if bot_member.status in ['administrator', 'creator']:
                print_success(f"Бот является администратором канала")
                print_info(f"Статус: {bot_member.status}")
                
                # Проверка прав на публикацию
                if bot_member.can_post_messages:
                    print_success("Бот может публиковать сообщения")
                else:
                    print_error("Бот НЕ может публиковать сообщения!")
                    print_info("Дайте боту права на публикацию в настройках канала")
            else:
                print_error(f"Бот НЕ является администратором! Статус: {bot_member.status}")
                print_info("Добавьте бота в канал как администратора")
        except Exception as e:
            print_error(f"Не удалось проверить права бота: {e}")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print_error(f"Ошибка доступа к каналу: {e}")
        print_info("Проверьте, что CHANNEL_ID указан правильно")
        print_info("Для публичных каналов: @channel_name")
        print_info("Для приватных каналов: числовой ID (например: -1001234567890)")
        return False


def test_database():
    """Проверка работы с базой данных"""
    try:
        from models import init_db, Question, db
        
        # Инициализация БД
        init_db()
        print_success("База данных инициализирована")
        
        # Проверка подключения
        if db.is_closed():
            db.connect()
        
        # Проверка таблиц
        tables = db.get_tables()
        if 'questions' in tables:
            print_success("Таблица 'questions' создана")
        else:
            print_error("Таблица 'questions' не найдена")
            return False
        
        # Проверка записи
        test_id = "test-12345"
        
        # Удаление тестовой записи, если существует
        Question.delete().where(Question.id == test_id).execute()
        
        # Создание тестовой записи
        Question.create(
            id=test_id,
            text="Тестовый вопрос",
            status="pending"
        )
        print_success("Тестовая запись создана")
        
        # Чтение записи
        test_q = Question.get_or_none(Question.id == test_id)
        if test_q and test_q.text == "Тестовый вопрос":
            print_success("Чтение из БД работает")
        else:
            print_error("Ошибка чтения из БД")
            return False
        
        # Обновление записи
        Question.update(status='approved').where(Question.id == test_id).execute()
        test_q = Question.get_or_none(Question.id == test_id)
        if test_q.status == 'approved':
            print_success("Обновление записей работает")
        else:
            print_error("Ошибка обновления записей")
            return False
        
        # Удаление тестовой записи
        Question.delete().where(Question.id == test_id).execute()
        print_success("Тестовая запись удалена")
        
        # Получение статистики
        count = Question.select().count()
        print_info(f"Всего вопросов в БД: {count}")
        
        db.close()
        return True
        
    except Exception as e:
        print_error(f"Ошибка работы с БД: {e}")
        return False


def test_utils():
    """Проверка утилит"""
    try:
        from utils import escape_markdown, validate_question_text, generate_question_id
        
        # Тест escape_markdown
        test_text = "Тест_с*спец[символами]"
        escaped = escape_markdown(test_text)
        if "\\" in escaped:
            print_success("Экранирование MarkdownV2 работает")
        else:
            print_error("Экранирование MarkdownV2 не работает")
            return False
        
        # Тест валидации
        is_valid, msg = validate_question_text("Нормальный вопрос")
        if is_valid:
            print_success("Валидация текста работает")
        else:
            print_error("Валидация текста не работает")
            return False
        
        # Тест валидации длинного текста
        long_text = "x" * 1001
        is_valid, msg = validate_question_text(long_text)
        if not is_valid:
            print_success("Валидация длины работает")
        else:
            print_error("Валидация длины не работает")
            return False
        
        # Тест генерации ID
        id1 = generate_question_id()
        id2 = generate_question_id()
        if id1 != id2 and len(id1) > 20:
            print_success("Генерация ID работает")
        else:
            print_error("Генерация ID не работает")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка проверки утилит: {e}")
        return False


async def main():
    """Главная функция тестирования"""
    
    print_section("🧪 ТЕСТИРОВАНИЕ TELEGRAM-БОТА")
    
    results = []
    
    # Тест 1: Утилиты
    print_section("1. Проверка утилит")
    results.append(('Утилиты', test_utils()))
    
    # Тест 2: База данных
    print_section("2. Проверка базы данных")
    results.append(('База данных', test_database()))
    
    # Тест 3: Подключение к боту
    print_section("3. Проверка подключения к боту")
    results.append(('Подключение к боту', await test_bot_connection()))
    
    # Тест 4: Доступ к каналу
    print_section("4. Проверка доступа к каналу")
    results.append(('Доступ к каналу', await test_channel_access()))
    
    # Итоги
    print_section("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
            passed += 1
        else:
            print_error(f"{test_name}: FAILED")
            failed += 1
    
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"Всего тестов: {len(results)}")
    print(f"{GREEN}Успешно: {passed}{RESET}")
    print(f"{RED}Провалено: {failed}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")
    
    if failed == 0:
        print_success("🎉 Все тесты пройдены! Бот готов к работе.")
        print_info("Запустите бота командой: python bot.py")
        return 0
    else:
        print_error("⚠️  Некоторые тесты провалены. Исправьте проблемы перед запуском.")
        return 1


if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        sys.exit(1)
