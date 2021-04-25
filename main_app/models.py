from django.core.validators import URLValidator
from django.db import models


class Tasks(models.Model):
    """Модель задачи на создание скриншотов сайта"""
    url = models.CharField('Адрес', max_length=256, validators=[URLValidator(schemes=['http', 'https'])])
    level = models.SmallIntegerField('Уровень вложенности', default=1)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    completed = models.BooleanField('Завершена', default=False)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.pk}: {self.url} ({self.level})'


class Links(models.Model):
    """Модель ссылки на конкретную страницу"""
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, verbose_name='Задача', related_name='links')
    link = models.CharField('Ссылка', max_length=256)
    image = models.ImageField('Скриншот', null=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task.pk}: {self.link}: {self.id}'
