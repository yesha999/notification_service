## Сервис уведомлений

*Проект реализует сервис управления рассылками API администрирования и получения статистики.*

Использованные инструменты:

*Python3.10, Django4.1.3 (+DRF), Postgresql, Celery (+Redis)*

Приложение можно организовать локально, для этого нужно:

#### 1) *Создать файл .docker_env, в нем прописать что-то вроде:*

DEBUG=TRUE

DATABASE_URL=postgres://postgres:password@postgres:5432/notification_service

TOKEN=Bearer
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDAwMzY3NDksImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6IkB5YXNoYXllc2hhIn0.HruBeJ8piBKyXrAuO6kWNnGYcVJaYlsfTLDDjcTX-pU

SECRET_KEY='django-insecure-7k595kjux6640w&=p*6+qa_#pc_69nobs+yp7%_irnqx&7-=$-'

DB_ENGINE=django.db.backends.postgresql_psycopg2

DB_NAME=notification_service

DB_USER=postgres

DB_PASSWORD=password

DB_HOST=postgres

DB_PORT=5432

#### 2) *docker-compose up --build*

Запустится 5 контейнеров:

*Редис, Celery worker, API, Postgresql, Применятся миграции.*

### Дополнительные штуки:

1 - Написаны тесты

2 - Подготовлен docker-compose

3 - Сделана подробная документация Swagger по каждому методу (/docs)

4 - Мы посылаем запрос на удаленный сервер, ждем 60 секунд (в зависимости от надежности сервера можно уменьшить), и в
случае любой неудачи поставим отправку сообщения в конец очереди через 2 часа, так до тех пор, пока наступит дата
окончания рассылки.

5 - Реализована дополнительная бизнес-логика: Добавлено поле "временной интервал" в сущность "Mailing", в которое можно
задать промежуток времени, в котором клиентам можно отправлять сообщения с учётом их локального времени. Если локальное
время не входит в указанный интервал, задача откладывается до начала интервала.

При создании рассылки Дату и время начала и окончания рассылки необходимо указывать по времени нулевого меридиана (UTC).

Мои контакты:
*tg@yashayesha, whatsapp +79081905426, e-mail: scrolltrip@mail.ru*
