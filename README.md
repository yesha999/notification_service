## Сервис уведомлений

### Cервис управления рассылками API администрирования и получения статистики.

Использованные инструменты:

*Python3.10, Django4.1.3 (+DRF), Postgresql, Celery (+Redis)*

Приложение можно организовать локально, для этого нужно:

#### 1) *pip install requirements.txt*

#### 2) *Создать файл .docker_env, в нем прописать что-то вроде:*

DEBUG=TRUE

DATABASE_URL=postgres://postgres:password@postgres:5432/notification_service

TOKEN=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDAwMzY3NDksImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6IkB5YXNoYXllc2hhIn0.HruBeJ8piBKyXrAuO6kWNnGYcVJaYlsfTLDDjcTX-pU

SECRET_KEY='django-insecure-7k595kjux6640w&=p*6+qa_#pc_69nobs+yp7%_irnqx&7-=$-'

DB_ENGINE=django.db.backends.postgresql_psycopg2

DB_NAME=notification_service

DB_USER=postgres

DB_PASSWORD=password

DB_HOST=postgres

DB_PORT=5432

#### 3) *docker-compose up --build*

Запустится 5 контейнеров:

*Редис, Celery worker, API, Postgresql, Применятся миграции.*

### Сделана подробная документация Swagger по каждому методу (/docs)

При создании рассылки необходимо писать время по нулевому меридиану (UTC).

Мои контакты:
*tg@yashayesha, whatsapp +79081905426, e-mail: scrolltrip@mail.ru*
