import requests
from bs4 import BeautifulSoup
import time
import schedule
import os
import time
import telegram
from configs import config as base_config
import asyncio
from flows.base import create_video_with_data
from utils.cleanup import cleanup

TELEGRAM_BOT_TOKEN = base_config.TELEGRAM_BOT_TOKEN

def store_previous_posts(posts, config):
    with open(config["content"]["storage_path"], "w", encoding="utf-8") as f:
        for post in posts:
            f.write(f"{post['title']}\n")

def load_previous_posts(config):
    try:
        with open(config["content"]["storage_path"], "r", encoding="utf-8") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        return []

async def send_message_to_telegram(message, config):
    """Отправляет текстовое сообщение в Telegram чат."""
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        chats = config["telegram"]["chat_ids"]

        for id in chats:
            await bot.send_message(chat_id=id, text=message)
            print(f"Сообщение отправлено в Telegram: {message[:50]}...")
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")

async def send_video_to_telegram(video_path, config):
    """Отправляет видеофайл в Telegram чат."""
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        chats = config["telegram"]["chat_ids"]

        for id in chats:
            with open(video_path, 'rb') as video_file:
                await bot.send_video(chat_id=id, video=video_file)
        print(f"Видео успешно отправлено в Telegram: {os.path.basename(video_path)}")
    except Exception as e:
        print(f"Ошибка при отправке видео в Telegram: {e}")

async def process_new_articles(new_posts, config):
    print("Обнаружены новые статьи:")
    for post in new_posts:
        print(f"- {post['title']}")

    content = await create_video_with_data(new_posts, config)
    post_data = [content['video_description'], content['hashtags']]

    # Получаем список видеофайлов из директории
    specific_video_path = config["compose_config"]["output_video_name"]

    if os.path.exists(specific_video_path):
        await send_video_to_telegram(specific_video_path, config)
        for message in post_data:
            await send_message_to_telegram(message, config)
            time.sleep(1)

    upload_video_to_youtube = config["social"]["youtube"]["uploader"]
    upload_video_to_youtube(config["compose_config"]["output_video_name"], config["content"]["pre_title"] + content["hashtags"], content["video_description"], config['social']['youtube'])

    cleanup('./')

async def fetch_and_compare(config):
    print("Fetching new articles...")
    get_posts = config["content"]["fetcher"]
    num_posts = config["content"]["num_posts"]
    new_posts_data = get_posts(num_posts)

    if not new_posts_data:
        return

    new_posts_titles = [post['title'] for post in new_posts_data]
    previous_posts_titles = load_previous_posts(config)

    # Находим новые статьи, сравнивая списки заголовков
    new_articles = [title for title in new_posts_titles if title not in previous_posts_titles]

    if len(new_articles) >= num_posts:
        print(f"Обнаружено {len(new_articles)} новых статей (>= {num_posts}).")

        # Фильтруем full данные постов, чтобы остались только новые
        actual_new_posts_data = [post for post in new_posts_data if post['title'] in new_articles]
        await process_new_articles(actual_new_posts_data, config)

        # Сохраняем
        store_previous_posts(new_posts_data, config)
    else:
        print(f"Обнаружено {len(new_articles)} новых статей. Необходимо минимум {num_posts} для запуска обработки.")

def run_scheduler(config):
    async def async_wrapper(config):
        await fetch_and_compare(config)

    schedule.every(config["content"]["fetch_delay_sec"]).seconds.do(lambda: asyncio.run(async_wrapper(config)))

    while True:
        schedule.run_pending()
        time.sleep(1)