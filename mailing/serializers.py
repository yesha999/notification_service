from rest_framework import serializers

from mailing.models import Client, Mailing


class ClientCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        phone = validated_data.get("phone")
        mobile_operator = int(str(phone)[1:4])  # Автоматически определяем оператора
        validated_data["mobile_operator"] = mobile_operator
        return super().create(validated_data)

    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "mobile_operator")


class ClientSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        phone = validated_data.get("phone")
        if phone:
            mobile_operator = int(str(phone)[1:4])
            validated_data["mobile_operator"] = mobile_operator
        return super().update(instance, validated_data)

    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "mobile_operator")


class MailingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")


class MailingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = "__all__"


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")
