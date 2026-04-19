# Telegram MCP Server для xiaozhi.me

Документация по интеграции Telegram бота с xiaozhi через MCP протокол.

## Оглавление

1. [Архитектура](#архитектура)
2. [Возможности](#возможности)
3. [Требования](#требования)
4. [Установка на Ubuntu](#установка-на-ubuntu)
5. [Настройка](#настройка)
6. [Запуск](#запуск)
7. [Подключение к xiaozhi](#подключение-к-xiaozhi)
8. [Доступные инструменты](#доступные-инструменты)
9. [Примеры использования](#примеры-использования)
10. [Устранение проблем](#устранение-проблем)

---

## Архитектура

```
┌─────────────────┐      WebSocket       ┌──────────────────┐
│  xiaozhi.me     │◄─────────────────────►│  mcp_pipe.py     │
│  (MCP Client)   │   wss://api.xiaozhi   │  (прокси)        │
└─────────────────┘                      └────────┬─────────┘
                                                   │
                                                   │ stdio
                                                   ▼
                                          ┌──────────────────┐
                                          │  telegram_mcp.py │
                                          │  (MCP Server)    │
                                          └────────┬─────────┘
                                                   │
                                                   ▼
                                          ┌──────────────────┐
                                          │  Telegram Bot API│
                                          └──────────────────┘
```

**Поток данных:**
1. xiaozhi отправляет команду через WebSocket на `mcp_pipe.py`
2. `mcp_pipe.py` проксирует запрос в `telegram_mcp.py` через stdio
3. `telegram_mcp.py` выполняет действие через Telegram Bot API
4. Ответ возвращается обратно по цепочке

---

## Возможности

- **Отправка сообщений** - текст, фото, документы, местоположение
- **Управление чатами** - получить инфу, участников, ссылки-приглашения
- **Модерация** - кик/бан пользователей, закреп/откреп сообщений
- **Получение данных** - инфо о боте, чатах, участниках

---

## Требования

- Python 3.10+
- Ubuntu 20.04+ (или другой Linux дистрибутив)
- Telegram бот токен (получить у @BotFather)
- MCP endpoint от xiaozhi.me

---

## Установка на Ubuntu

### Шаг 1: Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

### Шаг 2: Установка Python и зависимостей

```bash
# Установка Python 3 и необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv git

# Проверка версии Python
python3 --version
```

### Шаг 3: Создание директории проекта

```bash
# Создаем директорию
mkdir -p ~/telegram-mcp-server
cd ~/telegram-mcp-server

# Клонируем репозиторий (если есть) или создаем файлы вручную
# Здесь предполагается, что файлы уже скопированы
```

### Шаг 4: Создание виртуального окружения

```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Теперь в начале командной строки должен появиться (venv)
```

### Шаг 5: Установка зависимостей

```bash
# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements.txt
```

### Шаг 6: Настройка переменных окружения

```bash
# Копируем пример конфигурации
cp env.example .env

# Редактируем конфигурацию
nano .env
```

Содержимое `.env` файла:

```bash
# Telegram Bot Token (получить у @BotFather в Telegram)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# MCP Endpoint от xiaozhi.me (получить в панели xiaozhi.me)
MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Как получить Telegram Bot Token:**
1. Откройте Telegram и найдите @BotFather
2. Отправьте `/newbot` для создания нового бота
3. Следуйте инструкциям, введите имя бота
4. Скопируйте токен вида `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

**Как получить MCP Endpoint:**
1. Зайдите на xiaozhi.me и авторизуйтесь
2. Перейдите в настройки устройства
3. Найдите раздел "MCP接入点" (MCP Endpoint)
4. Скопируйте WebSocket URL

### Шаг 7: Проверка установки

```bash
# Проверяем, что все установлено правильно
python3 -c "import telegram; import websockets; print('OK')"
```

---

## Настройка

### Структура файлов

```
telegram-mcp-server/
├── env.example           # Пример конфигурации
├── .env                  # Ваша конфигурация (создать из env.example)
├── mcp_pipe.py          # Прокси-сервер
├── telegram_mcp.py      # MCP сервер с инструментами Telegram
├── requirements.txt     # Зависимости Python
└── venv/               # Виртуальное окружение (после установки)
```

### Конфигурация .env

Обязательные переменные:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | `123456789:ABC...` |
| `MCP_ENDPOINT` | WebSocket URL xiaozhi | `wss://api.xiaozhi.me/mcp/?token=...` |

---

## Запуск

### Активация виртуального окружения

```bash
cd ~/telegram-mcp-server
source venv/bin/activate
```

### Запуск прокси-сервера

```bash
python mcp_pipe.py
```

Ожидаемый вывод при успешном подключении:

```
2026-04-18 22:00:00,000 - __main__ - INFO - Connecting to xiaozhi MCP: wss://api.xiaozhi.me/mcp/?token=...
2026-04-18 22:00:00,100 - __main__ - INFO - Connected to xiaozhi MCP
2026-04-18 22:00:00,200 - __main__ - INFO - Starting MCP client: telegram_mcp.py
2026-04-18 22:00:00,300 - __main__ - INFO - MCP client started
```

### Запуск в фоновом режиме (рекомендуется)

```bash
# Запуск в фоне с логами
nohup python mcp_pipe.py > mcp.log 2>&1 &

# Проверка работы
tail -f mcp.log

# Остановка
pkill -f mcp_pipe.py
```

### Запуск как systemd сервис

```bash
# Создаем файл сервиса
sudo nano /etc/systemd/system/telegram-mcp.service
```

Содержимое:

```ini
[Unit]
Description=Telegram MCP Server for xiaozhi
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram-mcp-server
Environment="PATH=/home/ubuntu/telegram-mcp-server/venv/bin"
EnvironmentFile=/home/ubuntu/telegram-mcp-server/.env
ExecStart=/home/ubuntu/telegram-mcp-server/venv/bin/python mcp_pipe.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Запуск сервиса
sudo systemctl start telegram-mcp

# Автозапуск при загрузке
sudo systemctl enable telegram-mcp

# Проверка статуса
sudo systemctl status telegram-mcp

# Просмотр логов
sudo journalctl -u telegram-mcp -f
```

---

## Подключение к xiaozhi

### Через панель xiaozhi.me

1. Войдите в панель xiaozhi.me
2. Перейдите в настройки устройства
3. Найдите раздел "MCP接入点" (MCP Endpoint)
4. Введите URL вашего MCP сервера

### Локальный проброс портов (если xiaozhi на удалённом сервере)

Если xiaozhi.me подключается к вашему локальному серверу, нужно пробросить порт:

```bash
# Вариант 1: ngrok
# Скачайте и установите ngrok
ngrok tcp 8080

# Вариант 2: через SSH туннель
ssh -R 80:localhost:8080 serveo.net
```

### Проверка подключения

После запуска mcp_pipe.py в логах появится:
```
INFO - Connected to xiaozhi MCP
```

Это означает, что связь установлена и xiaozhi видит ваши Telegram инструменты.

---

## Доступные инструменты

### Сообщения

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `telegram_send_message` | Отправить текстовое сообщение | `chat_id`, `text`, `parse_mode` |
| `telegram_send_photo` | Отправить фото | `chat_id`, `photo`, `caption` |
| `telegram_send_document` | Отправить документ | `chat_id`, `document`, `caption` |
| `telegram_send_location` | Отправить геолокацию | `chat_id`, `latitude`, `longitude` |
| `telegram_delete_message` | Удалить сообщение | `chat_id`, `message_id` |

### Информация

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `telegram_get_chat` | Информация о чате | `chat_id` |
| `telegram_get_me` | Информация о боте | - |
| `telegram_get_chat_member_count` | Количество участников | `chat_id` |

### Управление чатом

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `telegram_pin_message` | Закрепить сообщение | `chat_id`, `message_id` |
| `telegram_unpin_message` | Открепить сообщение | `chat_id` |
| `telegram_export_invite_link` | Создать ссылку-приглашение | `chat_id` |
| `telegram_kick_chat_member` | Кикнуть пользователя | `chat_id`, `user_id` |
| `telegram_unban_chat_member` | Разбанить пользователя | `chat_id`, `user_id` |

---

## Примеры использования

### Через голосовые команды xiaozhi

После подключения xiaozhi получит доступ к инструментам. Примеры команд:

> "Отправь сообщение в чат X текст Y"

> "Сколько человек в чате X?"

> "Закрепи это сообщение"

> "Создай ссылку-приглашение для чата X"

### Прямое использование через API

```bash
# Отправить сообщение через MCP
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"telegram_send_message","arguments":{"chat_id":"123456","text":"Привет!"}}}' | python telegram_mcp.py
```

---

## Устранение проблем

### Ошибка: "TELEGRAM_BOT_TOKEN not set"

**Решение:** Проверьте `.env` файл:
```bash
cat .env | grep TOKEN
```

### Ошибка: "Connection refused" к xiaozhi

**Возможные причины:**
1. Неверный MCP_ENDPOINT
2. Проблемы с сетью/файрволом
3. Токен истёк

**Решение:**
```bash
# Проверьте доступность
curl -I "ваш_mcp_endpoint"

# Проверьте токен на сайте xiaozhi.me
```

### Ошибка: "python-telegram-bot not found"

**Решение:** Переустановите зависимости:
```bash
pip uninstall python-telegram-bot
pip install python-telegram-bot
```

### Ошибка: "WebSocket connection timeout"

**Решение:** Проверьте файрвол:
```bash
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
```

### Логи не показываются

**Решение:** Проверьте режим отладки:
```bash
export LOG_LEVEL=DEBUG
python mcp_pipe.py
```

### Бот не отвечает на команды

1. Проверьте, что бот запущен и имеет права администратора в группе
2. Убедитесь, что @BotFather разрешил групповые сообщения
3. Проверьте логи на ошибки API Telegram

---

## Обновление

```bash
cd ~/telegram-mcp-server
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## Безопасность

1. **Не.commit'tить `.env`** - добавить в `.gitignore`:
   ```
   .env
   *.log
   ```

2. **Ограничить доступ** - запускать от отдельного пользователя:
   ```bash
   sudo useradd -r -s /bin/false mcp
   sudo chown -R mcp:mcp ~/telegram-mcp-server
   ```

3. **Firewall** - закрыть неиспользуемые порты

---

## Ссылки

- [Документация xiaozhi](https://xiaozhi.dev)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [MCP Protocol](https://modelcontextprotocol.io)
- [python-telegram-bot](https://python-telegram-bot.org)