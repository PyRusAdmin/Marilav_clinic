# Развертывание бота на сервере

## Подготовка сервера (Ubuntu/Debian)

### 1. Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Установка Python 3.10+

```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 3. Создание пользователя для бота (опционально)

```bash
sudo adduser --system --group --no-create-home botuser
```

## Установка бота

### 1. Загрузка файлов

```bash
# Создание директории
mkdir -p /opt/telegram_bot
cd /opt/telegram_bot

# Загрузка файлов (или клонирование репозитория)
# scp или git clone ...
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройка конфигурации

```bash
cp .env.example .env
nano .env
```

Заполните параметры:
- BOT_TOKEN
- ADMIN_ID  
- CHANNEL_ID

### 4. Проверка конфигурации

```bash
python check_config.py
```

### 5. Тестовый запуск

```bash
python bot.py
```

Проверьте работу бота. Если всё ок, остановите (Ctrl+C).

## Настройка автозапуска (systemd)

### 1. Редактирование service файла

```bash
nano marilav-bot.service
```

Измените:
- `your_username` на имя пользователя
- `/path/to/telegram_bot` на реальный путь (например: `/opt/telegram_bot`)

### 2. Копирование service файла

```bash
sudo cp marilav-bot.service /etc/systemd/system/
```

### 3. Настройка прав доступа

```bash
# Если используете специального пользователя
sudo chown -R botuser:botuser /opt/telegram_bot

# Или для текущего пользователя
sudo chown -R $USER:$USER /opt/telegram_bot
```

### 4. Запуск сервиса

```bash
# Перезагрузка конфигурации systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable marilav-bot.service

# Запуск бота
sudo systemctl start marilav-bot.service
```

### 5. Проверка статуса

```bash
# Проверка статуса
sudo systemctl status marilav-bot.service

# Просмотр логов
sudo journalctl -u marilav-bot.service -f

# Или
tail -f /opt/telegram_bot/bot.log
```

## Управление сервисом

```bash
# Запуск
sudo systemctl start marilav-bot.service

# Остановка
sudo systemctl stop marilav-bot.service

# Перезапуск
sudo systemctl restart marilav-bot.service

# Статус
sudo systemctl status marilav-bot.service

# Логи
sudo journalctl -u marilav-bot.service -n 100

# Логи в реальном времени
sudo journalctl -u marilav-bot.service -f
```

## Настройка автоматического резервного копирования

### Создание cron задачи

```bash
crontab -e
```

Добавьте строку для ежедневного бэкапа в 2:00 ночи:

```cron
0 2 * * * cd /opt/telegram_bot && /opt/telegram_bot/venv/bin/python backup.py >> /opt/telegram_bot/backup.log 2>&1
```

Для еженедельной очистки старых бэкапов:

```cron
0 3 * * 0 find /opt/telegram_bot/backups -name "*.db" -mtime +30 -delete
```

## Обновление бота

### 1. Остановка сервиса

```bash
sudo systemctl stop marilav-bot.service
```

### 2. Резервное копирование

```bash
cd /opt/telegram_bot
python backup.py
```

### 3. Обновление файлов

```bash
# Загрузка новых файлов или git pull
git pull  # если используется git

# Обновление зависимостей
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 4. Запуск

```bash
sudo systemctl start marilav-bot.service
sudo systemctl status marilav-bot.service
```

## Мониторинг

### Проверка работы бота

```bash
# Статистика вопросов
cd /opt/telegram_bot
source venv/bin/activate
python db_utils.py stats
```

### Проверка использования ресурсов

```bash
# Использование памяти и CPU
ps aux | grep bot.py

# Размер базы данных
ls -lh /opt/telegram_bot/questions.db
```

### Ротация логов

Создайте файл `/etc/logrotate.d/marilav-bot`:

```
/opt/telegram_bot/bot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 botuser botuser
    postrotate
        systemctl reload marilav-bot.service > /dev/null 2>&1 || true
    endscript
}
```

## Безопасность

### 1. Защита .env файла

```bash
chmod 600 /opt/telegram_bot/.env
```

### 2. Настройка firewall (если нужно)

```bash
# UFW
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

### 3. Регулярные обновления

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Python пакетов
source venv/bin/activate
pip list --outdated
pip install --upgrade aiogram peewee python-dotenv
```

## Решение проблем

### Бот не запускается

```bash
# Проверка логов
sudo journalctl -u marilav-bot.service -n 50

# Проверка прав доступа
ls -la /opt/telegram_bot/

# Проверка конфигурации
cd /opt/telegram_bot
source venv/bin/activate
python check_config.py
```

### База данных повреждена

```bash
# Восстановление из бэкапа
cd /opt/telegram_bot
cp questions.db questions_broken.db
cp backups/questions_backup_YYYYMMDD_HHMMSS.db questions.db
sudo systemctl restart marilav-bot.service
```

### Много ошибок в логах

```bash
# Полная перезагрузка
sudo systemctl stop marilav-bot.service
sudo systemctl start marilav-bot.service

# Если не помогло - переустановка зависимостей
cd /opt/telegram_bot
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## Контакты

При возникновении проблем обращайтесь к технической документации в [README.md](README.md)
