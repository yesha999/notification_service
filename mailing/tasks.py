import datetime

import requests
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from mailing.models import Message, Client
from notification_service.settings import env


@shared_task
def send_message(message_id: int, phone: str, data: dict, end_date: str):
    """
    Если дата окончания рассылки не наступила, отправляем сообщение,
    изменяем статус на "отправлено" в базе данных
    """
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ")
    if datetime.datetime.now() < end_date:
        request = requests.post(f"https://probe.fbrq.cloud/v1/send/{message_id}",
                                json={"id": message_id, "phone": phone,
                                      "text": data.get("message_text")},
                                headers={"Authorization": env('TOKEN')}, timeout=60)
        if request.status_code == 200:
            with transaction.atomic():
                Message.objects.select_for_update().filter(pk=message_id).update(status=Message.Status.sent)
        else:
            send_message.apply_async(args=(message_id, phone, data, end_date), countdown=7200)


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
        send_message.delay(message.id, client.get('phone'), data, end_date)
