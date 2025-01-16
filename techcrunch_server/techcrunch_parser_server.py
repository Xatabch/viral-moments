import asyncio
import requests
from bs4 import BeautifulSoup
from configs import config
from techcrunch_content_generator import create_content

LATEST_POSTS_FILE = "latest_posts.txt"


# Load latest posts from file if it exists
def load_latest_posts():
    try:
        with open(LATEST_POSTS_FILE, "r") as file:
            return set(line.strip() for line in file)
    except FileNotFoundError:
        return set()


# Save latest posts to file
def save_latest_posts(posts):
    with open(LATEST_POSTS_FILE, "w") as file:
        for post in posts:
            file.write(post + "\n")


LATEST_POSTS = load_latest_posts()


async def fetch_latest_posts():
    url = "https://techcrunch.com/latest"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch TechCrunch posts")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    posts = soup.find_all("li", class_="wp-block-post")

    new_posts = []
    for post in posts[:10]:
        title_tag = post.find("a", class_="loop-card__title-link")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag["href"]

        if title not in LATEST_POSTS:
            LATEST_POSTS.add(title)
            # Fetch post content
            post_response = requests.get(link, headers=headers)
            if post_response.status_code != 200:
                continue
            post_soup = BeautifulSoup(post_response.content, "html.parser")
            content_tags = post_soup.find("div", class_="entry-content")
            if not content_tags:
                continue
            content = " ".join(p.get_text(strip=True) for p in content_tags.find_all("p"))
            new_posts.append({"title": title, "content": content, "link": link})

    if new_posts:
        save_latest_posts(LATEST_POSTS)

    return new_posts


async def send_telegram_notification(new_posts):
    for post in new_posts:
        message = f"New post: {post['title']}\nLink: {post['link']}"
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": config.TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")


async def send_telegram_video_content(content):
    message = f"New post text: {content['reels_text']}\nDescription: {content['video_description']}\nHashtags: {content['hashtags']}\nPrompts: {content['prompts']}"
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": config.TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")


async def post_watcher():
    while True:
        new_posts = await fetch_latest_posts()
        if new_posts:
            for post in new_posts:
                content = create_content(post)
                await send_telegram_video_content(content)
        await asyncio.sleep(3600)  # Wait for an hour before checking again
