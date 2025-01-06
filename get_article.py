import requests
import xml.etree.ElementTree as ET
import os
from configs import config

def get_existing_links():
    """Читает уже сохранённые ссылки из файла."""
    if os.path.exists(config.DOWNLOADED_LINKS_FILE):
        with open(config.DOWNLOADED_LINKS_FILE, "r") as f:
            return set(line.strip() for line in f.readlines())
    return set()

def save_link(link):
    """Сохраняет новую ссылку в файл."""
    with open(config.DOWNLOADED_LINKS_FILE, "a") as f:
        f.write(link + "\n")

def fetch_arxiv_articles(start=0, max_results=5):
    """Запрашивает статьи из категории cs.AI начиная с указанного индекса."""
    search_query = config.ARTICLE_SEARCH_QUERY
    url = f"http://export.arxiv.org/api/query?search_query={search_query}&start={start}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

    response = requests.get(url)
    articles = []
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            link = entry.find("{http://www.w3.org/2005/Atom}id").text
            pdf_link = link.replace("abs", "pdf")
            articles.append({"pdf_link": pdf_link})
    else:
        print(f"Failed to fetch data from arXiv API. Status code: {response.status_code}")
    return articles

def download_pdf(pdf_link):
    """Скачивает PDF файл по указанной ссылке."""
    response = requests.get(pdf_link)
    if response.status_code == 200:
        with open(config.PDF_FILE_NAME, "wb") as f:
            f.write(response.content)
        print(f"PDF файл успешно скачан: {config.PDF_FILE_NAME}")
    else:
        print(f"Не удалось скачать PDF файл. Статус: {response.status_code}")

def get_article_for_content():
    existing_links = get_existing_links()
    start = 0
    max_results = 5

    while True:
        articles = fetch_arxiv_articles(start=start, max_results=max_results)
        print(articles)
        filtered_articles = [article for article in articles if article["pdf_link"] not in existing_links]

        if not filtered_articles:
            start += max_results
            continue

        pdf_link = filtered_articles[0]["pdf_link"]
        download_pdf(pdf_link)
        save_link(pdf_link)
        break