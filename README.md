Test task: Django (бронювання столиків)
--------------------------------------

Репозиторій: [git](https://gitlab.com/alexsukhykh/test_task_django)

Це тестове завдання: реалізувати простий JSON API для бронювання столиків у кафе.

## Вимоги

- Python 3.11+
- pip, venv
- База даних: SQLite (вбудована, налаштовано за замовчуванням)

## Швидкий старт

1. Клонувати репозиторій та перейти в директорію проєкту
2. Створити та активувати віртуальне середовище
3. Встановити залежності
4. Застосувати міграції
5. Запустити сервер

## Моделі

- `db.Table`: `id`, `name`
- `db.Booking`: `id`, `table(FK)`, `date(DateTimeField)`, `client_name`, `client_phone`


## Маршрути та API

- GET `/tables/` — повертає список усіх столиків

  Приклад відповіді:
  ```json
  {
    "tables": [
      {"id": 1, "name": "Table 1"},
      {"id": 2, "name": "Table 2"}
    ]
  }
  ```

- GET `/tables/?date=DD.MM.YYYYT HH:MM` — повертає доступні столики для вказаної дати/часу у вікні ±2 години.

  Приклад відповіді:
  ```json
  {
    "tables": [
      {"id": 2, "name": "Table 2"}
    ]
  }
  ```

- POST `/bookings/` — створення бронювання

  Очікуваний JSON:
  ```json
  {
    "client_name": "Alex",
    "client_phone": "0931234567",
    "date": "29.06.2023T20:00",
    "table": 2
  }
  ```

  Успішна відповідь (201 Created):
  ```json
  {
    "id": 1,
    "client_name": "Alex",
    "client_phone": "0931234567",
    "date": "29.06.2023T20:00",
    "table": 2
  }
  ```

  Помилки:
  - `400 Bad Request` — невалідні дані (відсутні поля, невалідний формат дати, порожні значення)
  - `404 Not Found` — столик з вказаним ID не існує
  - `409 Conflict` — столик вже заброньований у вказаному часовому вікні (±2 години)



## Реалізовані функції

✅ Пошук доступних столиків у вікні ±2 години  
✅ Створення бронювання з валідацією  
✅ Перевірка конфліктів бронювань  
✅ Повернення статусу 201 Created при успішному створенні  
✅ Тести для всіх основних сценаріїв  

## Запуск тестів

```bash
python manage.py test app
```

## Приклади запитів

```bash
# Отримати всі столики
curl -s http://127.0.0.1:8000/tables/

# Перевірити доступні столики для конкретної дати/часу
curl -s "http://127.0.0.1:8000/tables/?date=01.07.2023T20:00"

# Створити бронювання
curl -s -X POST http://127.0.0.1:8000/bookings/ \
  -H "Content-Type: application/json" \
  -d '{"client_name":"Alex","client_phone":"0931234567","date":"29.06.2023T20:00","table":2}'

# Приклад успішного створення (201 Created)
curl -v -X POST http://127.0.0.1:8000/bookings/ \
  -H "Content-Type: application/json" \
  -d '{"client_name":"Alex","client_phone":"0931234567","date":"29.06.2023T20:00","table":2}'

# Приклад конфлікту (409 Conflict) - спроба забронювати столик, який вже зайнятий
# Спочатку створюємо бронювання:
curl -s -X POST http://127.0.0.1:8000/bookings/ \
  -H "Content-Type: application/json" \
  -d '{"client_name":"First Client","client_phone":"1111111111","date":"01.07.2023T20:00","table":1}'

# Потім намагаємося створити конфліктуюче бронювання (в межах ±2 годин):
curl -s -X POST http://127.0.0.1:8000/bookings/ \
  -H "Content-Type: application/json" \
  -d '{"client_name":"Second Client","client_phone":"2222222222","date":"01.07.2023T19:30","table":1}'

# Приклад помилки валідації (400 Bad Request) - відсутнє поле
curl -s -X POST http://127.0.0.1:8000/bookings/ \
  -H "Content-Type: application/json" \
  -d '{"client_name":"Alex","date":"29.06.2023T20:00","table":2}'

# Приклад помилки (404 Not Found) - неіснуючий столик
curl -s -X POST http://127.0.0.1:8000/bookings/ \
  -H "Content-Type: application/json" \
  -d '{"client_name":"Alex","client_phone":"0931234567","date":"29.06.2023T20:00","table":999}'
```
