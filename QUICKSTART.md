# Быстрый старт

## 1. Установка

```bash
# Установка зависимостей
pip install -r requirements.txt
```

## 2. Настройка

```bash
# Создание конфигурационного файла
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
BOT_TOKEN=ваш_токен_от_BotFather
ADMIN_ID=ваш_telegram_id
CHANNEL_ID=@ваш_канал
```

### Где взять данные:

- **BOT_TOKEN**: [@BotFather](https://t.me/BotFather) → `/newbot`
- **ADMIN_ID**: [@userinfobot](https://t.me/userinfobot)
- **CHANNEL_ID**: Имя вашего канала (с @) или числовой ID

⚠️ **Важно**: Добавьте бота в канал как администратора!

## 3. Проверка конфигурации

```bash
python check_config.py
```

## 4. Запуск бота

```bash
python bot.py
```

## 5. Тестирование

1. Найдите бота в Telegram
2. Отправьте `/start`
3. Напишите любой вопрос
4. Проверьте, что администратор получил уведомление

## Полезные команды

```bash
# Статистика по вопросам
python db_utils.py stats

# Список последних вопросов
python db_utils.py list pending

# Резервное копирование БД
python backup.py

# Список всех бэкапов
python backup.py list
```

## Структура файлов

- `bot.py` - главный файл бота
- `models.py` - модели базы данных
- `config.py` - конфигурация
- `utils.py` - вспомогательные функции
- `db_utils.py` - управление БД
- `backup.py` - резервное копирование
- `check_config.py` - проверка настроек

## Логи

Все действия записываются в `bot.log`

## Помощь

Подробная документация: [README.md](README.md)
