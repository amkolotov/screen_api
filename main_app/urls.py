from django.urls import path

from .views import TaskCreateView, ViewImageView, DownloadImageView, DetailTaskView, DownloadZipView

app_name = 'main_app'

urlpatterns = [
    path('screenshot/', TaskCreateView.as_view(), name='create_task'),
    path('screenshot/<int:pk>/', ViewImageView.as_view(), name='view_image'),
    path('check/<int:pk>/', DetailTaskView.as_view(), name='check'),
    path('download-image/<int:pk>/', DownloadImageView.as_view(), name='download_image'),
    path('download-zip/<int:pk>/', DownloadZipView.as_view(), name='download_zip'),
]

