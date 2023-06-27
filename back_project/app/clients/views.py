from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from clients.models import Client
from clients.serializers import ClientSerializer, ClientDefaultCoinsSerializer
from init_project.paginations import StandardResultsSetPagination


class ClientViewSet(ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = ClientSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser,)

    def get_queryset(self):
        return Client.objects.all()

    # @action(methods=['get'], detail=True, url_path="get-default-coins-user", url_name="get-default-coins-user",
    #         serializer_class=ClientDefaultCoinsSerializer)
    @action(methods=['get'], detail=False, url_path="get-default-coins-user", url_name="get-default-coins-user")
    def get_default_coins_user(self, request):
        client = request.client
        serializer = ClientDefaultCoinsSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path="set-default-coins-user", url_name="set-default-coins-user")
    def set_default_coins_user(self, request):
        coins = request.data.get('coins', 0)
        client = request.client
        client.default_coins_user = coins
        client.save()
        return Response("Monedas iniciales actualizadas", status=status.HTTP_200_OK)
