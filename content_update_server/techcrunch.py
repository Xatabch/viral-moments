import requests
from bs4 import BeautifulSoup
import time
import schedule
from flask import Flask

# Конфигурация
FETCH_INTERVAL = 3600  # Интервал проверки в секундах
NUM_ARTICLES = 5    # Количество получаемых статей
STORAGE_FILE = "./data/storages/techcrunch_posts.txt"

app = Flask(__name__)

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

def process_new_articles(new_posts):
    print("Обнаружены новые статьи:")
    for post in new_posts:
        print(f"- {post['title']}")
    # Здесь можно вызвать вашу функцию для обработки новых статей
    # Например: my_custom_function(new_posts)

def fetch_and_compare():
    print("Fetching new articles...")
    new_posts_data = fetch_posts(NUM_ARTICLES)
    if not new_posts_data:
        return

    new_posts_titles = [post['title'] for post in new_posts_data]
    previous_posts_titles = load_previous_posts()

    if new_posts_titles and new_posts_titles != previous_posts_titles:
        print("Новые статьи отличаются от предыдущих.")
        process_new_articles(new_posts_data)
        store_previous_posts(new_posts_data)
    else:
        print("Новых статей не обнаружено или они не отличаются от предыдущих.")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)