import requests
from bs4 import BeautifulSoup
import time
import schedule
import os
import time
import telegram
from configs import config
import asyncio
from flows.techcrunch_generate import create_video_with_data
from utils.cleanup import cleanup
from social_publicators.youtube import upload_video_to_youtube

# Конфигурация
FETCH_INTERVAL = 3600  # Интервал проверки в секундах
NUM_ARTICLES = 5    # Количество получаемых статей
STORAGE_FILE = "./data/storages/techcrunch_posts.txt"
VIDEO_DIRECTORY = "./"  # Путь к директории с видео
SPECIFIC_VIDEO_FILENAME = "output.mp4"

# Настройки Telegram бота
TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN  # Замените на токен вашего бота
TELEGRAM_CHAT_ID = config.TELEGRAM_CHAT_ID   # Замените на ID чата, куда отправлять видео

def fetch_posts(num):
    url = "https://techcrunch.com/latest"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch TechCrunch posts")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    posts = soup.find_all("li", class_="wp-block-post")  # Ищем все посты

    news_data = []
    for post in posts[:num]:  # Ограничиваемся запрошенным количеством постов
        # Извлекаем заголовок
        title_tag = post.find("a", class_="loop-card__title-link")
        if not title_tag:
            continue  # Пропускаем пост, если заголовок не найден
        title = title_tag.get_text(strip=True)
        link = title_tag["href"]

        # Переходим по ссылке, чтобы получить контент поста
        post_response = requests.get(link, headers=headers)
        if post_response.status_code != 200:
            print(f"Failed to fetch post content for {title}")
            continue

        post_soup = BeautifulSoup(post_response.content, "html.parser")
        content_tags = post_soup.find("div", class_="entry-content")
        if not content_tags:
            continue

        # Извлекаем текстовый контент
        content = " ".join(p.get_text(strip=True) for p in content_tags.find_all("p"))

        news_data.append({
            "title": title,
            "content": content,
            "link": link
        })

    return news_data

def store_previous_posts(posts):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        for post in posts:
            f.write(f"{post['title']}\n")

def load_previous_posts():
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        return []

async def send_message_to_telegram(message):
    """Отправляет текстовое сообщение в Telegram чат."""
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print(f"Сообщение отправлено в Telegram: {message[:50]}...")
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")

async def send_video_to_telegram(video_path):
    """Отправляет видеофайл в Telegram чат."""
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        with open(video_path, 'rb') as video_file:
            await bot.send_video(chat_id=TELEGRAM_CHAT_ID, video=video_file)
        print(f"Видео успешно отправлено в Telegram: {os.path.basename(video_path)}")
    except Exception as e:
        print(f"Ошибка при отправке видео в Telegram: {e}")

async def process_new_articles(new_posts):
    print("Обнаружены новые статьи:")
    for post in new_posts:
        print(f"- {post['title']}")

    tech_content = await create_video_with_data(new_posts)
    post_data = [tech_content['video_description'], tech_content['hashtags']]

    # Получаем список видеофайлов из директории
    specific_video_path = os.path.join(VIDEO_DIRECTORY, SPECIFIC_VIDEO_FILENAME)

    if os.path.exists(specific_video_path):
        await send_video_to_telegram(specific_video_path)
        for message in post_data:
            await send_message_to_telegram(message)
            time.sleep(1)

    upload_video_to_youtube('output.mp4', "Tech news " + tech_content['hashtags'], tech_content['video_description'])
    cleanup('./')

async def fetch_and_compare():
    print("Fetching new articles...")
    new_posts_data = fetch_posts(NUM_ARTICLES)
    if not new_posts_data:
        return

    new_posts_titles = [post['title'] for post in new_posts_data]
    previous_posts_titles = load_previous_posts()

    if new_posts_titles and new_posts_titles != previous_posts_titles:
        print("Новые статьи отличаются от предыдущих.")
        await process_new_articles(new_posts_data)
        store_previous_posts(new_posts_data)
    else:
        print("Новых статей не обнаружено или они не отличаются от предыдущих.")

def run_scheduler():
    async def async_wrapper():
        await fetch_and_compare()

    schedule.every(FETCH_INTERVAL).seconds.do(lambda: asyncio.run(async_wrapper()))

    while True:
        schedule.run_pending()
        time.sleep(1)