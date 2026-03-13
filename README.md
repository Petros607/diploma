# Капи*bbb*ара

## 1. Клонирование репозитория

```
git clone https://github.com/Petros607/diploma.git
cd diploma
```

---

## 2. Создание виртуального окружения

```
python -m venv .venv
```

Активировать:

Mac / Linux

```
source .venv/bin/activate
```

Windows

```
.venv\Scripts\activate
```

---

## 3. Установка зависимостей

```
brew install awscli (На мак!!!)
```
```
pip install -r requirements.txt
```

---

# Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`.

---

# Настройка базы данных

Проект использует **PostgreSQL**.
Создайте базу данных:

```
createdb lecture_app
```

---

# Миграции базы данных

Проект использует **Alembic** для управления схемой БД.
Создание миграции:

```
alembic revision --autogenerate -m "initial schema"
```

Применение миграций:

```
alembic upgrade head
```

---

# Запуск сервера

```
uvicorn app.main:app --reload
```

После запуска API будет доступно по адресу:

```
[http://127.0.0.1:8000](http://127.0.0.1:8000)
```

Документация:

```
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
```

> **Начиная с версии 0.х** воркер запускается автоматически вместе с сервером. Дополнительный ручной запуск не требуется, но вы всё ещё можете стартовать его отдельно в другом терминале для разработки или отладки:

```bash
python -m app.workers.run_worker
```

---

# Запуск тестов

```
pytest -vs ./tests/0_test_parser_service.py
```

```
pytest -vs ./tests/*
```
