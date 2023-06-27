from rest_framework import serializers

from clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("id", "name")


class ClientDefaultCoinsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["default_coins_user"]
