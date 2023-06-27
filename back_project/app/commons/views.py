from django.shortcuts import render
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from streamings.models import Streaming
from posts.models import Post, Hashtag
from django.db.models import Q
from users.serializers import UserPublicationSerializer
from streamings.serializers import StreamingInLiveSerializer
from posts.serializers import PublicationMinSerializer, HashTagSerializer
import boto3
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.conf import settings


class CommonsViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser, MultiPartParser, FormParser,)

    @action(methods=['get'], detail=False, url_path="search", url_name="search")
    def search(self, request):
        search = request.query_params.get("search", None)
        print(search)
        users_list = []
        posts_list = []
        streamings_list = []
        hashtags_list = []

        if search.startswith('#'):
            hashtags = Hashtag.objects.filter(Q(name__icontains=search)
                                              )[:15]
            if hashtags:
                hashtags_list = HashTagSerializer(hashtags, many=True)
                hashtags_list = hashtags_list.data

        else:
            users = User.objects.filter(
                Q(username__icontains=search) |
                Q(name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search) |
                Q(bio__icontains=search)
            ).exclude(rol=3, profile_type=0)[:15]

            users_list = []
            if users:
                users_list = UserPublicationSerializer(users, many=True)
                users_list = users_list.data
            else:
                if search.find('@') == 0:
                    search_two = search.split("@")
                    users = User.objects.filter(username__icontains=search_two[1]).exclude(rol=3, profile_type=0)[:15]
                    if users:
                        users_list = UserPublicationSerializer(users, many=True)
                        users_list = users_list.data

            streamings = Streaming.objects.filter(
                name__icontains=search
            )[:15]
            streamings_list = []
            if streamings:
                streamings_list = StreamingInLiveSerializer(streamings, many=True, context={'request': request})
                streamings_list = streamings_list.data

            posts = Post.objects.filter(
                Q(description__icontains=search) |
                Q(name__icontains=search)
            )[:15]
            posts_list = []
            if posts:
                posts_list = PublicationMinSerializer(posts, many=True)
                posts_list = posts_list.data

        count = len(users_list) + len(streamings_list) + len(posts_list) + len(hashtags_list)
        return Response(
            {'users': users_list, 'streamings': streamings_list, 'posts': posts_list, 'hashtags': hashtags_list,
             'count': count}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path="search-user", url_name="search-user")
    def search_user(self, request):
        search = request.query_params.get("search", None)
        users = User.objects.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search),
            rol__in=[2, 3, 4]
        )[:15]

        users_list = []
        if users:
            users_list = UserPublicationSerializer(users, many=True)
            users_list = users_list.data

        return Response({'users': users_list}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path="file-upload", url_name="search-user")
    def file_upload(self, request):
        try:
            # client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)
            up_file = request.FILES['file']
            name = request.data.get('name')
            s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            s3_client.upload_fileobj(up_file, settings.AWS_STORAGE_BUCKET_NAME, 'media/' + name,
                                     ExtraArgs={'ACL': 'public-read'})
            return Response({'name': name}, status=status.HTTP_200_OK)
        except FileNotFoundError:
            print("Archivo no encontrado")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)
