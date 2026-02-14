"""
Утилиты для бота
"""
import uuid


def escape_markdown(text: str) -> str:
    """
    Экранирование специальных символов для MarkdownV2
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def generate_question_id() -> str:
    """
    Генерация уникального ID для вопроса
    """
    return str(uuid.uuid4())


def validate_question_text(text: str, max_length: int = 1000) -> tuple[bool, str]:
    """
    Валидация текста вопроса
    Возвращает (True, "") если валидация прошла успешно
    или (False, "сообщение об ошибке") если есть проблемы
    """
    if not text or not text.strip():
        return False, "Вопрос не может быть пустым"

    if len(text) > max_length:
        return False, f"Вопрос слишком длинный. Максимум {max_length} символов"

    return True, ""
