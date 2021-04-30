from django.conf import settings
from rest_framework import serializers

from .models import Tasks, Links


class LinkListSerializer(serializers.ModelSerializer):

    download_link = serializers.SerializerMethodField('get_download_link')

    def get_download_link(self, link):
        download_link = f'http://{settings.ALLOWED_HOSTS[-1]}:8000/download-image/{link.pk}'
        return download_link

    class Meta:
            model = Links
            fields = ['id', 'link', 'download_link']


class DetailTaskSerializer(serializers.ModelSerializer):

    links = LinkListSerializer(many=True)
    download_zip = serializers.SerializerMethodField('get_download_zip')

    def get_download_zip(self, task):
        download_link = f'http://{settings.ALLOWED_HOSTS[-1]}:8000/download-zip/{task.pk}'
        return download_link

    class Meta:
        model = Tasks
        fields = ['id', 'url', 'level', 'download_zip', 'links']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Добавление новой задачи"""

    class Meta:
        model = Tasks
        fields = ['url', 'level']


