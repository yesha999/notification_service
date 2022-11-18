import pytz as pytz
from django.core.validators import RegexValidator
from django.db import models

from django.utils import timezone

MOBILE_OPERATORS = ((900, 900), (901, 901), (902, 902), (903, 903), (904, 904), (905, 905), (906, 906), (908, 908),
                    (909, 909), (910, 910), (911, 911), (912, 912), (913, 913), (914, 914), (915, 915), (916, 916),
                    (917, 917), (918, 918), (919, 919), (920, 920), (921, 921), (922, 922), (923, 923), (924, 924),
                    (925, 925), (926, 926), (927, 927), (928, 928), (929, 929), (930, 930), (931, 931), (932, 932),
                    (933, 933), (934, 934), (936, 936), (937, 937), (938, 938), (939, 939), (941, 941), (950, 950),
                    (951, 951), (952, 952), (953, 953), (954, 954), (955, 955), (956, 956), (958, 958), (960, 960),
                    (961, 961), (962, 962), (963, 963), (964, 964), (965, 965), (966, 966), (967, 967), (968, 968),
                    (969, 969), (970, 970), (971, 971), (977, 977), (978, 978), (980, 980), (981, 981), (982, 982),
                    (983, 983), (984, 984), (985, 985), (986, 986), (987, 987), (988, 988), (989, 989), (991, 991),
                    (992, 992), (993, 993), (994, 994), (995, 995), (996, 996), (997, 997), (999, 999))


class DatesModelMixin(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(verbose_name="Дата создания")
    updated = models.DateTimeField(verbose_name="Дата последнего обновления")

    def save(self, *args, **kwargs):
        if not self.id:  # Когда объект только создается, у него еще нет id
            self.created = timezone.now()  # проставляем дату создания
        self.updated = timezone.now()  # проставляем дату обновления
        return super().save(*args, **kwargs)


class MobileOperatorChoices(models.Model):
    code = models.IntegerField(verbose_name="Коды мобильных операторов", primary_key=True)

    def __str__(self):
        return f"({self.code})"


class Mailing(DatesModelMixin):
    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    start = models.DateTimeField(verbose_name="Дата и время запуска рассылки")
    end = models.DateTimeField(verbose_name="Дата и время окончания рассылки")
    message_text = models.TextField(verbose_name="Текст сообщения для доставки клиенту", null=False)
    operator_filter = models.ManyToManyField(MobileOperatorChoices, verbose_name="Фильтр клиентов по коду оператора",
                                             null=True, blank=True, default=None)
    # В ТЗ не совсем так, но на мой взгляд, так должно быть лучше
    tag_filter = models.CharField(verbose_name="Фильтр клиентов по тегу", max_length=100, null=True, blank=True,
                                  default=None)


class Client(DatesModelMixin):
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    phoneRegex = RegexValidator(regex=r"^7\d{10}$")

    phone = models.BigIntegerField(validators=[phoneRegex], verbose_name="Номер телефона", unique=True, null=False)
    mobile_operator = models.IntegerField(verbose_name="Код мобильного оператора", choices=MOBILE_OPERATORS)
    tag = models.CharField(verbose_name="Тег (произвольная метка)", max_length=30)
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default='UTC')


class Message(models.Model):
    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    class Status(models.IntegerChoices):
        not_sent = 0, "Не отправлено"
        sent = 1, "Отправлено"

    message_sent_date = models.DateTimeField(verbose_name="Дата и время отправки сообщения")
    status = models.PositiveSmallIntegerField(verbose_name="Статус отправки", choices=Status.choices,
                                              default=Status.not_sent)
    mailing = models.ForeignKey(
        Mailing,
        verbose_name="Рассылка",
        on_delete=models.PROTECT,
        related_name="messages")

    client = models.ForeignKey(
        Client,
        verbose_name="Клиент",
        on_delete=models.PROTECT,
        related_name="messages"
    )
