import datetime

from celery import states
from celery.worker.control import revoke
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response

from mailing import tasks
from mailing.models import Client, Mailing, Message
from mailing.serializers import ClientCreateSerializer, ClientSerializer, MailingCreateSerializer, \
    MailingListSerializer, MailingSerializer


@extend_schema_view(
    post=extend_schema(
        description="Создает клиента рассылки",
        summary="Создает клиента рассылки"))
class ClientCreateView(CreateAPIView):
    model = Client
    serializer_class = ClientCreateSerializer


@extend_schema_view(
    get=extend_schema(
        description="Получает информацию о клиенте (часовой пояс, номер телефона, тэг)",
        summary="Получает клиента"),
    delete=extend_schema(
        description="Удаляет клиента из базы данных",
        summary="Удаляет клиента"),
    put=extend_schema(
        description="Изменяет параметры клиента (часовой пояс, номер телефона, тэг)",
        summary="Изменяет клиента"))
class ClientView(RetrieveUpdateDestroyAPIView):
    model = Client
    serializer_class = ClientSerializer
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        return Client.objects.all()


class MailingCreateView(CreateAPIView):
    model = Mailing
    serializer_class = MailingCreateSerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        return obj.id  # Добавим возвращение, чтобы получить id создаваемого объекта

    @extend_schema(
        description="Создаем рассылку, если рассылка создана на ненаступившую дату,"
                    " она будет произведена когда дата наступит, иначе запустится сразу же,"
                    " после окончания срока рассылки она будет немедленно прекращена",
        summary="Создание рассылки")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mailing_id = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        start = serializer.data.get("start")
        end = serializer.data.get("end")
        start_date = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
        end_date = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
        if start_date > end_date:
            try:
                raise ValidationError("Ошибка! Время начала рассылки позже, чем время ее окончания")
            except ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        time_interval_start = datetime.datetime.strptime(
            serializer.data.get("time_interval_start"), "%H:%M:%S").time()
        time_interval_end = datetime.datetime.strptime(
            serializer.data.get("time_interval_end"), "%H:%M:%S").time()
        if time_interval_start > time_interval_end:
            try:
                raise ValidationError("Ошибка! Задан некорректный временной интервал рассылки")
            except ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        if start_date <= datetime.datetime.now():
            tasks.prepare_mailing.delay(serializer.data, end)  # Здесь мы не указываем id задачи,
            # потому что рассылка будет запущена сразу же, ее нельзя будет изменить
        else:
            tasks.prepare_mailing.apply_async(args=(serializer.data, end), eta=start_date, task_id=str(mailing_id))
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return Mailing.objects.all()


class MailingListView(ListAPIView):
    model = Mailing
    serializer_class = MailingListSerializer

    @extend_schema(
        description="Статистика по рассылкам, сколько писем доставлено, сколько не доставлено",
        summary="Статистика по рассылкам")
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = MailingListSerializer(queryset, many=True)
        response_list = serializer.data
        not_sent_count = Message.objects.filter(status=Message.Status.not_sent).count()
        sent_count = Message.objects.filter(status=Message.Status.sent).count()
        for response in response_list:
            response["not_sent_messages_count"] = not_sent_count
            response["sent_messages_count"] = sent_count
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Mailing.objects.all()


class MailingDetailView(RetrieveUpdateDestroyAPIView):
    model = Mailing
    serializer_class = MailingSerializer
    http_method_names = ["get", "put", "delete"]

    @extend_schema(
        description="Статистика одной рассылки, информация по каждому сообщению рассылки",
        summary="Статистика одной рассылки")
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        not_sent_count = Message.objects.filter(mailing_id=data["id"], status=Message.Status.not_sent).count()
        sent_count = Message.objects.filter(mailing_id=data["id"], status=Message.Status.sent).count()
        data["not_sent_messages_count"] = not_sent_count
        data["sent_messages_count"] = sent_count

        messages = Message.objects.filter(mailing_id=data["id"]).order_by('status').values()
        data["messages_statistic"] = messages
        return Response(data)

    @extend_schema(
        description="Изменяет рассылку (текст, даты, фильтры), если рассылка еще не была отправлена, отменяет"
                    "задачу на старую рассылку и запускает измененную, так же как создание новой",
        summary="Изменяет рассылку")
    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        # После выполнения обновления, если задача еще не запущена, изменим ее.
        try:
            revoke(state=states.PENDING, task_id=str(serializer.data["id"]))
            start = serializer.data.get("start")
            end = serializer.data.get("end")
            start_date = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
            end_date = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
            if start_date > end_date:
                try:
                    raise ValidationError("Ошибка! Время начала рассылки позже, чем время ее окончания")
                except ValidationError as e:
                    return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            if start_date <= datetime.datetime.now():
                tasks.prepare_mailing.delay(serializer.data, end)  # Здесь мы не указываем id задачи,
                # потому что рассылка будет запущена сразу же, ее нельзя будет изменить
            else:
                tasks.prepare_mailing.apply_async(args=(serializer.data, end), eta=start_date,
                                                  task_id=serializer.data["id"])
            return Response(serializer.data)
        except TypeError as e:
            return Response("Ошибка! Рассылка уже запущена или не была создана", status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Удаляет рассылку, но если рассылка уже отправлена, задача отменена не будет",
        summary="Удаляет рассылку")
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.perform_destroy(instance)
        try:
            revoke(state=states.PENDING, task_id=str(serializer.data["id"]))
            return Response(data="Рассылка удалена и не будет произведена", status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(data="Рассылка удалена из базы, но сообщения уже отправлены",
                            status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return Mailing.objects.all()
