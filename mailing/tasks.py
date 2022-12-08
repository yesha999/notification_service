import datetime

import pytz
import requests
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from mailing.models import Message, Client
from notification_service.settings import env


@shared_task
def send_message(message_id: int, client: dict, data: dict, end_date: str):
    """
    Если дата окончания рассылки не наступила, отправляем сообщение,
    изменяем статус на "отправлено" в базе данных
    """
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ")
    if datetime.datetime.now() < end_date:
        client_timezone = Client.objects.filter(pk=client.get("id")).values("timezone").first()
        local_time_now = datetime.datetime.now(tz=pytz.timezone(client_timezone["timezone"])).time()
        time_interval_start = datetime.datetime.strptime(data.get("time_interval_start"), "%H:%M:%S").time()
        time_interval_end = datetime.datetime.strptime(data.get("time_interval_end"), "%H:%M:%S").time()

        if time_interval_start <= local_time_now <= time_interval_end:
            request = requests.post(f"https://probe.fbrq.cloud/v1/send/{message_id}",
                                    json={"id": message_id, "phone": client.get("phone"),
                                          "text": data.get("message_text")},
                                    headers={"Authorization": env('TOKEN')}, timeout=60)
            if request.status_code == 200:
                with transaction.atomic():
                    Message.objects.select_for_update().filter(pk=message_id).update(status=Message.Status.sent)
            else:
                send_message.apply_async(args=(message_id, client, data, end_date), countdown=7200)
        elif local_time_now < time_interval_start:  # Если время еще не наступило
            date_time_start = datetime.datetime.combine(datetime.date.today(), time_interval_start)
            date_time_local = datetime.datetime.combine(datetime.date.today(), local_time_now)
            date_time_difference = date_time_start - date_time_local
            send_message.apply_async(args=(message_id, client, data, end_date),
                                     countdown=date_time_difference.total_seconds() + 60)
            # Минуту добавим на всякий случай :)
        else:  # Если текущее время больше чем время окончания рассылки
            # дождемся конца суток и посчитаем сколько до начала рассылки
            time_end_of_day = datetime.datetime.strptime("23:59:59", "%H:%M:%S").time()
            time_start_of_day = datetime.datetime.strptime("00:00:00", "%H:%M:%S").time()

            date_time_end_of_day = datetime.datetime.combine(datetime.date.today(), time_end_of_day)
            date_time_start_of_day = datetime.datetime.combine(datetime.date.today(), time_start_of_day)

            date_time_start = datetime.datetime.combine(datetime.date.today(), time_interval_start)
            date_time_local = datetime.datetime.combine(datetime.date.today(), local_time_now)

            date_time_difference1 = date_time_end_of_day - date_time_local
            date_time_difference2 = date_time_start - date_time_start_of_day
            total_countdown = date_time_difference1.total_seconds() + date_time_difference2.total_seconds() + 120
            send_message.apply_async(args=(message_id, client, data, end_date),
                                     countdown=total_countdown)
            # Тут добавим 2 минуты, потому что из-за неуказания секунд может пролететь


@shared_task
def prepare_mailing(data: dict, end_date: str):
    """
    Подготавливается рассылка, определяются клиенты, создаются сообщения в базе данных,
    передаются к отправке
    """
    clients = Client.objects.all()
    if data.get("operator_filter"):
        clients = clients.filter(mobile_operator__in=data["operator_filter"])
    if data.get("tag_filter"):
        clients = clients.filter(tag=data["tag_filter"])

    for client in clients.values('id', 'phone'):
        message = Message.objects.create(message_sent_date=timezone.now(),
                                         mailing_id=data.get('id'),
                                         client_id=client.get('id'))
        send_message.delay(message.id, client, data, end_date)
