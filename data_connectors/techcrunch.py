import requests
from bs4 import BeautifulSoup

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
    for post in posts[:num]:  # Ограничиваемся 10 постами
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
