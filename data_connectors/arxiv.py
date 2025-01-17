import requests
import xml.etree.ElementTree as ET
import os
from configs import config
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

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
            title = entry.find("{http://www.w3.org/2005/Atom}title").text
            summary = entry.find("{http://www.w3.org/2005/Atom}summary").text
            link = entry.find("{http://www.w3.org/2005/Atom}id").text
            pdf_link = link.replace("abs", "pdf")
            articles.append({"title": title, "summary": summary, "pdf_link": pdf_link})
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

def get_interesting(article_list):
    model = ChatOpenAI(model=config.GPT_MODEL, api_key=config.OPENAI_API, temperature=0.7, max_tokens=3000)

    class Response(BaseModel):
        article_title: str = Field(description="the title of chosen article")
        article_link: str = Field(description="the link of chosen article")

    parser = JsonOutputParser(pydantic_object=Response)
    system_template = """
                Role: You are the professional science popular blogger you know all about how to pick viral topics.
                Context: You creating the shorts video for youtube shorts, instagram reels, tiktok. You receive the list of articles "{article_list}".
                Task: Choose what the topic from the list will be the most interesting and viral for the video.
                \n{format_instructions}\n
    """

    prompt = PromptTemplate(
                template=system_template,
                input_variables=["article_list"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    result = chain.invoke({
        "article_list": article_list,
    })

    return result
    

def get_article():
    existing_links = get_existing_links()
    start = 0
    max_results = 5

    while True:
        articles = fetch_arxiv_articles(start=start, max_results=max_results)
        filtered_articles = [article for article in articles if article["pdf_link"] not in existing_links]

        if not filtered_articles:
            start += max_results
            continue

        pdf_link = filtered_articles[0]["pdf_link"]
        download_pdf(pdf_link)
        save_link(pdf_link)
        break