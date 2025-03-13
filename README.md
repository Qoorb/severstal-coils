# Severstal Coils API

API для управления складом рулонов металла.

## Технологии

- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Alembic (миграции)
- Pytest (тесты)

## Установка и запуск

### С использованием Docker

1. Клонируйте репозиторий:

    ```bash
    git clone git@github.com:Qoorb/severstal-coils.git
    cd severstal-coils
    ```

2. Создайте файл .env в корневой директории проекта:

    ```bash
    DATABASE_URL=postgresql://postgres:postgres@db:5432/severstal
    ENVIRONMENT=development
    DEBUG=True
    SECRET_KEY=your-secret-key-here
    ```

3. Запустите приложение с помощью Docker Compose:

    ```bash
    docker-compose up --build
    ```

4. Проверьте работоспособность:

    - API будет доступно по адресу: <http://localhost:8000>
    - Swagger UI: <http://localhost:8000/docs>
    - База данных PostgreSQL: localhost:5432

5. Для остановки приложения:

    ```bash
    docker-compose down
    ```

### Локальная разработка

1. Создайте и активируйте виртуальное окружение:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # для Linux/MacOS
    .venv\Scripts\activate     # для Windows
    ```

2. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

3. Создайте файл .env с настройками подключения к БД:

    ```bash
    DATABASE_URL=sqlite:///./severstal.db
    ENVIRONMENT=development
    DEBUG=True
    SECRET_KEY=your-secret-key-here 
    ```

4. Примените миграции:

    ```bash
    alembic upgrade head
    ```

5. Запустите приложение:

    ```bash
    uvicorn app.main:app --reload
    ```

## API Endpoints

### Рулоны (Coils)

#### Добавление нового рулона

`POST /api/v1/coils/`

Создает новый рулон на складе.

**Тело запроса:**

```json
{
    "length": 10.5,    // Длина рулона в метрах (>0)
    "weight": 1000.0   // Вес рулона в килограммах (>0)
}
```

**Успешный ответ (200):**

```json
{
    "id": 1,
    "length": 10.5,
    "weight": 1000.0,
    "added_at": "2025-03-13T18:33:53.746598+00:00",
    "removed_at": null,
    "updated_at": null
}
```

#### Удаление рулона

`DELETE /api/v1/coils/{coil_id}`

Помечает рулон как удаленный (soft delete).

**Параметры пути:**

- `coil_id` (integer) - ID рулона

**Успешный ответ (200):**

```json
{
    "message": "Coil removed successfully",
    "coil_id": 1,
    "removed_at": "2025-03-13T18:35:53.746598+00:00"
}
```

#### Получение списка рулонов

`GET /api/v1/coils/`

Возвращает список рулонов с возможностью фильтрации.

**Параметры запроса:**

- `id_range` (array[integer], опционально) - Диапазон ID рулонов (например: `?id_range=1,10`)
- `weight_range` (array[float], опционально) - Диапазон веса (например: `?weight_range=900,1100`)
- `length_range` (array[float], опционально) - Диапазон длины (например: `?length_range=9,11`)
- `added_at_range` (array[datetime], опционально) - Диапазон дат добавления
- `removed_at_range` (array[datetime], опционально) - Диапазон дат удаления

**Успешный ответ (200):**

```json
{
    "items": [
        {
            "id": 1,
            "length": 10.5,
            "weight": 1000.0,
            "added_at": "2025-03-13T18:33:53.746598+00:00",
            "removed_at": null,
            "updated_at": null
        },
        // ...
    ],
    "total": 1
}
```

#### Получение статистики по рулонам

`POST /api/v1/coils/statistics/`

Возвращает статистику по рулонам за указанный период.

**Тело запроса:**

```json
{
    "date_range": {
        "start": "2025-03-01T00:00:00Z",  // Начало периода
        "end": "2025-03-14T00:00:00Z"     // Конец периода
    }
}
```

**Успешный ответ (200):**

```json
{
    "period": {
        "start": "2025-03-01T00:00:00Z",
        "end": "2025-03-14T00:00:00Z"
    },
    "total_coils": 10,           // Общее количество рулонов
    "active_coils": 8,           // Количество активных рулонов
    "removed_coils": 2,          // Количество удаленных рулонов
    "total_weight": 10000.0,     // Общий вес всех рулонов
    "total_length": 105.0,       // Общая длина всех рулонов
    "average_weight": 1000.0,    // Средний вес рулона
    "average_length": 10.5       // Средняя длина рулона
}
```

### Коды ошибок

- `400 Bad Request` - Некорректные параметры запроса
- `404 Not Found` - Рулон не найден
- `422 Unprocessable Entity` - Ошибка валидации данных
- `500 Internal Server Error` - Внутренняя ошибка сервера

### Формат даты и времени

Все даты и время передаются в формате ISO 8601 с указанием временной зоны (UTC).
Пример: `2025-03-13T18:33:53.746598+00:00`

### Swagger UI

Интерактивная документация API доступна по адресу: <http://localhost:8000/docs>

## Тестирование

Для запуска тестов выполните:

```bash
pytest
```

## Линтеры и типизация

Проект проверяется следующими инструментами:

- mypy (проверка типов)
- flake8 (стиль кода)
- black (форматирование)
- isort (сортировка импортов)

Для запуска проверок:

```bash
mypy .
flake8 .
black .
isort .
```

## Структура проекта

- `app/` - Основной код приложения
  - `api/` - API эндпоинты
  - `core/` - Ядро приложения (конфигурация, подключение к БД)
  - `domain/` - Доменные модели
  - `repositories/` - Репозитории для работы с данными
  - `schemas/` - Pydantic модели для валидации данных
- `migrations/` - Миграции Alembic
- `tests/` - Тесты
- `docker-compose.yml` - Конфигурация Docker Compose
- `Dockerfile` - Инструкции для сборки Docker образа
