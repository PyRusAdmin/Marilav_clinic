"""
Основной файл Telegram-бота для анонимных вопросов
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)

from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID, MAX_QUESTION_LENGTH
from models import Question, init_db, close_db
from utils import escape_markdown, generate_question_id, validate_question_text

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Состояния для FSM
class AdminStates(StatesGroup):
    waiting_for_video = State()  # Ожидание видеосообщения от администратора


# ============== ОБРАБОТЧИКИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==============

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    welcome_text = (
        "👋 Добро пожаловать\\!\n\n"
        "Я бот для анонимных вопросов клиники «МариЛав»\\.\n\n"
        "Вы можете задать любой вопрос, и врачи клиники ответят на него в видеоформате\\. "
        "Ваш вопрос будет полностью анонимным\\.\n\n"
        "💬 Просто напишите ваш вопрос в чат\\."
    )

    try:
        await message.answer(welcome_text, parse_mode="MarkdownV2")
        logger.info(f"Пользователь {message.from_user.id} запустил бота")
    except Exception as e:
        logger.error(f"Ошибка при отправке приветствия: {e}")


@dp.message(F.text & ~F.photo & ~F.document & ~F.video & ~F.audio)
async def handle_question(message: Message):
    """Обработчик текстовых сообщений (вопросов) от пользователей"""

    # Игнорируем сообщения от администратора (если он не в режиме ожидания видео)
    if message.from_user.id == ADMIN_ID:
        return

    question_text = message.text

    # Валидация вопроса
    is_valid, error_message = validate_question_text(question_text, MAX_QUESTION_LENGTH)

    if not is_valid:
        await message.answer(f"❌ {error_message}")
        logger.warning(f"Невалидный вопрос от пользователя {message.from_user.id}: {error_message}")
        return

    try:
        # Генерация ID и сохранение вопроса в БД
        question_id = generate_question_id()
        Question.create(
            id=question_id,
            text=question_text,
            status='pending'
        )

        # Подтверждение пользователю
        confirmation_text = (
            "✅ Ваш вопрос отправлен\\!\n\n"
            "Ответ будет опубликован в канале «МариЛав»: @marilove\\_channel\n\n"
            "Спасибо\\!"
        )
        await message.answer(confirmation_text, parse_mode="MarkdownV2")

        # Уведомление администратору
        await send_question_to_admin(question_id, question_text)

        logger.info(f"Новый вопрос {question_id} от пользователя {message.from_user.id}")

    except Exception as e:
        logger.error(f"Ошибка при обработке вопроса: {e}")
        await message.answer("❌ Произошла ошибка при отправке вопроса. Попробуйте позже.")


@dp.message(F.content_type.in_({'photo', 'document', 'video', 'audio', 'voice', 'sticker'}))
async def handle_attachments(message: Message):
    """Обработчик вложений - запрещаем их"""
    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "❌ Пожалуйста, отправьте только текстовый вопрос без вложений."
        )
        logger.warning(f"Пользователь {message.from_user.id} попытался отправить вложение")


# ============== ОБРАБОТЧИКИ ДЛЯ АДМИНИСТРАТОРА ==============

async def send_question_to_admin(question_id: str, question_text: str):
    """Отправка вопроса администратору с кнопками модерации"""

    # Создание inline-кнопок
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{question_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{question_id}")
        ]
    ])

    # Экранирование текста для MarkdownV2
    escaped_text = escape_markdown(question_text)

    admin_message = (
        f"📩 *Новый вопрос*\n\n"
        f"ID: `{question_id}`\n\n"
        f"*Вопрос:*\n{escaped_text}"
    )

    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        logger.info(f"Вопрос {question_id} отправлен администратору")
    except Exception as e:
        logger.error(f"Ошибка при отправке вопроса администратору: {e}")


@dp.callback_query(F.data.startswith("approve_"))
async def callback_approve(callback: CallbackQuery, state: FSMContext):
    """Обработчик нажатия кнопки 'Принять'"""

    question_id = callback.data.split("_", 1)[1]

    try:
        # Обновление статуса в БД
        Question.update(status='approved').where(Question.id == question_id).execute()

        # Сохранение ID вопроса в состоянии
        await state.update_data(question_id=question_id)
        await state.set_state(AdminStates.waiting_for_video)

        # Уведомление администратору
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            f"✅ Вопрос принят\\!\n\n"
            f"Теперь отправьте видеосообщение \\(кружочек\\) с ответом\\.",
            parse_mode="MarkdownV2"
        )

        await callback.answer("Вопрос принят")
        logger.info(f"Администратор принял вопрос {question_id}")

    except Exception as e:
        logger.error(f"Ошибка при принятии вопроса: {e}")
        await callback.answer("Ошибка при обработке", show_alert=True)


@dp.callback_query(F.data.startswith("reject_"))
async def callback_reject(callback: CallbackQuery):
    """Обработчик нажатия кнопки 'Отклонить'"""

    question_id = callback.data.split("_", 1)[1]

    try:
        # Обновление статуса в БД
        Question.update(status='rejected').where(Question.id == question_id).execute()

        # Уведомление администратору
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("❌ Вопрос отклонён")

        await callback.answer("Вопрос отклонён")
        logger.info(f"Администратор отклонил вопрос {question_id}")

    except Exception as e:
        logger.error(f"Ошибка при отклонении вопроса: {e}")
        await callback.answer("Ошибка при обработке", show_alert=True)


@dp.message(AdminStates.waiting_for_video, F.video_note)
async def handle_admin_video(message: Message, state: FSMContext):
    """Обработчик видеосообщения (кружочка) от администратора"""

    # Получение ID вопроса из состояния
    data = await state.get_data()
    question_id = data.get('question_id')

    if not question_id:
        await message.answer("❌ Ошибка: не найден ID вопроса")
        await state.clear()
        return

    try:
        # Получение информации о вопросе из БД
        question = Question.get_or_none(Question.id == question_id)

        if not question:
            await message.answer("❌ Вопрос не найден в базе данных")
            await state.clear()
            return

        # Сохранение file_id видео в БД
        video_file_id = message.video_note.file_id
        Question.update(video_file_id=video_file_id).where(Question.id == question_id).execute()

        # Публикация в канале
        await publish_to_channel(question.text, video_file_id)

        # Уведомление администратору
        await message.answer("✅ Вопрос опубликован в канале\\!", parse_mode="MarkdownV2")

        # Очистка состояния
        await state.clear()

        logger.info(f"Вопрос {question_id} опубликован в канале")

    except Exception as e:
        logger.error(f"Ошибка при публикации вопроса: {e}")
        await message.answer("❌ Произошла ошибка при публикации")
        await state.clear()


@dp.message(AdminStates.waiting_for_video)
async def handle_wrong_content(message: Message):
    """Обработчик неправильного типа контента от администратора"""
    await message.answer(
        "❌ Пожалуйста, отправьте именно видеосообщение (кружочек), а не другой тип контента."
    )


async def publish_to_channel(question_text: str, video_file_id: str):
    """Публикация вопроса и ответа в канале"""

    # Формирование текста поста
    signature = (
        "\n\n📍 На вопросы отвечают квалифицированные врачи: "
        "косметологи, массажисты, специалисты по коррекции фигуры "
        "и главный врач клиники Мария Лаврентьева. "
        "Ответ может занять какое-то время.\n\n"
        "👉 Подписывайтесь: @marilove_channel"
    )

    caption = f"❓ Вопрос: {question_text}{signature}"

    try:
        # Отправка видеосообщения с подписью в канал
        await bot.send_video_note(
            chat_id=CHANNEL_ID,
            video_note=video_file_id,
            duration=None  # Автоматическая длительность
        )

        # Отправка текста отдельным сообщением (т.к. кружочки не поддерживают длинные подписи)
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=caption
        )

        logger.info(f"Пост опубликован в канале {CHANNEL_ID}")

    except Exception as e:
        logger.error(f"Ошибка при публикации в канале: {e}")
        raise


# ============== ЗАПУСК БОТА ==============

async def main():
    """Основная функция запуска бота"""

    # Инициализация базы данных
    init_db()

    logger.info("Бот запущен")

    try:
        # Запуск polling
        await dp.start_polling(bot)
    finally:
        # Закрытие соединений при остановке
        await bot.session.close()
        close_db()
        logger.info("Бот остановлен")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
