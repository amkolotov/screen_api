import time

from screen_api import celery_app
from .models import Tasks, Links
from .services import get_level_urls, get_driver, get_screen, quit_driver


@celery_app.task
def save_images(url, level, task_pk):
    """Функция обработки основного запроса"""
    if level == 1:
        links = [url]
    else:
        links = get_level_urls(url, level)
    task = Tasks.objects.filter(pk=task_pk).first()
    for link in links:
        driver = get_driver()
        image = get_screen(driver, link, task_pk)
        Links.objects.create(task=task, link=link, image=image)
        quit_driver(driver)
        time.sleep(0.1)
    task.completed = True
    task.save()

