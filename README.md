# FastApi веб-сервис сокращения ссылок

## Описание API.

Это API-сервис по сокращению ссылок. Этот сервис предоставляет API для сокращения ссылок с возможностью создания, управления и поиска коротких ссылок. Поддерживает авторизацию пользователей, создание ссылок с кастомными или случайными короткими кодами, а также базовую статистику использования. Используется Redis для кэширования. 

Функции сервиса:
- Регистрация и авторизация пользователей через JWT-токены.
- Создание коротких ссылок с указанием срока действия.
- Поиск ссылок по оригинальному URL.
- Получение статистики по использованию ссылок.

## Примеры запросов

### 1. Получение токена (авторизация)
```bash
curl -X 'POST' \
  'https://shortlink-fastapi.onrender.com/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin&password=admin'
```
### Ответ
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
### 2. Создание короткой ссылки
```bash
curl -X 'POST' \
  'https://shortlink-fastapi.onrender.com/links/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <your-token>' \
  -H 'Content-Type: application/json' \
  -d '{"original_url": "https://example.com", "short_code": "exmpl"}'
```
### Ответ
```json
{
  "id": 1,
  "original_url": "https://example.com",
  "short_code": "exmpl",
  "created_at": "2025-03-17T12:00:00",
  "expires_at": "2025-04-16T12:00:00",
  "last_used": null,
  "clicks": 0,
  "user_id": 1
}
```
### 3. Поиск ссылки по оригинальному URL
```bash
curl -X 'GET' \
  'https://shortlink-fastapi.onrender.com/links/search?original_url=https%3A%2F%2Fexample.com' \
  -H 'accept: application/json'
```
### Ответ
```json
[
  {
    "id": 1,
    "original_url": "https://example.com",
    "short_code": "exmpl",
    "created_at": "2025-03-17T12:00:00",
    "expires_at": "2025-04-16T12:00:00",
    "last_used": null,
    "clicks": 0,
    "user_id": 1
  }
]
```
### 4. Получение статистики по короткой ссылке
```bash
curl -X 'GET' \
  'https://shortlink-fastapi.onrender.com/links/stats/exmpl' \
  -H 'accept: application/json'
```
### Ответ
```json
{
  "original_url": "https://example.com",
  "short_code": "exmpl",
  "clicks": 0,
  "created_at": "2025-03-17T12:00:00",
  "expires_at": "2025-04-16T12:00:00",
  "last_used": null
}
```

## Инструкцию по запуску

### Чтобы протестировать его, выполните следующие шаги:

1. Откройте документацию Swagger:
- Перейдите в браузере по вышеуказанной ссылке. 
- Здесь вы увидите все доступные эндпоинты и сможете их протестировать.
2. Получите токен:
- В Swagger найдите POST /register.
- Нажмите "Try it out".
- Придумайте и введите username и password.
- После регистрации нажмите "Authorize", чтобы войти (логин).
3. Протестируйте эндпоинты:
- В Swagger выберите любой эндпоинт (например, POST /links/).
- Заполните необходимые поля и выполните запрос, нажав "Execute".
4. Используйте curl (альтернатива):
- В Swagger найдите POST /token.
- Нажмите "Try it out".
- Введите username и password (если пользователь уже создан через /register).
- Скопируйте примеры запросов выше, заменив <your-token> на ваш токен.
- Выполните их в терминале.
- Примечание: Если у вас нет пользователя, вам нужно создать его напрямую через /register.

## Описание базы данных

Схема базы данных включает две основные таблицы:

1. Таблица users (зарегистрированные пользователи)
| Поле | Описание |
|-------------|-------------|
| id | Идентификатор пользователя |
| username | String, уникальный логин пользователя. |
| hashed_password | String, хэшированный пароль (с использованием passlib). |
| links | Связь один-ко-многим с таблицей links. |

2. Таблица links (сгенерированные сервисом короткие ссылки)
| Поле | Описание |
|-------------|-------------|
| id | Идентификатор  ссылки |
| original_url | Оригинальный URL |
| short_code | String, короткий код ссылки (уникальный, индексируется). |
| created_at | Дата и время создания . |
| expires_at | DateTime, срок действия (опционально). |
| last_used | DateTime, дата последнего использования (опционально). |
| clicks | Integer, количество переходов (по умолчанию 0).
| user_id | Integer, внешний ключ на users.id (опционально, nullable). |
| user | Связь многие-к-одному с таблицей users. |

## Тестирование кода

### Структура и уровни тестов

В репозитории присутствуют следующие тестовые файлы (указаны от самого «низкоуровневого» к «высокоуровневому»):

1. **Юнит-тесты (минимальный контекст, проверка отдельных функций и модулей):**
   - `test_auth.py` — тестирует функции аутентификации и работы с токенами (создание, верификация).
   - `test_services.py` — охватывает внутренние сервисы (создание, поиск, удаление ссылок и т.д.).

2. **Функциональные (интеграционные) тесты (проверка взаимодействия через HTTP-запросы):**
   - `test_links.py` — тестирует эндпоинты, связанные с ссылками (создание, удаление, поиск).
   - `test_users.py` — тестирует эндпоинты, связанные с пользователями (регистрация, логин).

3. **Нагрузочные (performance) тесты:**
   - `locustfile.py` — сценарии нагрузки с помощью Locust (проверка производительности и устойчивости под нагрузкой).

Прочие файлы в папке `tests`:
- `conftest.py` — конфигурация для тестовой среды (фикстуры, переопределение зависимостей, настройка базы данных).
- `coverage.xml` — итоговый XML-отчет о покрытии (генерируется автоматически).
- `htmlcov/` — папка с HTML-отчетом о покрытии (генерируется командой `coverage html`).

### Запуск

1. Для запуска, выполните:

```bash
python -m pytest --cov app tests
```

#### Краткая сводка покрытия находится в `/results/test_files.html` 

| Module                   | Statements | Missing | Coverage |
|--------------------------|-----------:|--------:|---------:|
| **app/__init__.py**      | 0         | 0       | 100%     |
| **app/auth.py**          | 38        | 3       | 92%      |
| **app/cache.py**         | 10        | 0       | 100%     |
| **app/config.py**        | 5         | 0       | 100%     |
| **app/database.py**      | 12        | 0       | 100%     |
| **app/main.py**          | 7         | 0       | 100%     |
| **app/models.py**        | 21        | 0       | 100%     |
| **app/routers/__init__.py** | 0      | 0       | 100%     |
| **app/routers/links.py** | 61        | 21      | 66%      |
| **app/routers/users.py** | 27        | 0       | 100%     |
| **app/schemas.py**       | 29        | 0       | 100%     |
| **app/services.py**      | 64        | 0       | 100%     |
| **app/utils.py**         | 5         | 0       | 100%     |
| **Total**                | 282       | 24      | **91%**  |

2. Чтобы запустить нагрузочное тестирование, выполните:

```bash
locust -f tests/locustfile.py
```

Дальше откройте http://localhost:8089 в браузере, настройте количество пользователей и интенсивность.
