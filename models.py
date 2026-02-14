"""
Модели базы данных для бота анонимных вопросов
"""
import datetime

from peewee import (
    Model, CharField, TextField, DateTimeField, SqliteDatabase
)

# Инициализация базы данных
db = SqliteDatabase('questions.db')


class Question(Model):
    """Модель для хранения вопросов"""
    id = CharField(primary_key=True)  # Уникальный идентификатор вопроса
    text = TextField()  # Текст вопроса
    status = CharField(default='pending')  # Статус: pending, approved, rejected
    video_file_id = CharField(null=True)  # file_id кружочка (может быть пустым)
    created_at = DateTimeField(default=datetime.datetime.now)  # Дата и время создания

    class Meta:
        database = db
        table_name = 'questions'


def init_db():
    """Инициализация базы данных и создание таблиц"""
    db.connect()
    db.create_tables([Question], safe=True)
    print("База данных инициализирована успешно")


def close_db():
    """Закрытие соединения с базой данных"""
    if not db.is_closed():
        db.close()
