import mimetypes
import os
from wsgiref.util import FileWrapper
from zipfile import ZipFile

from django.conf import settings

from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Links, Tasks
from .serializers import TaskCreateSerializer, DetailTaskSerializer
from .task import save_images

from django.http import FileResponse, HttpResponse


class TaskCreateView(generics.CreateAPIView):
    """Создание новой задачи"""
    serializer_class = TaskCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        save_images.delay(obj.url, obj.level, obj.pk)
        serializer.data.update({'task_id': obj.pk})
        headers = self.get_success_headers(serializer.data)

        return Response({'task_id': obj.pk}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()


class DetailTaskView(generics.RetrieveAPIView):
    """Просмотр подробной информации о задаче"""
    serializer_class = DetailTaskSerializer
    queryset = Tasks.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.completed:
            return Response({'condition': 'in_process'})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ViewImageView(APIView):
    """Просмотр изображения"""
    def get(self, request, pk):
        link = get_object_or_404(Links, pk=pk)
        return FileResponse(open(f'{settings.MEDIA_ROOT}/{link.image.name}', 'rb'))


class DownloadImageView(APIView):
    """Загрузка изображения"""
    def get(self, request, pk):
        link = get_object_or_404(Links, pk=pk)
        image_name = link.image.name
        wrapper = FileWrapper(open(f'{settings.MEDIA_ROOT}/{image_name}', 'rb'))
        content_type = mimetypes.guess_type(image_name)
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Disposition'] = f"attachment; filename={image_name}"
        return response


class DownloadZipView(APIView):
    """Загрузка архива с изображениями"""
    def get(self, request, pk):
        task = get_object_or_404(Tasks, pk=pk)
        zip_name = f'{settings.MEDIA_ROOT}/{task.pk}.zip'
        if not os.path.exists(zip_name):
            for link in task.links.all():
                image_name = link.image.name
                image_path = f'{settings.MEDIA_ROOT}/{image_name}'

                with ZipFile(zip_name, 'a') as export_zip:
                    export_zip.write(image_path, image_name)

        wrapper = FileWrapper(open(zip_name, 'rb'))
        content_type = 'application/zip'
        content_disposition = f'attachment; filename={task.pk}.zip'

        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Disposition'] = content_disposition
        return response

