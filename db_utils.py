#!/usr/bin/env python3
"""
Утилита для управления базой данных вопросов
"""
import sys
from datetime import datetime
from models import Question, init_db, db


def show_stats():
    """Показать статистику по вопросам"""
    init_db()
    
    total = Question.select().count()
    pending = Question.select().where(Question.status == 'pending').count()
    approved = Question.select().where(Question.status == 'approved').count()
    rejected = Question.select().where(Question.status == 'rejected').count()
    
    print("\n" + "=" * 50)
    print("📊 Статистика вопросов")
    print("=" * 50)
    print(f"Всего вопросов:      {total}")
    print(f"Ожидают модерации:   {pending}")
    print(f"Принято:             {approved}")
    print(f"Отклонено:           {rejected}")
    print("=" * 50 + "\n")


def list_questions(status=None, limit=10):
    """Показать список вопросов"""
    init_db()
    
    query = Question.select().order_by(Question.created_at.desc())
    
    if status:
        query = query.where(Question.status == status)
    
    questions = query.limit(limit)
    
    if not questions:
        print(f"\n❌ Вопросы не найдены")
        return
    
    print(f"\n{'=' * 80}")
    print(f"📋 Список вопросов (показаны последние {limit})")
    if status:
        print(f"Статус: {status}")
    print("=" * 80)
    
    for q in questions:
        print(f"\nID: {q.id}")
        print(f"Дата: {q.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Статус: {q.status}")
        print(f"Вопрос: {q.text[:100]}{'...' if len(q.text) > 100 else ''}")
        if q.video_file_id:
            print(f"Видео ID: {q.video_file_id[:30]}...")
        print("-" * 80)


def delete_question(question_id):
    """Удалить вопрос по ID"""
    init_db()
    
    try:
        question = Question.get_or_none(Question.id == question_id)
        if not question:
            print(f"❌ Вопрос с ID {question_id} не найден")
            return
        
        print(f"\nВопрос:")
        print(f"ID: {question.id}")
        print(f"Текст: {question.text}")
        print(f"Статус: {question.status}")
        
        confirm = input("\n⚠️  Вы уверены, что хотите удалить этот вопрос? (yes/no): ")
        if confirm.lower() in ['yes', 'y', 'да']:
            question.delete_instance()
            print("✅ Вопрос удален")
        else:
            print("❌ Удаление отменено")
    
    except Exception as e:
        print(f"❌ Ошибка при удалении: {e}")


def clear_old_questions(days=30):
    """Удалить старые отклоненные вопросы"""
    init_db()
    
    from datetime import timedelta
    cutoff_date = datetime.now() - timedelta(days=days)
    
    old_questions = Question.select().where(
        (Question.status == 'rejected') &
        (Question.created_at < cutoff_date)
    )
    
    count = old_questions.count()
    
    if count == 0:
        print(f"❌ Нет отклоненных вопросов старше {days} дней")
        return
    
    print(f"\n⚠️  Найдено {count} отклоненных вопросов старше {days} дней")
    confirm = input("Удалить их? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y', 'да']:
        deleted = 0
        for q in old_questions:
            q.delete_instance()
            deleted += 1
        print(f"✅ Удалено {deleted} вопросов")
    else:
        print("❌ Удаление отменено")


def export_questions(filename='questions_export.txt'):
    """Экспорт всех вопросов в текстовый файл"""
    init_db()
    
    questions = Question.select().order_by(Question.created_at)
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("ЭКСПОРТ ВОПРОСОВ\n")
            f.write("=" * 80 + "\n\n")
            
            for q in questions:
                f.write(f"ID: {q.id}\n")
                f.write(f"Дата: {q.created_at}\n")
                f.write(f"Статус: {q.status}\n")
                f.write(f"Вопрос: {q.text}\n")
                if q.video_file_id:
                    f.write(f"Видео ID: {q.video_file_id}\n")
                f.write("\n" + "-" * 80 + "\n\n")
        
        print(f"✅ Экспорт завершен: {filename}")
        print(f"   Экспортировано вопросов: {questions.count()}")
    
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")


def show_help():
    """Показать справку по командам"""
    help_text = """
    Утилита управления базой данных вопросов
    
    Использование: python db_utils.py <команда> [параметры]
    
    Команды:
        stats                          - Показать статистику
        list [status] [limit]          - Список вопросов
                                         status: pending, approved, rejected
                                         limit: количество (по умолчанию 10)
        delete <question_id>           - Удалить вопрос по ID
        clear [days]                   - Удалить старые отклоненные вопросы
                                         days: количество дней (по умолчанию 30)
        export [filename]              - Экспорт в текстовый файл
        help                           - Показать эту справку
    
    Примеры:
        python db_utils.py stats
        python db_utils.py list pending 20
        python db_utils.py delete abc-123-def
        python db_utils.py clear 60
        python db_utils.py export my_export.txt
    """
    print(help_text)


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'stats':
        show_stats()
    
    elif command == 'list':
        status = sys.argv[2] if len(sys.argv) > 2 else None
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        list_questions(status, limit)
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Укажите ID вопроса")
            return
        question_id = sys.argv[2]
        delete_question(question_id)
    
    elif command == 'clear':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        clear_old_questions(days)
    
    elif command == 'export':
        filename = sys.argv[2] if len(sys.argv) > 2 else 'questions_export.txt'
        export_questions(filename)
    
    elif command == 'help':
        show_help()
    
    else:
        print(f"❌ Неизвестная команда: {command}")
        print("Используйте 'python db_utils.py help' для справки")


if __name__ == '__main__':
    main()
