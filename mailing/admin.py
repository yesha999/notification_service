from django.contrib import admin

from mailing.models import Mailing, Client, Message


class MailingAdmin(admin.ModelAdmin):
    list_display = ('start', 'end', 'message_text', 'tag_filter', 'created', 'updated')
    search_fields = ('message_text', 'operator_filter', 'tag_filter')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('phone', 'mobile_operator', 'tag', 'timezone', 'created', 'updated')
    search_fields = ('phone', 'mobile_operator', 'tag', 'timezone')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_sent_date', 'status', "mailing", "client")
    search_fields = ('message_sent_date', 'status', "mailing", "client")


admin.site.register(Mailing, MailingAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Message, MessageAdmin)
