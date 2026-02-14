#!/usr/bin/env python3
"""
Скрипт для резервного копирования базы данных
"""
import os
import shutil
from datetime import datetime

from loguru import logger

DB_FILE = 'questions.db'
BACKUP_DIR = 'backups'


def create_backup():
    """Создание резервной копии базы данных"""

    # Создание директории для бэкапов, если её нет
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        logger.info(f"Создана директория для бэкапов: {BACKUP_DIR}")

    # Проверка существования БД
    if not os.path.exists(DB_FILE):
        logger.error(f"Ошибка: файл базы данных {DB_FILE} не найден")
        return False

    # Формирование имени файла бэкапа с текущей датой и временем
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'questions_backup_{timestamp}.db'
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        # Копирование файла базы данных
        shutil.copy2(DB_FILE, backup_path)
        file_size = os.path.getsize(backup_path)
        logger.info(f"✅ Резервная копия создана успешно:")
        logger.info(f"   Файл: {backup_path}")
        logger.info(f"   Размер: {file_size} байт")
        logger.info(f"   Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при создании резервной копии: {e}")
        return False


def list_backups():
    """Показать список всех резервных копий"""

    if not os.path.exists(BACKUP_DIR):
        logger.warning(f"Директория {BACKUP_DIR} не найдена")
        return

    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]

    if not backups:
        logger.info("Резервные копии не найдены")
        return

    print(f"\nНайдено резервных копий: {len(backups)}\n")

    for backup in sorted(backups, reverse=True):
        backup_path = os.path.join(BACKUP_DIR, backup)
        size = os.path.getsize(backup_path)
        mtime = datetime.fromtimestamp(os.path.getmtime(backup_path))
        logger.info(f"  {backup}")
        logger.info(f"    Размер: {size} байт")
        logger.info(f"    Дата: {mtime.strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_backups()
    else:
        create_backup()
