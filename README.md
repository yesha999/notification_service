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

### Выполнены следующие дополнительные задания:

1 - Написаны тесты (не на все возможные варианты событий, т.к. ограничено время)

3 - Подготовлен docker-compose 

5 - Сделана подробная документация Swagger по каждому методу (/docs)

9 - Мы посылаем запрос на удаленный сервер, ждем 60 секунд (в зависимости от надежности сервера можно уменьшить), и в
случае любой неудачи поставим отправку сообщения в конец очереди через 2 часа, так до тех пор, пока наступит дата
окончания рассылки.

При создании рассылки необходимо писать время по нулевому меридиану (UTC).

Мои контакты:
*tg@yashayesha, whatsapp +79081905426, e-mail: scrolltrip@mail.ru*
