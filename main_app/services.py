import time
from typing import Set
from urllib.parse import urlparse, urljoin

from django.conf import settings
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


all_urls = set()
visited_urls_count = 0
visited_urls = set()


def valid_url(url: str) -> bool:
    """Проверка валидности url"""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_links(url: str, level: int) -> set:
    """Получение ссылок на странице"""
    urls = set()
    domain_name = urlparse(url).netloc
    time.sleep(0.1)
    soup = BeautifulSoup(requests.get(url, headers={'User-Agent': UserAgent().chrome}).text, 'lxml')

    for a_tag in soup.findAll('a'):
        href = a_tag.attrs.get('href')

        if href == "" or href is None:
            continue
        href = urljoin(url, href)

        parsed_href = urlparse(href)

        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if href[-1] == '/':
            href = href[:-1]
        if not valid_url(href):
            continue
        if '@' in href:
            continue

        if href in urls or href in all_urls:
            continue
        if domain_name not in href:
            continue
        if len(urlparse(href).path.strip('/').split('/')) >= level:
            continue
        all_urls.add(href)
        urls.add(href)

    return urls


def get_all_links(url: str, level: int, max_urls=990):
    """Функция, рекурсивно собирающая адреса"""
    global visited_urls_count
    if url in visited_urls:
        return
    visited_urls_count += 1
    visited_urls.add(url)
    print('visit', visited_urls_count)
    links = get_links(url, level)
    for link in links:
        if visited_urls_count > max_urls:
            break
        get_all_links(link, level, max_urls=max_urls)


def get_level_urls(url, level):
    """Функция, возвращающая адреса необходимого уровня"""
    get_all_links(url, level)
    level_urls = []
    for link in all_urls:
        if len(urlparse(link).path.strip('/').split('/')) >= level:
            continue
        level_urls.append(link)
    return level_urls


def get_driver():
    """Cоздание драйвера хром"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1600, 900)
    return driver


def quit_driver(driver):
    """Закрытие драйвера"""
    driver.quit()


def get_screen(driver, url, task_pk):
    """Создает скриншот страницы и возвращает путь до файла"""
    driver.get(url)

    element = driver.find_element_by_tag_name('body')
    height = element.size["height"]
    driver.set_window_size(1600, height)

    driver.refresh()
    filename = f'{task_pk}:{str(datetime.utcnow())}.png'
    filepath = f'{settings.MEDIA_ROOT}/{filename}'
    driver.save_screenshot(filepath)
    return filename


def save_images(url, level):
    """Функция обработки основного запроса"""
    if level == 1:
        links = [url]
    else:
        links = get_level_urls(url, level)
    driver = get_driver()
    for link in links:
        image = get_screen(driver, link, 100)
        time.sleep(0.5)
    quit_driver(driver)


if __name__ == '__main__':
    save_images('http://xn--79-6kc3bfr2e.xn--80acgfbsl1azdqr.xn--p1ai/', 2)

