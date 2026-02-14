#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации перед запуском бота
"""
import os
import sys
from dotenv import load_dotenv

# Цветной вывод
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    print(f"{RED}❌ {message}{RESET}")


def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")


def check_env_file():
    """Проверка наличия .env файла"""
    if not os.path.exists('.env'):
        print_error(".env файл не найден!")
        print_warning("Создайте .env файл на основе .env.example:")
        print("   cp .env.example .env")
        return False
    print_success(".env файл найден")
    return True


def check_env_variables():
    """Проверка переменных окружения"""
    load_dotenv()

    errors = []
    warnings = []

    # Проверка BOT_TOKEN
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        errors.append("BOT_TOKEN не установлен")
    elif bot_token == 'your_bot_token_here':
        errors.append("BOT_TOKEN не изменен (используется значение по умолчанию)")
    elif len(bot_token) < 40:
        warnings.append("BOT_TOKEN выглядит подозрительно коротким")
    else:
        print_success(f"BOT_TOKEN установлен (длина: {len(bot_token)} символов)")

    # Проверка ADMIN_ID
    admin_id = os.getenv('ADMIN_ID')
    if not admin_id:
        errors.append("ADMIN_ID не установлен")
    elif not admin_id.isdigit():
        errors.append("ADMIN_ID должен быть числом")
    elif admin_id == '123456789':
        errors.append("ADMIN_ID не изменен (используется значение по умолчанию)")
    else:
        print_success(f"ADMIN_ID установлен: {admin_id}")

    # Проверка CHANNEL_ID
    channel_id = os.getenv('CHANNEL_ID')
    if not channel_id:
        errors.append("CHANNEL_ID не установлен")
    elif channel_id == '@your_channel':
        errors.append("CHANNEL_ID не изменен (используется значение по умолчанию)")
    elif not (channel_id.startswith('@') or channel_id.startswith('-100')):
        warnings.append("CHANNEL_ID должен начинаться с @ (для публичных) или -100 (для приватных каналов)")
    else:
        print_success(f"CHANNEL_ID установлен: {channel_id}")

    return errors, warnings


def check_dependencies():
    """Проверка установленных зависимостей"""
    required_packages = {
        'aiogram': '3.0',
        'peewee': '3.0',
        'dotenv': '0.1'
    }

    missing = []

    for package, min_version in required_packages.items():
        try:
            if package == 'dotenv':
                __import__('dotenv')
                module_name = 'python-dotenv'
            else:
                __import__(package)
                module_name = package
            print_success(f"{module_name} установлен")
        except ImportError:
            missing.append(package)
            print_error(f"{package} не установлен")

    return missing


def check_files():
    """Проверка наличия необходимых файлов"""
    required_files = ['bot.py', 'models.py', 'config.py', 'utils.py']
    missing = []

    for file in required_files:
        if os.path.exists(file):
            print_success(f"Файл {file} найден")
        else:
            missing.append(file)
            print_error(f"Файл {file} не найден")

    return missing


def main():
    """Главная функция проверки"""
    print("=" * 60)
    print("🔍 Проверка конфигурации Telegram-бота")
    print("=" * 60)
    print()

    all_ok = True

    # Проверка файлов
    print("📁 Проверка файлов проекта...")
    missing_files = check_files()
    if missing_files:
        all_ok = False
    print()

    # Проверка .env файла
    print("⚙️  Проверка конфигурации...")
    if not check_env_file():
        all_ok = False
        print()
        sys.exit(1)

    # Проверка переменных окружения
    errors, warnings = check_env_variables()
    if errors:
        all_ok = False
        print()
        print("Найдены ошибки в конфигурации:")
        for error in errors:
            print_error(error)

    if warnings:
        print()
        print("Предупреждения:")
        for warning in warnings:
            print_warning(warning)

    print()

    # Проверка зависимостей
    print("📦 Проверка зависимостей...")
    missing_deps = check_dependencies()
    if missing_deps:
        all_ok = False
        print()
        print_error("Установите недостающие зависимости:")
        print("   pip install -r requirements.txt")

    print()
    print("=" * 60)

    if all_ok and not errors:
        print_success("Все проверки пройдены! Бот готов к запуску.")
        print()
        print("Запустите бота командой:")
        print("   python bot.py")
    else:
        print_error("Обнаружены проблемы. Исправьте их перед запуском.")
        sys.exit(1)

    print("=" * 60)


if __name__ == '__main__':
    main()
