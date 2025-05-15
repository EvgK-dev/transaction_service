# 💳 transaction_service

Transaction Service — это мини-сервис на Python/Django для анализа пользовательских транзакций. Он разработан в рамках тестового задания и предоставляет REST API и веб-интерфейс для импорта, категоризации и анализа трат, с уведомлением о превышении лимитов.

---

## 🚀 Описание

### Сервис реализует следующие функции:

* Импорт транзакций — через веб-интерфейс или API.
* Категоризация — автоматическая классификация трат.
* Отслеживание лимитов — дневных и недельных.
* REST API — для получения статистики.
* Логирование — предупреждения о превышениях и ошибки.

---

## 📁 Структура проекта

```plaintext
transaction_service/
├── adminStyles/              # Стили для админки
├── api/                      # API-приложение (использует Django REST Framework)
├── logs/                     # Логи 
├── mainapp/                  # Django-приложение (веб-интерфейс)
│   ├── models.py             # Модели UserProfile и Transaction
│   ├── views.py              # Обработчики запросов
│   ├── static/mainapp/       # CSS, JS, изображения
│   └── templates/mainapp/    # HTML-шаблоны
├── media/                    # Загруженные файлы 
├── transaction_service/      # Настройки проекта (settings, urls)
├── .env                      # Переменные окружения 
├── db.sqlite3                # SQLite база (не добавлен в Git)
├── manage.py                 # Запуск Django
└── requirements.txt          # Зависимости проекта
```
---

## ⚙️ Установка и запуск

### 1. Клонировать репозиторий
git clone git@github.com:EvgK-dev/transaction_service.git

Или, если SSH не настроен:

git clone https://github.com/EvgK-dev/transaction_service.git

### 2. Перейти в каталог проекта
cd transaction_service

### 3. Создать и активировать виртуальное окружение 
Windows:  
python -m venv venv  
.\venv\Scripts\activate

Linux/macOS:  
python3 -m venv venv  
source venv/bin/activate  

### 4. Установить зависимости
pip install -r requirements.txt

### 5. Применить миграции
python manage.py migrate  
или полностью:  
python manage.py makemigrations  
python manage.py migrate

### 6. Запустить сервер разработки
python manage.py runserver

### 7. Открыть приложение
http://127.0.0.1:8000/

### 8. Открыть административную панель Django
http://127.0.0.1:8000/admin/

### 9. Создать суперпользователя (админа)
python manage.py createsuperuser  
Укажите логин, email и пароль по запросу в терминале.

---

### 🛠️ API эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST  | /api/transactions/ | Создание транзакции |
| GET   | /api/user-stats/ | Баланс и траты |
| GET   | /api/users/<id>/stats/?from=YYYY-MM-DD&to=YYYY-MM-DD | Детальная статистика |
| POST  | /api/topup/ | Пополнение / списание баланса |
| POST  | /api/clear-transactions/ | Очистка всех транзакций |

---

### 🧩 Пример запросов:
## Примечание: Все запросы требуют аутентификации пользователя
##Рекомендуется использовать веб-интерфейс для ввода и анализа данных, а также отслеживать поведение системы через логи

Создание транзакции (POST /api/transactions/): http://127.0.0.1:8000/api/transactions/  
Пополнение/списание баланса (POST /api/topup/): http://127.0.0.1:8000/api/topup/?amount=1000.00  
Очистка транзакций (POST /api/clear-transactions/): http://127.0.0.1:8000/api/clear-transactions/  
Текущая статистика (GET /api/user-stats/): http://127.0.0.1:8000/api/user-stats/  
Общая статистика трат (GET /api/spending-stats/): http://127.0.0.1:8000/api/spending-stats/?from=2024-11-01&to=2024-11-07  
Детальная статистика (GET /api/users/<id>/stats/): http://127.0.0.1:8000/api/users/1/stats/?from=2024-11-01&to=2024-11-07  

